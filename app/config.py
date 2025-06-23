class Config:
    SECRET_KEY = 'your_secret_key_here'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit for uploads
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # Database configurations (if applicable)
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False