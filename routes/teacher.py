# flask 
from flask import render_template,request, flash, redirect, url_for,Blueprint,Response
from flask_login import login_required
from core.models import Teacher, Schedule
from flask_login import current_user
from datetime import datetime
from io import BytesIO

#pour pdf
from reportlab.lib.pagesizes import letter,landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, time,date

#pour sql
from sqlalchemy.orm import joinedload
# PDF setup with smaller margins
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER

# Create a Blueprint named 'teacher'
teacher_bp = Blueprint('teacher', __name__)

# Routes pour les enseignants
@teacher_bp.route('/dashboard')
@login_required
def teacher_dashboard():
    # Commentaire: Tableau de bord des enseignants
    if current_user.role != 'teacher':
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('auth.login'))
    
    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        flash('Enseignant non trouvé.', 'error')
        return redirect(url_for('auth.login'))

    # Fetch schedules for the current teacher with eager loading
    from sqlalchemy.orm import joinedload
    schedules = Schedule.query.filter_by(teacher_id=teacher.id).options(
        joinedload(Schedule.group),
        joinedload(Schedule.course),
        joinedload(Schedule.room),
        joinedload(Schedule.program)  # Added to preload the program relationship
    ).all()

    # Precompute schedules for each day and time slot
    time_slots = [
        ('08:30', '10:30'),
        ('10:40', '12:40'),
        ('13:00', '15:00'),
        ('15:10', '17:10'),
        ('17:20', '19:20')
    ]
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

    # Initialize a dictionary to hold schedules for each day and slot
    schedule_grid = {day: {i: [] for i in range(len(time_slots))} for day in days}

    # Populate the grid by checking which slots each schedule overlaps
    for schedule in schedules:
        schedule_start = schedule.start_time.strftime('%H:%M')
        schedule_end = schedule.end_time.strftime('%H:%M')
        day = schedule.day

        if day in days:
            for slot_idx, (slot_start, slot_end) in enumerate(time_slots):
                # Check if the schedule overlaps with this time slot
                if schedule_start <= slot_end and schedule_end >= slot_start:
                    schedule_grid[day][slot_idx].append(schedule)

    return render_template('/teacher/dashboard.html', schedule_grid=schedule_grid, days=days, time_slots=time_slots, teacher=teacher)


@teacher_bp.route('/export/schedule/pdf')
@login_required
def export_teacher_schedule_pdf():
    if current_user.role != 'teacher':
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('login'))

    # Get teacher information
    teacher = current_user.teacher
    if not teacher:
        flash('Profil enseignant non trouvé.', 'error')
        return redirect(url_for('index'))

    # Get teacher's schedules
    schedules = Schedule.query.filter_by(teacher_id=teacher.id).all()

    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    elements = []
    styles = getSampleStyleSheet()

    # Teacher information header
    teacher_info = [
        f"Enseignant: {teacher.first_name} {teacher.last_name}",
        f"Type: {teacher.type}",
        f"Heures max/semaine: {teacher.max_hours}"
    ]

    for info in teacher_info:
        elements.append(Paragraph(info, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Title
    title = Paragraph(f"<b>Emploi du Temps - {teacher.first_name} {teacher.last_name}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Define days and time slots (match your template)
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    time_slots = [
        ("08:30", "10:30"),
        ("10:40", "12:40"),
        ("13:00", "15:00"),
        ("15:10", "17:10"),
        ("17:20", "19:20")
    ]

    # Prepare table data
    data = [["Jour/Horaire"] + [f"{start}-{end}" for start, end in time_slots]]

    for day in days:
        row = [day]
        for start, end in time_slots:
            # Find matching schedules
            matching = [s for s in schedules 
                       if s.day == day 
                       and s.start_time.strftime('%H:%M') <= start
                       and s.end_time.strftime('%H:%M') >= end]

            if matching:
                s = matching[0]
                cell_content = [
                    f"<b>{s.course.name}</b> ({s.course.type})",
                    f"Filière: {s.program.name}",
                    f"Groupe: {s.group.name if s.group else 'Tous'}",
                    f"Salle: {s.room.name}"
                ]
                row.append(Paragraph("<br/>".join(cell_content), styles['Normal']))
            else:
                row.append("")
        data.append(row)

    # Create table with styling
    table = Table(data, colWidths=[80] + [120]*len(time_slots), repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))

    elements.append(table)
    
    # Add total hours calculation
    total_hours = sum(
        (datetime.combine(datetime.today(), s.end_time) - 
         datetime.combine(datetime.today(), s.start_time)).seconds / 3600
        for s in schedules
    )
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Total heures/semaine: {total_hours:.1f}h</b>", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return Response(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename=emploi_du_temps_{teacher.last_name}.pdf'
        }
    )
