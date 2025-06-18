# routes/admin.py
from flask import current_app, jsonify, render_template, request, flash, redirect, url_for, Blueprint, Response
from flask_login import login_required, current_user
from core.models import Department, Program, Teacher, Room, Course, Schedule, StudentGroup, User, db
from datetime import date, datetime, timedelta
from core.extensions import db, login_manager
from core.utils import send_email
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape 
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from patterns.decorators import role_required, role_required_api
from patterns.repositories import UserRepository
from patterns.factories import UserFactory

# Create a Blueprint named 'admin'
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@role_required('admin')
def admin_dashboard():
    """Tableau de bord administrateur."""
    departments_count = Department.query.count()
    teachers_count = Teacher.query.count()
    rooms_count = Room.query.count()
    schedules_count = Schedule.query.count()
    recent_schedules = Schedule.query.order_by(Schedule.created_at.desc()).limit(5).all()

    teachers = Teacher.query.all()
    teacher_labels = [f"{t.first_name} {t.last_name}" for t in teachers]
    teacher_hours = []
    for teacher in teachers:
        total_hours = 0
        for schedule in teacher.schedules:
            duration = (datetime.combine(datetime.today(), schedule.end_time) -
                    datetime.combine(datetime.today(), schedule.start_time)).seconds / 3600
            total_hours += duration
        teacher_hours.append(round(total_hours, 2))

    return render_template('admin/dashboard.html',
                            departments_count=departments_count,
                            teachers_count=teachers_count,
                            rooms_count=rooms_count,
                            schedules_count=schedules_count,
                            recent_schedules=recent_schedules,
                            teacher_labels=teacher_labels,
                            teacher_hours=teacher_hours)

@admin_bp.route('/departments', methods=['GET', 'POST'])
@role_required('admin')
def manage_departments():
    """Gestion des départements."""
    if request.method == 'POST':
        if request.form.get('_method') == 'POST':
            name = request.form['name']
            description = request.form['description']
            
            if Department.query.filter_by(name=name).first():
                flash('Un département avec ce nom existe déjà.', 'error')
                return redirect(url_for('admin.manage_departments'))
            
            department = Department(name=name, description=description)
            db.session.add(department)
            db.session.commit()
            flash('Département créé avec succès !', 'success')
            return redirect(url_for('admin.manage_departments'))
        
        elif request.form.get('_method') == 'PUT':
            department_id = request.form['department_id']
            name = request.form['name']
            description = request.form['description']
            
            department = Department.query.get_or_404(department_id)
            if Department.query.filter_by(name=name).filter(Department.id != department_id).first():
                flash('Un autre département avec ce nom existe déjà.', 'error')
                return redirect(url_for('admin.manage_departments'))
            
            department.name = name
            department.description = description
            db.session.commit()
            flash('Département modifié avec succès !', 'success')
            return redirect(url_for('admin.manage_departments'))
    
    departments = Department.query.all()
    return render_template('admin/departments.html', departments=departments)

@admin_bp.route('/departments/delete/<int:department_id>', methods=['POST'])
@role_required('admin')
def delete_department(department_id):
    """Suppression d'un département."""
    department = Department.query.get_or_404(department_id)
    
    if department.programs:
        flash('Impossible de supprimer ce département car il est associé à des filières.', 'error')
        return redirect(url_for('admin.manage_departments'))
    
    db.session.delete(department)
    db.session.commit()
    flash('Département supprimé avec succès !', 'success')
    return redirect(url_for('admin.manage_departments'))

@admin_bp.route('/programs', methods=['GET', 'POST'])
@role_required('admin')
def manage_programs():
    """Gestion des filières."""
    if request.method == 'POST':
        if request.form.get('_method') == 'POST':
            name = request.form['name']
            department_id = request.form['department']
            duration = request.form['duration']
            year = request.form['year']
            
            if Program.query.filter_by(name=name, department_id=department_id).first():
                flash('Une filière avec ce nom existe déjà dans ce département.', 'error')
                return redirect(url_for('admin.manage_programs'))
            
            program = Program(name=name, department_id=department_id, duration=duration, year=year)
            db.session.add(program)
            db.session.commit()
            flash('Filière ajoutée avec succès !', 'success')
            return redirect(url_for('admin.manage_programs'))
        
        elif request.form.get('_method') == 'PUT':
            program_id = request.form['program_id']
            name = request.form['name']
            department_id = request.form['department']
            duration = request.form['duration']
            year = request.form['year']
            
            program = Program.query.get_or_404(program_id)
            if Program.query.filter_by(name=name, department_id=department_id).filter(Program.id != program_id).first():
                flash('Une autre filière avec ce nom existe déjà dans ce département.', 'error')
                return redirect(url_for('admin.manage_programs'))
            
            program.name = name
            program.department_id = department_id
            program.duration = duration
            program.year = year
            db.session.commit()
            flash('Filière modifiée avec succès !', 'success')
            return redirect(url_for('admin.manage_programs'))
    
    departments = Department.query.all()
    programs = Program.query.all()
    return render_template('admin/programs.html', departments=departments, programs=programs)

@admin_bp.route('/programs/delete/<int:program_id>', methods=['POST'])
@role_required('admin')
def delete_program(program_id):
    """Suppression d'une filière."""
    program = Program.query.get_or_404(program_id)
    
    if program.courses or program.student_groups:
        flash('Impossible de supprimer cette filière car elle est associée à des cours ou groupes.', 'error')
        return redirect(url_for('admin.manage_programs'))
    
    db.session.delete(program)
    db.session.commit()
    flash('Filière supprimée avec succès !', 'success')
    return redirect(url_for('admin.manage_programs'))

@admin_bp.route('/teachers', methods=['GET', 'POST'])
@role_required('admin')
def manage_teachers():
    """Gestion des enseignants."""
    user_repo = UserRepository()
    if request.method == 'POST':
        send_email_flag = request.form.get('send_email') == 'true'
        
        if request.form.get('_method') == 'POST':  # CREATE TEACHER
            try:
                username = request.form.get('username')
                email = request.form.get('email')
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')
                password = request.form.get('password')
                teacher_type = request.form.get('type', 'Permanent')
                max_hours = request.form.get('max_hours', 20, type=int)

                if not all([username, email, password, first_name, last_name]):
                    flash('Tous les champs sont obligatoires !', 'error')
                    return redirect(url_for('admin.manage_teachers'))

                if user_repo.get_by_username(username):
                    flash('Ce nom d\'utilisateur existe déjà !', 'error')
                    return redirect(url_for('admin.manage_teachers'))

                if user_repo.get_by_email(email):
                    flash('Cet email est déjà utilisé !', 'error')
                    return redirect(url_for('admin.manage_teachers'))

                user, teacher = UserFactory.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role='teacher',
                    first_name=first_name,
                    last_name=last_name,
                    teacher_type=teacher_type,
                    max_hours=max_hours
                )
                user_repo.add(user)
                if teacher:
                    db.session.add(teacher)
                db.session.commit()

                if send_email_flag:
                    send_teacher_account_email(email, username, password, first_name, last_name)
                    flash('Enseignant ajouté et email envoyé avec succès !', 'success')
                else:
                    flash('Enseignant ajouté avec succès !', 'success')

            except Exception as e:
                db.session.rollback()
                flash(f'Erreur lors de la création : {str(e)}', 'error')
                return redirect(url_for('admin.manage_teachers'))

            return redirect(url_for('admin.manage_teachers'))
        
        elif request.form.get('_method') == 'PUT':  # UPDATE TEACHER
            try:
                teacher_id = request.form.get('teacher_id')
                teacher = Teacher.query.get_or_404(teacher_id)
                user = user_repo.get_by_id(teacher.user_id)

                new_username = request.form.get('username')
                new_email = request.form.get('email')
                new_first_name = request.form.get('first_name')
                new_last_name = request.form.get('last_name')
                new_password = request.form.get('password')
                new_type = request.form.get('type')
                new_max_hours = request.form.get('max_hours', type=int)

                if user_repo.get_by_username(new_username) and new_username != user.username:
                    flash('Ce nom d\'utilisateur est déjà pris !', 'error')
                    return redirect(url_for('admin.manage_teachers'))

                if user_repo.get_by_email(new_email) and new_email != user.email:
                    flash('Cet email est déjà utilisé !', 'error')
                    return redirect(url_for('admin.manage_teachers'))

                user.username = new_username
                user.email = new_email
                if new_password:
                    user.set_password(new_password)
                
                teacher.first_name = new_first_name
                teacher.last_name = new_last_name
                teacher.type = new_type
                teacher.max_hours = new_max_hours
                db.session.commit()

                if send_email_flag and new_password:
                    send_teacher_update_email(new_email, new_username, new_password, new_first_name, new_last_name)
                    flash('Enseignant modifié et email envoyé avec succès !', 'success')
                else:
                    flash('Enseignant modifié avec succès !', 'success')

            except Exception as e:
                db.session.rollback()
                flash(f'Erreur lors de la modification : {str(e)}', 'error')
            
            return redirect(url_for('admin.manage_teachers'))
    
    teachers = Teacher.query.all()
    return render_template('admin/teachers.html', teachers=teachers)

def send_teacher_account_email(email, username, password, first_name, last_name):
    """Send email for new teacher account."""
    subject = "Votre compte enseignant a été créé"
    body = f"""
    Bonjour {first_name} {last_name},
    
    Votre compte enseignant a été créé avec les informations suivantes :
    
    Identifiant: {username}
    Mot de passe: {password}
    Email: {email}
    
    Vous pouvez vous connecter à l'adresse: {url_for('auth.login', _external=True)}
    
    Cordialement,
    L'administration
    """
    send_email(subject, [email], body)

def send_teacher_update_email(email, username, password, first_name, last_name):
    """Send email for updated teacher account."""
    subject = "Votre compte enseignant a été mis à jour"
    body = f"""
    Bonjour {first_name} {last_name},
    
    Votre compte enseignant a été mis à jour avec les informations suivantes :
    
    Identifiant: {username}
    Nouveau mot de passe: {password}
    Email: {email}
    
    Vous pouvez vous connecter à l'adresse: {url_for('auth.login', _external=True)}
    
    Cordialement,
    L'administration
    """
    send_email(subject, [email], body)

@admin_bp.route('/teachers/delete/<int:teacher_id>', methods=['POST'])
@role_required('admin')
def delete_teacher(teacher_id):
    """Suppression d'un enseignant."""
    teacher = Teacher.query.get_or_404(teacher_id)
    
    if teacher.courses or teacher.schedules:
        flash('Impossible de supprimer cet enseignant car il est associé à des cours ou horaires.', 'error')
        return redirect(url_for('admin.manage_teachers'))
    
    user = teacher.user
    db.session.delete(teacher)
    db.session.delete(user)
    db.session.commit()
    flash('Enseignant supprimé avec succès !', 'success')
    return redirect(url_for('admin.manage_teachers'))

@admin_bp.route('/rooms', methods=['GET', 'POST'])
@role_required('admin')
def manage_rooms():
    """Gestion des salles."""
    if request.method == 'POST':
        if request.form.get('_method') == 'POST':
            name = request.form['name']
            capacity = request.form['capacity']
            room_type = request.form['type']
            
            if Room.query.filter_by(name=name).first():
                flash('Une salle avec ce nom existe déjà.', 'error')
                return redirect(url_for('admin.manage_rooms'))
            
            room = Room(name=name, capacity=capacity, type=room_type)
            db.session.add(room)
            db.session.commit()
            flash('Salle ajoutée avec succès !', 'success')
            return redirect(url_for('admin.manage_rooms'))
        
        elif request.form.get('_method') == 'PUT':
            room_id = request.form['room_id']
            name = request.form['name']
            capacity = request.form['capacity']
            room_type = request.form['type']
            
            room = Room.query.get_or_404(room_id)
            if Room.query.filter_by(name=name).filter(Room.id != room_id).first():
                flash('Une autre salle avec ce nom existe déjà.', 'error')
                return redirect(url_for('admin.manage_rooms'))
            
            room.name = name
            room.capacity = capacity
            room.type = room_type
            db.session.commit()
            flash('Salle modifiée avec succès !', 'success')
            return redirect(url_for('admin.manage_rooms'))
    
    rooms = Room.query.all()
    return render_template('admin/rooms.html', rooms=rooms)

@admin_bp.route('/rooms/delete/<int:room_id>', methods=['POST'])
@role_required('admin')
def delete_room(room_id):
    """Suppression d'une salle."""
    room = Room.query.get_or_404(room_id)
    
    if room.schedules:
        flash('Impossible de supprimer cette salle car elle est associée à des horaires.', 'error')
        return redirect(url_for('admin.manage_rooms'))
    
    db.session.delete(room)
    db.session.commit()
    flash('Salle supprimée avec succès !', 'success')
    return redirect(url_for('admin.manage_rooms'))

@admin_bp.route('/courses', methods=['GET', 'POST'])
@role_required('admin')
def manage_courses():
    """Gestion des cours."""
    if request.method == 'POST':
        if request.form.get('_method') == 'POST':
            name = request.form['name']
            code = request.form['code']
            course_type = request.form['type']
            duration = request.form['duration']
            program_id = request.form['program']
            teacher_id = request.form['teacher']
            
            if Course.query.filter_by(code=code).first():
                flash('Un cours avec ce code existe déjà.', 'error')
                return redirect(url_for('admin.manage_courses'))
            
            course = Course(
                name=name,
                code=code,
                type=course_type,
                duration=duration,
                program_id=program_id,
                teacher_id=teacher_id
            )
            db.session.add(course)
            db.session.commit()
            flash('Cours ajouté avec succès !', 'success')
            return redirect(url_for('admin.manage_courses'))
        
        elif request.form.get('_method') == 'PUT':
            course_id = request.form['course_id']
            name = request.form['name']
            code = request.form['code']
            course_type = request.form['type']
            duration = request.form['duration']
            program_id = request.form['program']
            teacher_id = request.form['teacher']
            
            course = Course.query.get_or_404(course_id)
            if Course.query.filter_by(code=code).filter(Course.id != course_id).first():
                flash('Un autre cours avec ce code existe déjà.', 'error')
                return redirect(url_for('admin.manage_courses'))
            
            course.name = name
            course.code = code
            course.type = course_type
            course.duration = duration
            course.program_id = program_id
            course.teacher_id = teacher_id
            db.session.commit()
            flash('Cours modifié avec succès !', 'success')
            return redirect(url_for('admin.manage_courses'))
    
    programs = Program.query.all()
    teachers = Teacher.query.all()
    courses = Course.query.all()
    return render_template('admin/courses.html', programs=programs, teachers=teachers, courses=courses)

@admin_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
@role_required('admin')
def delete_course(course_id):
    """Suppression d'un cours."""
    course = Course.query.get_or_404(course_id)
    
    if course.schedules:
        flash('Impossible de supprimer ce cours car il est associé à des horaires.', 'error')
        return redirect(url_for('admin.manage_courses'))
    
    db.session.delete(course)
    db.session.commit()
    flash('Cours supprimé avec succès !', 'success')
    return redirect(url_for('admin.manage_courses'))

def check_schedule_conflicts(room_id, teacher_id, group_id, day, start_time_obj, end_time_obj, exclude_schedule_id=None):
    """Check for scheduling conflicts with existing schedules."""
    conflicts = {
        'room': [],
        'teacher': [],
        'group': []
    }

    conflict_query = Schedule.query.filter(
        Schedule.day == day,
        (
            (Schedule.start_time <= start_time_obj) & (Schedule.end_time > start_time_obj) |
            (Schedule.start_time < end_time_obj) & (Schedule.end_time >= end_time_obj) |
            (Schedule.start_time >= start_time_obj) & (Schedule.end_time <= end_time_obj)
        )
    )

    if exclude_schedule_id:
        conflict_query = conflict_query.filter(Schedule.id != exclude_schedule_id)

    room_conflicts = conflict_query.filter(Schedule.room_id == room_id).all()
    for conflict in room_conflicts:
        conflicts['room'].append({
            'type': 'room',
            'course': conflict.course.name,
            'teacher': f"{conflict.teacher.first_name} {conflict.teacher.last_name}",
            'group': conflict.group.name if conflict.group else 'Tous',
            'time': f"{conflict.start_time.strftime('%H:%M')}-{conflict.end_time.strftime('%H:%M')}"
        })

    teacher_conflicts = conflict_query.filter(Schedule.teacher_id == teacher_id).all()
    for conflict in teacher_conflicts:
        conflicts['teacher'].append({
            'type': 'teacher',
            'course': conflict.course.name,
            'room': conflict.room.name,
            'group': conflict.group.name if conflict.group else 'Tous',
            'time': f"{conflict.start_time.strftime('%H:%M')}-{conflict.end_time.strftime('%H:%M')}"
        })

    if group_id:
        group_conflicts = conflict_query.filter(Schedule.group_id == group_id).all()
        for conflict in group_conflicts:
            conflicts['group'].append({
                'type': 'group',
                'course': conflict.course.name,
                'teacher': f"{conflict.teacher.first_name} {conflict.teacher.last_name}",
                'room': conflict.room.name,
                'time': f"{conflict.start_time.strftime('%H:%M')}-{conflict.end_time.strftime('%H:%M')}"
            })

    return conflicts

@admin_bp.route('/schedule', methods=['GET', 'POST'])
@role_required('admin')
def manage_schedule():
    """Gestion des emplois du temps."""
    programs = Program.query.all()
    courses = Course.query.all()
    teachers = Teacher.query.all()
    groups = StudentGroup.query.all()
    rooms = Room.query.all()

    if request.method == 'POST':
        program_id = request.form.get('program')
        year = request.form.get('year')
        course_id = request.form.get('course')
        teacher_id = request.form.get('teacher')
        group_id = request.form.get('group')
        room_id = request.form.get('room')
        day = request.form.get('day')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        if group_id == 'all':
            group_id = None

        try:
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        except ValueError:
            flash('Format de temps invalide. Utilisez HH:MM.', 'error')
            return redirect(url_for('admin.manage_schedule'))

        if start_time_obj >= end_time_obj:
            flash("L'heure de fin doit être après l'heure de début.", 'error')
            return redirect(url_for('admin.manage_schedule'))

        method = request.form.get('_method', 'POST')
        schedule_id = request.form.get('schedule_id', type=int) if method == 'PUT' else None

        conflicts = check_schedule_conflicts(
            room_id=room_id,
            teacher_id=teacher_id,
            group_id=group_id,
            day=day,
            start_time_obj=start_time_obj,
            end_time_obj=end_time_obj,
            exclude_schedule_id=schedule_id
        )

        if any(conflicts.values()):
            conflict_messages = []
            for conflict_type, conflict_list in conflicts.items():
                for conflict in conflict_list:
                    if conflict_type == 'room':
                        msg = (f"Conflit de salle: {conflict['course']} avec {conflict['teacher']} "
                               f"(Groupe: {conflict['group']}) à {conflict['time']}")
                    elif conflict_type == 'teacher':
                        msg = (f"Enseignant occupé: {conflict['course']} en {conflict['room']} "
                               f"(Groupe: {conflict['group']}) à {conflict['time']}")
                    elif conflict_type == 'group':
                        msg = (f"Groupe occupé: {conflict['course']} avec {conflict['teacher']} "
                               f"en {conflict['room']} à {conflict['time']}")
                    conflict_messages.append(msg)

            flash('Conflits détectés: ' + ' | '.join(conflict_messages), 'error')
            return redirect(url_for('admin.manage_schedule'))

        if method == 'POST':
            try:
                schedule = Schedule(
                    program_id=program_id,
                    year=year,
                    course_id=course_id,
                    teacher_id=teacher_id,
                    group_id=group_id,
                    room_id=room_id,
                    day=day,
                    start_time=start_time_obj,
                    end_time=end_time_obj
                )
                db.session.add(schedule)
                db.session.commit()
                flash('Créneau ajouté avec succès.', 'success')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error adding schedule: {str(e)}")
                flash('Erreur lors de l\'ajout du créneau.', 'error')

        elif method == 'PUT':
            try:
                schedule = Schedule.query.get_or_404(schedule_id)
                schedule.program_id = program_id
                schedule.year = year
                schedule.course_id = course_id
                schedule.teacher_id = teacher_id
                schedule.group_id = group_id
                schedule.room_id = room_id
                schedule.day = day
                schedule.start_time = start_time_obj
                schedule.end_time = end_time_obj
                db.session.commit()
                flash('Créneau modifié avec succès.', 'success')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error updating schedule: {str(e)}")
                flash('Erreur lors de la modification du créneau.', 'error')

        return redirect(url_for('admin.manage_schedule'))

    program_id = request.args.get('program_id')
    year = request.args.get('year')

    query = Schedule.query.options(
        joinedload(Schedule.program),
        joinedload(Schedule.course),
        joinedload(Schedule.teacher),
        joinedload(Schedule.group),
        joinedload(Schedule.room)
    )

    if program_id:
        query = query.filter_by(program_id=program_id)
    if year:
        query = query.filter_by(year=year)

    schedules = query.order_by(Schedule.day, Schedule.start_time).all()

    for schedule in schedules:
        conflicts = check_schedule_conflicts(
            room_id=schedule.room_id,
            teacher_id=schedule.teacher_id,
            group_id=schedule.group_id,
            day=schedule.day,
            start_time_obj=schedule.start_time,
            end_time_obj=schedule.end_time,
            exclude_schedule_id=schedule.id
        )
        schedule.has_conflict = any(conflicts.values())

    time_slots = [
        ('08:30', '10:30'),
        ('10:40', '12:40'),
        ('13:00', '15:00'),
        ('15:10', '17:10'),
        ('17:20', '19:20')
    ]
    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]

    schedule_grid = {day: {i: [] for i in range(len(time_slots))} for day in days}

    for schedule in schedules:
        schedule_start = schedule.start_time.strftime('%H:%M')
        schedule_end = schedule.end_time.strftime('%H:%M')
        day = schedule.day

        if day in days:
            for slot_idx, (slot_start, slot_end) in enumerate(time_slots):
                if schedule_start <= slot_end and schedule_end >= slot_start:
                    schedule_grid[day][slot_idx].append(schedule)

    return render_template(
        'admin/schedule.html',
        programs=programs,
        courses=courses,
        teachers=teachers,
        groups=groups,
        rooms=rooms,
        schedule_grid=schedule_grid,
        days=days,
        time_slots=time_slots,
        selected_program_id=program_id,
        selected_year=year
    )

@admin_bp.route('/schedule/delete/<int:schedule_id>', methods=['POST'])
@role_required('admin')
def delete_schedule(schedule_id):
    """Suppression d'un créneau."""
    schedule = Schedule.query.get_or_404(schedule_id)
    program_id = schedule.program_id
    year = schedule.year
    db.session.delete(schedule)
    db.session.commit()
    flash('Créneau supprimé avec succès !', 'success')
    return redirect(url_for('admin.manage_schedule', program_id=program_id, year=year))

@admin_bp.route('/export/schedule/pdf')
@role_required('admin')
def export_schedule_pdf():
    """Exportation de l'emploi du temps en PDF."""
    program_id = request.args.get('program_id')
    year = request.args.get('year')

    if not program_id or not year:
        flash('Veuillez sélectionner une filière et une année avant d\'exporter.', 'error')
        return redirect(url_for('admin.manage_schedule'))

    program = Program.query.get(program_id)
    if not program:
        flash('Filière non trouvée.', 'error')
        return redirect(url_for('admin.manage_schedule'))

    program_name = program.name
    year_text = f"{year}ère année" if year == '1' else f"{year}ème année"

    schedules = Schedule.query.options(
        joinedload(Schedule.group),
        joinedload(Schedule.course),
        joinedload(Schedule.teacher),
        joinedload(Schedule.room),
        joinedload(Schedule.program)
    ).filter(
        Schedule.program_id == program_id,
        Schedule.year == year
    ).order_by(
        Schedule.day,
        Schedule.start_time
    ).all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=72,
        rightMargin=72,
        topMargin=36,
        bottomMargin=36
    )
    
    elements = []
    styles = getSampleStyleSheet()
    styles['Title'].alignment = TA_CENTER
    styles['Heading1'].alignment = TA_CENTER
    
    cell_style = styles['Normal'].clone('CellStyle')
    cell_style.fontSize = 8
    cell_style.leading = 10
    cell_style.alignment = TA_CENTER
    
    title = Paragraph(f"<b>Emploi du Temps - {program_name} ({year_text})</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    time_slots = [
        ("08:30", "10:30"),
        ("10:40", "12:40"),
        ("13:00", "15:00"),
        ("15:10", "17:10"),
        ("17:20", "19:20")
    ]

    data = []
    header = ["Jour/Horaire"] + [f"{start}-{end}" for start, end in time_slots]
    data.append(header)
    
    for day in days:
        row = [day]
        for start_time_str, end_time_str in time_slots:
            matching_schedules = [
                s for s in schedules 
                if s.day == day 
                and s.start_time.strftime('%H:%M') <= start_time_str
                and s.end_time.strftime('%H:%M') >= end_time_str
            ]
            
            if matching_schedules:
                s = matching_schedules[0]
                cell_content = [
                    f"<b>{s.course.name}</b> ({s.course.type})",
                    f"Pr. {s.teacher.last_name}",
                    f"Groupe: {s.group.name if s.group else 'Tous'}",
                    f"Salle: {s.room.name}"
                ]
                cell_text = "<br/>".join(cell_content)
                row.append(Paragraph(cell_text, cell_style))
            else:
                row.append("")
        data.append(row)

    table = Table(data, 
                 colWidths=[100] + [120] * len(time_slots),
                 repeatRows=1)
    
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    doc.build(elements)
    
    buffer.seek(0)
    return Response(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename=emploi_du_temps_{program_name}_{year_text}.pdf'
        }
    )

@admin_bp.route('/teacher_chart')
@role_required_api('admin')
def teacher_chart():
    """Génération du graphique des heures par enseignant."""
    try:
        teachers = Teacher.query.options(db.joinedload(Teacher.schedules)).all()
        
        if not teachers:
            current_app.logger.info("No teachers found for chart data")
            return jsonify({'status': 'success', 'image': ''})

        labels = []
        hours = []
        
        for teacher in teachers:
            total_hours = 0.0
            schedule_count = len(teacher.schedules)
            current_app.logger.info(f"Processing teacher {teacher.first_name} {teacher.last_name} with {schedule_count} schedules")
            
            for schedule in teacher.schedules:
                try:
                    if not schedule.start_time or not schedule.end_time:
                        current_app.logger.warning(f"Schedule {schedule.id} missing start_time or end_time")
                        continue
                        
                    start = schedule.start_time
                    end = schedule.end_time
                    
                    if isinstance(start, str):
                        try:
                            start = datetime.strptime(start, '%H:%M:%S').time()
                        except ValueError as e:
                            current_app.logger.error(f"Invalid start_time format for schedule {schedule.id}: {start}, error: {str(e)}")
                            continue
                    if isinstance(end, str):
                        try:
                            end = datetime.strptime(end, '%H:%M:%S').time()
                        except ValueError as e:
                            continue
                            
                    start_dt = datetime.combine(date.today(), start)
                    end_dt = datetime.combine(date.today(), end)
                    
                    if end < start:
                        end_dt = datetime.combine(date.today() + timedelta(days=1), end)
                    
                    duration = (end_dt - start_dt).total_seconds() / 3600
                    if duration < 0:
                        current_app.logger.error(f"Negative duration for schedule {schedule.id}: start={start}, end={end}")
                        continue
                        
                    total_hours += duration
                    current_app.logger.debug(f"Schedule {schedule.id} duration: {duration:.2f} hours")
                except Exception as e:
                    current_app.logger.error(f"Error processing schedule {schedule.id}: {str(e)}")
                    continue

            labels.append(f"{teacher.first_name} {teacher.last_name}")
            hours.append(round(total_hours, 2))
            current_app.logger.info(f"Teacher {teacher.first_name} {teacher.last_name} total hours: {total_hours:.2f}")

        sorted_indices = np.argsort(hours)[::-1]
        labels = [labels[i] for i in sorted_indices]
        hours = [hours[i] for i in sorted_indices]

        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(labels))
        bars = ax.bar(x, hours, color='#1e88e5', edgecolor='black')
        
        ax.set_xlabel('Enseignants', fontsize=12)
        ax.set_ylabel('Heures', fontsize=12)
        ax.set_title('Heures par Enseignant', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.2f}h',
                    ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        buf.close()
        plt.close(fig)

        return jsonify({
            'status': 'success',
            'image': f'data:image/png;base64,{image_base64}'
        })

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in teacher_chart: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Database operation failed',
            'error': str(e)
        }), 500
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in teacher_chart: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred',
            'error': str(e)
        }), 500