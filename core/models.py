from datetime import datetime
from core.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), nullable=False)  # admin, teacher, student
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=True)  # For students
    year = db.Column(db.Integer, nullable=True)  # For students (e.g., 1, 2, 3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    program = db.relationship('Program', backref=db.backref('users', lazy=True))
    teacher = db.relationship('Teacher', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    duration = db.Column(db.Integer)  # Durée en années
    year = db.Column(db.Integer, nullable=False)  # Academic year (e.g., 1, 2, 3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    department = db.relationship('Department', backref=db.backref('programs', lazy=True))

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # Permanent, Vacataire
    max_hours = db.Column(db.Integer, default=20)  # Heures max par semaine
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudentGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    size = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    program = db.relationship('Program', backref=db.backref('student_groups', lazy=True))

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # Amphi, Salle TD, Salle TP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # Cours, TD, TP
    duration = db.Column(db.Integer, nullable=False)  # Durée en heures
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    program = db.relationship('Program', backref=db.backref('courses', lazy=True))
    teacher = db.relationship('Teacher', backref=db.backref('courses', lazy=True))

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)  # Assuming 1-3 for academic years
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    day = db.Column(db.String(10), nullable=False)  # e.g., "Lundi", "Mardi", etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey('student_group.id'), nullable=True)
    
    group = db.relationship('StudentGroup', backref=db.backref('schedules', lazy=True))
    program = db.relationship('Program', backref=db.backref('schedules', lazy=True))
    course = db.relationship('Course', backref=db.backref('schedules', lazy=True))
    teacher = db.relationship('Teacher', backref=db.backref('schedules', lazy=True))
    room = db.relationship('Room', backref=db.backref('schedules', lazy=True))