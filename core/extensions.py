# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

# Singleton Metaclass for ensuring single instances of extensions
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# Singleton-enabled instances
class DB(SQLAlchemy, metaclass=Singleton): pass
class Login(LoginManager, metaclass=Singleton): pass
class Mailer(Mail, metaclass=Singleton): pass

db = DB()
login_manager = Login()
mail = Mailer()

def init_app(app):
    """Initialize extensions with the Flask app."""
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Ensure consistent login view
    mail.init_app(app)