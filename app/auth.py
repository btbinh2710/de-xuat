from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
import bcrypt
import datetime
from .models import User, db

auth_bp = Blueprint('auth', __name__)

limiter = Limiter(key_func=get_remote_address)

@auth_bp.record
def record_params(setup_state):
    limiter.init_app(setup_state.app)

class APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

@auth_bp.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify({'message': error.message, 'status_code': error.status_code})
    response.status_code = error.status_code
    current_app.logger.error(f'APIError: {error.message} (Status: {error.status_code})')
    return response

@auth_bp.route('/api/login', methods=['POST'])
@limiter.limit("100/hour")
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise APIError('Tên đăng nhập và mật khẩu là bắt buộc', 400)

    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        current_app.logger.warning(f'Thử đăng nhập thất bại cho người dùng: {username}')
        raise APIError('Tên đăng nhập hoặc mật khẩu không đúng!', 401)

    access_token = jwt.encode({
        'username': user.username,
        'role': user.role,
        'branch': user.branch,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    refresh_token = jwt.encode({
        'username': user.username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=current_app.config['JWT_REFRESH_TOKEN_EXPIRES'])
    }, current_app.config['SECRET_KEY'], algorithm='HS256')

    current_app.logger.info(f'Đăng nhập thành công cho người dùng: {username}')
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'role': user.role,
        'branch': user.branch
    })

@auth_bp.route('/api/refresh', methods=['POST'])
@limiter.limit("100/hour")
def refresh():
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        raise APIError('Refresh token là bắt buộc', 400)

    try:
        payload = jwt.decode(refresh_token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        username = payload['username']
        user = User.query.filter_by(username=username).first()
        if not user:
            raise APIError('Người dùng không tồn tại', 404)

        access_token = jwt.encode({
            'username': user.username,
            'role': user.role,
            'branch': user.branch,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=current_app.config['JWT_ACCESS_TOKEN_EXPIRES'])
        }, current_app.config['SECRET_KEY'], algorithm='HS256')

        current_app.logger.info(f'Làm mới token thành công cho người dùng: {username}')
        return jsonify({'access_token': access_token})
    except jwt.ExpiredSignatureError:
        raise APIError('Refresh token đã hết hạn', 401)
    except jwt.InvalidTokenError:
        raise APIError('Refresh token không hợp lệ', 401)