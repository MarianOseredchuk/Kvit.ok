"""Application factory and initialization."""
import logging
from flask import Flask, jsonify
from flask_login import LoginManager

import config
from models import db
from routes.auth import auth_bp
from routes.events import events_bp
from routes.admin import admin_bp
from routes.pages import pages_bp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
    app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
    
    # Initialize extensions
    db.init_app(app)
    
    # Setup login manager
    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 errors."""
        return jsonify({'success': False, 'message': 'Ресурс не знайдено'}), 404

    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors."""
        logger.error(f"Server error: {str(e)}")
        return jsonify({'success': False, 'message': 'Внутрішня помилка сервера'}), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
