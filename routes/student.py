from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, Response
from core.extensions import db, login_manager
from core.config import Config
from flask_login import login_required, current_user
from core.models import User, Schedule, Program, StudentGroup
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime
from flask_login import current_user

# Create a Blueprint named 'student'
student_bp = Blueprint('student', __name__)

# Routes pour les étudiants
@student_bp.route('/dashboard')
@login_required
def student_dashboard():
    # Commentaire: Tableau de bord des étudiants
    if current_user.role != 'student':
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('login'))
    
    if not current_user.program_id or not current_user.year:
        flash('Veuillez spécifier votre filière et année dans votre profil.', 'error')
        return redirect(url_for('register'))
    
    
    
    program = Program.query.get(current_user.program_id)
    from sqlalchemy.orm import joinedload
    schedules = Schedule.query.filter(
        Schedule.program_id == current_user.program_id,
        Schedule.year == str(current_user.year),
        db.or_(
            Schedule.group_id == StudentGroup.id,
            Schedule.group_id.is_(None)
        )
    ).options(
        joinedload(Schedule.group),
        joinedload(Schedule.course),
        joinedload(Schedule.teacher),
        joinedload(Schedule.room)
    ).all()

    # Debug: Print schedules info
    print(f"Number of schedules: {len(schedules)}")
    for s in schedules:
        print(f"Schedule: day={s.day}, start={s.start_time}, end={s.end_time}, program_id={s.program_id}, year={s.year}, group_id={s.group_id}")

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

    return render_template('student/dashboard.html', 
                          schedule_grid=schedule_grid,
                          days=days,
                          time_slots=time_slots,
                          student_name=current_user.username, 
                          program_name=program.name if program else 'Non spécifié', 
                          year=current_user.year,
                          schedules=schedules)


@student_bp.route('/export/schedule/pdf')
@login_required
def export_student_schedule_pdf():
    if current_user.role != 'student':
        flash('Accès non autorisé.', 'error')
        return redirect(url_for('login'))

    # Get student information
    student = current_user
    program = Program.query.get(student.program_id)
    year_text = f"{student.year}ème année" if student.year != 1 else f"{student.year}ère année"

    # Get student's group and schedules
    group = StudentGroup.query.filter_by(program_id=student.program_id).first()
    schedules = Schedule.query.filter(
        Schedule.program_id == student.program_id,
        Schedule.year == str(student.year),
        db.or_(
            Schedule.group_id == StudentGroup.id,
            Schedule.group_id.is_(None)
        )
    ).all()

    # Debug: Print schedules info for PDF
    print(f"PDF - Number of schedules: {len(schedules)}")
    for s in schedules:
        print(f"PDF - Schedule: day={s.day}, start={s.start_time}, end={s.end_time}, program_id={s.program_id}, year={s.year}, group_id={s.group_id}")

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

    # Student information header
    student_info = [
        f"Filière: {program.name}",
        f"Année: {year_text}",
        f"Groupe: {group.name if group else 'Non assigné'}"
    ]

    for info in student_info:
        elements.append(Paragraph(info, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Title
    title = Paragraph(f"<b>Emploi du Temps - {program.name} ({year_text})</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Define days and time slots
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
                    f"Pr. {s.teacher.last_name}",
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
            'Content-Disposition': f'attachment; filename=emploi_du_temps.pdf'
        }
    )