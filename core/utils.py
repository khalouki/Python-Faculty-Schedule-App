from flask_mail import Message
from core.extensions import mail
from flask import current_app

def send_email(subject, recipients, body):
    msg = Message(
        subject=subject,
        recipients=recipients,
        body=body,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
