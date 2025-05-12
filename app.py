from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import jwt
import bcrypt
import datetime
import sqlite3
from dotenv import load_dotenv
import os
from marshmallow import Schema, fields, validate, ValidationError
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')  # Fallback for local dev

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://btbinh2710.github.io", "https://de-xuat-ea0h.onrender.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
})

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')
handler = RotatingFileHandler('logs/app.log', maxBytes=1000000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application started')

# Custom API Error
class APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

# Marshmallow Schema for Proposal
class ProposalSchema(Schema):
    proposer = fields.Str(required=True, validate=validate.Length(min=1))
    room = fields.Str(allow_none=True)
    department = fields.Str(required=True, validate=validate.Length(min=1))
    date = fields.Str(required=True, validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$'))
    code = fields.Str(allow_none=True)
    proposal = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    purpose = fields.Str(allow_none=True)
    supplier = fields.Str(allow_none=True)
    estimated_cost = fields.Float(allow_none=True, validate=validate.Range(min=0))
    budget = fields.Float(allow_none=True, validate=validate.Range(min=0))
    approved_amount = fields.Float(allow_none=True, validate=validate.Range(min=0))
    transfer_code = fields.Str(allow_none=True)
    payment_date = fields.Str(allow_none=True, validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$|^$'))
    notes = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    approver = fields.Str(allow_none=True)
    approval_date = fields.Str(allow_none=True, validate=validate.Regexp(r'^\d{4}-\d{2}-\d{2}$|^$'))
    completed = fields.Str(allow_none=True)

proposal_schema = ProposalSchema()

# Database connection
def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

# Format proposal to ensure 'branch' is first
def format_proposal(proposal):
    return {
        'branch': proposal['branch'],
        'id': proposal['id'],
        'proposer': proposal['proposer'],
        'room': proposal['room'],
        'department': proposal['department'],
        'date': proposal['date'],
        'code': proposal['code'],
        'proposal': proposal['proposal'],
        'content': proposal['content'],
        'purpose': proposal['purpose'],
        'supplier': proposal['supplier'],
        'estimated_cost': proposal['estimated_cost'],
        'budget': proposal['budget'],
        'approved_amount': proposal['approved_amount'],
        'transfer_code': proposal['transfer_code'],
        'payment_date': proposal['payment_date'],
        'notes': proposal['notes'],
        'status': proposal['status'],
        'approver': proposal['approver'],
        'approval_date': proposal['approval_date'],
        'completed': proposal['completed']
    }

# Health check route
@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Error handlers
@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify({'message': error.message, 'status_code': error.status_code})
    response.status_code = error.status_code
    app.logger.error(f'APIError: {error.message} (Status: {error.status_code})')
    return response

@app.errorhandler(Exception)
def handle_general_error(error):
    response = jsonify({'message': 'Internal server error', 'status_code': 500})
    response.status_code = 500
    app.logger.error(f'Unexpected error: {str(error)}')
    return response

# Handle preflight requests
@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization', 'Content-Type')
    return response

# Authenticate token
def authenticate_token():
    token = request.headers.get('Authorization', '').split(' ')[1] if 'Authorization' in request.headers else None
    if not token:
        raise APIError('Token required', 401)
    try:
        user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        app.logger.info(f'Token authenticated for user: {user["username"]}')
        return user, None, None
    except Exception as e:
        app.logger.error(f'Invalid token: {str(e)}')
        raise APIError('Invalid token', 403)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        raise APIError('Username and password are required', 400)

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        app.logger.warning(f'Failed login attempt for username: {username}')
        raise APIError('Tên đăng nhập hoặc mật khẩu không đúng!', 401)

    token = jwt.encode({
        'username': user['username'],
        'role': user['role'],
        'branch': user['branch'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm='HS256')

    app.logger.info(f'Login successful for user: {username}')
    return jsonify({'token': token, 'role': user['role'], 'branch': user['branch']})

@app.route('/api/proposals', methods=['GET'])
def get_proposals():
    user, error, status = authenticate_token()
    if error:
        return error, status
    
    conn = get_db_connection()
    if user['role'] == 'admin':
        proposals = conn.execute('SELECT * FROM proposals').fetchall()
    else:
        proposals = conn.execute('SELECT * FROM proposals WHERE branch = ?', (user['branch'],)).fetchall()
    conn.close()

    app.logger.info(f'Retrieved {len(proposals)} proposals for user: {user["username"]}')
    return jsonify([format_proposal(dict(row)) for row in proposals])

@app.route('/api/proposals', methods=['POST'])
def add_proposal():
    user, error, status = authenticate_token()
    if error:
        return error, status
    if user['role'] == 'admin':
        raise APIError('Admin không thể thêm đề xuất!', 403)

    data = request.get_json()
    try:
        validated_data = proposal_schema.load(data)
    except ValidationError as err:
        raise APIError(f'Validation error: {err.messages}', 400)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO proposals (proposer, room, branch, department, date, code, proposal, content, purpose, supplier,
                              estimated_cost, budget, approved_amount, transfer_code, payment_date, notes, status,
                              approver, approval_date, completed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        validated_data.get('proposer'),
        validated_data.get('room'),
        user['branch'],
        validated_data.get('department'),
        validated_data.get('date'),
        validated_data.get('code'),
        validated_data.get('proposal'),
        validated_data.get('content'),
        validated_data.get('purpose'),
        validated_data.get('supplier'),
        validated_data.get('estimated_cost'),
        validated_data.get('budget'),
        validated_data.get('approved_amount'),
        validated_data.get('transfer_code'),
        validated_data.get('payment_date'),
        validated_data.get('notes'),
        validated_data.get('status'),
        validated_data.get('approver'),
        validated_data.get('approval_date'),
        validated_data.get('completed')
    ))
    conn.commit()
    new_id = cursor.lastrowid
    new_proposal = conn.execute('SELECT * FROM proposals WHERE id = ?', (new_id,)).fetchone()
    conn.close()

    app.logger.info(f'Created new proposal ID {new_id} by user: {user["username"]}')
    return jsonify(format_proposal(dict(new_proposal))), 201

@app.route('/api/proposals/<int:id>', methods=['PUT'])
def update_proposal(id):
    user, error, status = authenticate_token()
    if error:
        return error, status

    conn = get_db_connection()
    proposal = conn.execute('SELECT * FROM proposals WHERE id = ?', (id,)).fetchone()
    
    if not proposal:
        conn.close()
        raise APIError('Đề xuất không tồn tại!', 404)
    if user['role'] != 'admin' and proposal['branch'] != user['branch']:
        conn.close()
        raise APIError('Bạn không có quyền chỉnh sửa đề xuất này!', 403)

    data = request.get_json()
    try:
        validated_data = proposal_schema.load(data, partial=True)
    except ValidationError as err:
        conn.close()
        raise APIError(f'Validation error: {err.messages}', 400)

    update_fields = {k: v for k, v in validated_data.items() if v is not None}
    if not update_fields:
        conn.close()
        raise APIError('No fields to update', 400)

    query = 'UPDATE proposals SET ' + ', '.join(f'{k} = ?' for k in update_fields.keys()) + ' WHERE id = ?'
    values = list(update_fields.values()) + [id]
    conn.execute(query, values)
    conn.commit()

    updated_proposal = conn.execute('SELECT * FROM proposals WHERE id = ?', (id,)).fetchone()
    conn.close()

    app.logger.info(f'Updated proposal ID {id} by user: {user["username"]}')
    return jsonify(format_proposal(dict(updated_proposal)))

@app.route('/api/proposals/<int:id>', methods=['DELETE'])
def delete_proposal(id):
    user, error, status = authenticate_token()
    if error:
        return error, status

    conn = get_db_connection()
    proposal = conn.execute('SELECT * FROM proposals WHERE id = ?', (id,)).fetchone()
    
    if not proposal:
        conn.close()
        raise APIError('Đề xuất không tồn tại!', 404)
    if user['role'] != 'admin' and proposal['branch'] != user['branch']:
        conn.close()
        raise APIError('Bạn không có quyền xóa đề xuất này!', 403)

    conn.execute('DELETE FROM proposals WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    app.logger.info(f'Deleted proposal ID {id} by user: {user["username"]}')
    return '', 204

if __name__ == '__main__':
    port = int(os.getenv('PORT', 10000))  # Use PORT from environment, fallback to 10000
    app.run(host='0.0.0.0', port=port)