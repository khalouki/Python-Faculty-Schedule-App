# app.py
from flask import Flask, render_template
from core.config import Config
from core.extensions import db, login_manager
from datetime import datetime
from core.models import User, Department, Program, Teacher, Course, StudentGroup
from flask_login import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.teacher import teacher_bp
    from routes.student import student_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')
    app.register_blueprint(student_bp, url_prefix='/student')
    
    # Initialize database with default data
    with app.app_context():
        initialize_database()
    
    # Add cache control headers
    @app.after_request
    def add_header(response):
        if current_user.is_authenticated:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '-1'
        return response

    @app.route('/')
    def index():
        return render_template('accueil.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    return app

def initialize_database():
    db.create_all()
    
    # Create default admin user
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", email="admin@example.com", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
    
    # Create default department
    department = Department.query.filter_by(name="Informatique").first()
    if not department:
        department = Department(name="Informatique", description="Département Informatique")
        db.session.add(department)
        db.session.commit()
        print("Department created!")
    
    # Create default program
    program = Program.query.filter_by(name="Licence Informatique").first()
    if not program:
        program = Program(name="Licence Informatique", department_id=department.id, duration=3, year=1)
        db.session.add(program)
        db.session.commit()
        print("Program created!")
    
    # Create default teacher
    teacher = Teacher.query.filter_by(first_name="abdelkhalk").first()
    if not teacher:
        user = User.query.filter_by(username="abdelkhalk").first()
        if not user:
            user = User(username="abdelkhalk", email="abdelkhalk@example.com", role="teacher")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
            print("Teacher user created!")
        
        teacher = Teacher(user_id=user.id, first_name="abdelkhalk", last_name="essaid", type="Permanent")
        db.session.add(teacher)
        db.session.commit()
        print("Teacher created!")
    
    # Create default course
    course = Course.query.filter_by(name="Algorithmique").first()
    if not course:
        course = Course(name="Algorithmique", code="ALG101", type="Cours", duration=30, program_id=program.id, teacher_id=teacher.id)
        db.session.add(course)
        db.session.commit()
        print("Course created!")
    
    # Create default student groups
    group = StudentGroup.query.filter_by(name="Groupe 1").first()
    if not group:
        group = StudentGroup(name="Groupe 1", program_id=program.id, size=30)
        db.session.add(group)
        group = StudentGroup(name="Groupe 2", program_id=program.id, size=30)
        db.session.add(group)
        group = StudentGroup(name="Groupe 3", program_id=program.id, size=30)
        db.session.add(group)
        group = StudentGroup(name="Groupe 4", program_id=program.id, size=30)
        db.session.add(group)
        db.session.commit()
        print("Student groups created!")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)