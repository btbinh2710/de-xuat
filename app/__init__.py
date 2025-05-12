from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
import os
from .config import Config
from .auth import auth_bp
from .proposals import proposals_bp

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Khởi tạo extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["https://btbinh2710.github.io", "https://de-xuat-ea0h.onrender.com"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Authorization", "Content-Type"]
        }
    })

    # Cấu hình logging
    if not os.path.exists('logs'):
        os.makedirs('logs')
    handler = RotatingFileHandler('logs/app.log', maxBytes=1000000, backupCount=5)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Ứng dụng khởi động')

    # Đăng ký blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(proposals_bp)

    # Health check route
    @app.route('/', methods=['GET', 'HEAD'])
    def health_check():
        app.logger.info('Yêu cầu health check')
        return jsonify({'status': 'healthy'}), 200

    @app.errorhandler(Exception)
    def handle_general_error(error):
        response = jsonify({'message': 'Lỗi server nội bộ', 'status_code': 500})
        response.status_code = 500
        app.logger.error(f'Lỗi không mong muốn: {str(error)}')
        return response

    return app