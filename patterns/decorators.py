# decorators.py
from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for,jsonify

def role_required(*roles):
    """Decorator to restrict access to specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('Accès non autorisé.', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def role_required_api(*roles):
    """Decorator for API endpoints to restrict access to specific roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                return jsonify({'status': 'error', 'message': 'Unauthorized access'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator