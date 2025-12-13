import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)

    # Створюємо папку для завантажень, якщо її немає
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Ініціалізація розширень
    db.init_app(app)
    login_manager.init_app(app)

    # Імпорт моделей для login_manager (щоб він знав про User)
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Реєстрація Blueprint-ів (маршрутів)
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.events import events_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()

    return app