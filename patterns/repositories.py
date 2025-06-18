# repositories.py
from core.models import User
from core.extensions import db

class UserRepository:
    """Repository for User database operations."""
    def __init__(self):
        self.db_session = db.session

    def get_by_username(self, username):
        """Get user by username."""
        return self.db_session.query(User).filter_by(username=username).first()

    def get_by_email(self, email):
        """Get user by email."""
        return self.db_session.query(User).filter_by(email=email).first()

    def add(self, user):
        """Add user to session."""
        self.db_session.add(user)

    def get_by_id(self, user_id):
        """Get user by ID."""
        return self.db_session.query(User).get(user_id)