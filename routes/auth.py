# routes/auth.py
from flask import render_template, request, flash, redirect, url_for, session, Blueprint, Response
from flask_login import login_user, logout_user, login_required
from core.models import User, Program
from core.extensions import db, login_manager
from patterns.factories import UserFactory
from patterns.repositories import UserRepository
from patterns.strategies import RedirectContext

# Create a Blueprint named 'auth'
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion des utilisateurs."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_repo = UserRepository()
        user = user_repo.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash('Connexion réussie !', 'success')
            redirect_context = RedirectContext()
            return redirect(redirect_context.get_redirect(user.role))
        else:
            flash('Identifiant ou mot de passe incorrect.', 'error')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion sécurisée pour tous les utilisateurs."""
    session.clear()  # Effacer toutes les données de session
    logout_user()  # Déconnecter l'utilisateur via Flask-Login
    flash('Vous avez été déconnecté avec succès.', 'success')
    
    # Create response with cache control headers
    response = redirect(url_for('auth.login'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription des nouveaux utilisateurs."""
    user_repo = UserRepository()
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form['role']
        program_id = request.form.get('program')  # Pour les étudiants
        year = request.form.get('year')  # Pour les étudiants
        first_name = request.form.get('first_name')  # Pour les enseignants
        last_name = request.form.get('last_name')  # Pour les enseignants
        teacher_type = request.form.get('type')  # Pour les enseignants
        max_hours = request.form.get('max_hours', 20, type=int)  # Pour les enseignants
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return redirect(url_for('auth.register'))
        
        if user_repo.get_by_username(username):
            flash('Ce nom d\'utilisateur est déjà pris.', 'error')
            return redirect(url_for('auth.register'))
        
        if user_repo.get_by_email(email):
            flash('Cet email est déjà utilisé.', 'error')
            return redirect(url_for('auth.register'))
        
        try:
            user, teacher = UserFactory.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                program_id=program_id,
                year=year,
                first_name=first_name,
                last_name=last_name,
                teacher_type=teacher_type,
                max_hours=max_hours
            )
            user_repo.add(user)
            if teacher:
                db.session.add(teacher)
            db.session.commit()
            flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('auth.register'))
    
    programs = Program.query.all()
    return render_template('auth/register.html', programs=programs)