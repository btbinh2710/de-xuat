import pytest
from app import create_app, db
from app.models import User, Proposal
import bcrypt
import jwt
import time

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

@pytest.fixture
def auth_token(app, client):
    with app.app_context():
        password = bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(username='testuser', password=password, branch='Test Branch', role='manager')
        db.session.add(user)
        db.session.commit()

    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'test123'
    })
    return response.json['access_token']

def test_create_proposal(client, auth_token):
    response = client.post('/api/proposals', json={
        'proposer': 'Nguyễn Văn A',
        'room': 'Kinh Doanh',
        'department': 'KD',
        'date': '01/05/2025',
        'proposal': 'Mua laptop',
        'content': 'Mua laptop phục vụ công việc',
        'purpose': 'Phục vụ công việc',
        'supplier': 'Công ty ABC',
        'estimated_cost': 15000000,
        'budget': 20000000,
        'transfer_code': 'XBDC-123',
        'payment_date': '03/05/2025',
        'status': 'Đang chờ duyệt',
        'approver': '',
        'approval_date': ''
    }, headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 201
    assert response.json['proposer'] == 'Nguyễn Văn A'
    assert response.json['date'] == '01/05/2025'