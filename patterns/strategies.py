# strategies.py
from abc import ABC, abstractmethod
from flask import url_for

class RedirectStrategy(ABC):
    """Abstract base class for redirection strategies."""
    @abstractmethod
    def redirect(self):
        pass

class AdminRedirect(RedirectStrategy):
    def redirect(self):
        return url_for('admin.admin_dashboard')

class TeacherRedirect(RedirectStrategy):
    def redirect(self):
        return url_for('teacher.teacher_dashboard')

class StudentRedirect(RedirectStrategy):
    def redirect(self):
        return url_for('student.student_dashboard')

class RedirectContext:
    """Context for selecting redirection strategy based on role."""
    def __init__(self):
        self.strategies = {
            'admin': AdminRedirect(),
            'teacher': TeacherRedirect(),
            'student': StudentRedirect()
        }

    def get_redirect(self, role):
        """Get redirection URL for the given role."""
        return self.strategies.get(role, StudentRedirect()).redirect()