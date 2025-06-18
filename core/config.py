class Config:
    SECRET_KEY = 'b3a8c12e45f67d8901e2b3c4567890abcdef12345fedcba9876543210abcdef'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/emploi_du_temps'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    # Email configuration
    MAIL_SERVER = 'smtp.yourprovider.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your@email.com'
    MAIL_PASSWORD = 'yourpassword'
    MAIL_DEFAULT_SENDER = 'your@email.com'
