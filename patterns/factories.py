# factories.py
from core.models import User, Teacher
from core.extensions import db

class UserFactory:
    """Factory for creating User and related objects based on role."""
    @staticmethod
    def create_user(username, email, password, role, program_id=None, year=None, first_name=None, last_name=None, teacher_type=None, max_hours=20):
        """Create a user and associated objects based on role."""
        user = User(username=username, email=email, role=role, program_id=program_id, year=year)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Get user.id without committing

        if role == 'teacher':
            if not first_name or not last_name:
                raise ValueError("First name and last name are required for teachers.")
            teacher = Teacher(
                user_id=user.id,
                first_name=first_name,
                last_name=last_name,
                type=teacher_type or 'Permanent',
                max_hours=max_hours
            )
            return user, teacher
        return user, None