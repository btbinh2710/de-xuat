import pytest
from app import create_app, db
from app.models import User
import bcrypt

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_success(client):
    # Thêm user test
    with client.application.app_context():
        password = bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(username='testuser', password=password, branch='Test Branch', role='manager')
        db.session.add(user)
        db.session.commit()

    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'test123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json
    assert response.json['role'] == 'manager'
    assert response.json['branch'] == 'Test Branch'

def test_login_invalid_credentials(client):
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'wrong'
    })
    assert response.status_code == 401
    assert response.json['message'] == 'Tên đăng nhập hoặc mật khẩu không đúng!'