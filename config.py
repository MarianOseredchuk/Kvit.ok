import os

class Config:
    SECRET_KEY = 'secret-key-123' # В реальному проекті використовуйте os.environ.get()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///kvitok.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Налаштування завантаження файлів
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}