from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import jwt
import datetime
from functools import wraps
from dotenv import load_dotenv
import os
from marshmallow import Schema, fields, validate, ValidationError
import bcrypt

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8000", "https://btbinh2710.github.io"]}})
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'e0e55e5f584ef6555aa9bb957a4b75fb0d674e0693c54da243ee8dcbefff7258')

def get_db_connection():
    try:
        conn = sqlite3.connect('proposals.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        app.logger.error(f"Database connection error: {str(e)}")
        return None

def init_db():
    try:
        conn = get_db_connection()
        if not conn:
            return False
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                branch TEXT,
                role TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposer TEXT,
                room TEXT,
                branch TEXT,
                department TEXT,
                date TEXT,
                code TEXT,
                content TEXT,
                purpose TEXT,
                supplier TEXT,
                estimated_cost REAL,
                budget REAL,
                approved_amount REAL,
                transfer_code TEXT,
                payment_date TEXT,
                notes TEXT,
                status TEXT,
                approver TEXT,
                approval_date TEXT,
                completed TEXT,
                UNIQUE(branch, code)
            )
        ''')
        users = [
            ('admin', 'admin123', 'Admin', 'admin'),
            ('accountant', 'accountant123', 'Accountant', 'accountant'),
            ('xdv_thaodien_manager1', 'manager123', 'XDV_ThaoDien', 'manager'),
            ('xdv_thaodien_employee1', 'employee123', 'XDV_ThaoDien', 'employee'),
            # Thêm các người dùng khác nếu cần
        ]
        for user in users:
            username, password, branch, role = user
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            c.execute('INSERT OR IGNORE INTO users (username, password, branch, role) VALUES (?, ?, ?, ?)',
                      (username, hashed.decode('utf-8'), branch, role))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        app.logger.error(f"Database initialization error: {str(e)}")
        return False

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

class ProposalSchema(Schema):
    proposer = fields.Str(required=True)
    room = fields.Str(required=True)
    branch = fields.Str(required=True)
    department = fields.Str(required=True)
    date = fields.Str(required=True, validate=validate.Regexp(r'^\d{2}/\d{2}/\d{4}$|^$'))
    code = fields.Str(required=True)
    content = fields.Str(required=True)
    purpose = fields.Str(allow_none=True)
    supplier = fields.Str(required=True)
    estimated_cost = fields.Float(required=True, validate=validate.Range(min=0))
    budget = fields.Float(allow_none=True, validate=validate.Range(min=0))
    approved_amount = fields.Float(allow_none=True, validate=validate.Range(min=0))
    transfer_code = fields.Str(allow_none=True)
    payment_date = fields.Str(allow_none=True, validate=validate.Regexp(r'^\d{2}/\d{2}/\d{4}$|^$'))
    notes = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    approver = fields.Str(allow_none=True)
    approval_date = fields.Str(allow_none=True, validate=validate.Regexp(r'^\d{2}/\d{2}/\d{4}$|^$'))
    completed = fields.Str(allow_none=True)

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'message': 'Missing username or password'}), 400

        username = data.get('username')
        password = data.get('password')

        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500

        # Kiểm tra và khởi tạo bảng users nếu chưa tồn tại
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            conn.close()
            if not init_db():
                return jsonify({'message': 'Failed to initialize database'}), 500
            conn = get_db_connection()
            if not conn:
                return jsonify({'message': 'Database connection failed after initialization'}), 500

        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if not user:
            conn.close()
            return jsonify({'message': 'Invalid credentials!'}), 401

        # Kiểm tra mật khẩu
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            token = jwt.encode({
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            conn.close()
            return jsonify({
                'token': token,
                'username': user['username'],
                'branch': user['branch'],
                'role': user['role']
            })
        else:
            conn.close()
            return jsonify({'message': 'Invalid credentials!'}), 401
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

@app.route('/api/proposals', methods=['GET'])
@token_required
def get_proposals(current_user):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500

        user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
        if not user:
            conn.close()
            return jsonify({'message': 'User not found!'}), 404

        if user['role'] == 'accountant':
            proposals = conn.execute('SELECT * FROM proposals').fetchall()
        else:
            proposals = conn.execute('SELECT * FROM proposals WHERE branch = ?', (user['branch'],)).fetchall()
        conn.close()
        return jsonify([dict(row) for row in proposals])
    except Exception as e:
        app.logger.error(f"Get proposals error: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

@app.route('/api/proposals', methods=['POST'])
@token_required
def create_proposal(current_user):
    try:
        if request.headers.get('Content-Type') != 'application/json':
            return jsonify({'message': 'Content-Type must be application/json'}), 415
        data = request.get_json()
        schema = ProposalSchema()
        validated_data = schema.load(data)

        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500

        user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
        if not user:
            conn.close()
            return jsonify({'message': 'User not found!'}), 404

        if user['role'] == 'accountant':
            conn.close()
            return jsonify({'message': 'Accountants cannot create proposals!'}), 403

        validated_data['branch'] = user['branch']
        conn.execute('''
            INSERT INTO proposals (proposer, room, branch, department, date, code, content, purpose, supplier, 
            estimated_cost, budget, approved_amount, transfer_code, payment_date, notes, status, approver, approval_date, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            validated_data['proposer'], validated_data['room'], validated_data['branch'], validated_data['department'],
            validated_data['date'], validated_data['code'], validated_data['content'], validated_data['purpose'],
            validated_data['supplier'], validated_data['estimated_cost'], validated_data['budget'], 
            validated_data['approved_amount'], validated_data['transfer_code'], validated_data['payment_date'], 
            validated_data['notes'], validated_data['status'], validated_data['approver'], validated_data['approval_date'], 
            validated_data['completed']
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Proposal created successfully!'}), 201
    except ValidationError as err:
        return jsonify({'message': err.messages}), 400
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'message': 'Proposal code already exists for this branch!'}), 400
    except Exception as e:
        app.logger.error(f"Create proposal error: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

@app.route('/api/proposals/<int:id>', methods=['PUT'])
@token_required
def update_proposal(current_user, id):
    try:
        data = request.get_json()
        schema = ProposalSchema()
        validated_data = schema.load(data, partial=True)

        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500

        user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
        proposal = conn.execute('SELECT * FROM proposals WHERE id = ?', (id,)).fetchone()

        if not user:
            conn.close()
            return jsonify({'message': 'User not found!'}), 404
        if not proposal:
            conn.close()
            return jsonify({'message': 'Proposal not found!'}), 404

        if user['role'] != 'admin' and user['branch'] != proposal['branch'] and user['role'] != 'accountant':
            conn.close()
            return jsonify({'message': 'Unauthorized!'}), 403

        if user['role'] == 'accountant':
            allowed_fields = ['approved_amount', 'transfer_code', 'payment_date', 'notes', 'completed', 'status']
            validated_data = {k: v for k, v in validated_data.items() if k in allowed_fields}
        else:
            validated_data.pop('branch', None)

        query = 'UPDATE proposals SET ' + ', '.join(f'{k} = ?' for k in validated_data.keys()) + ' WHERE id = ?'
        values = list(validated_data.values()) + [id]
        conn.execute(query, values)
        conn.commit()
        conn.close()
        return jsonify({'message': 'Proposal updated successfully!'})
    except ValidationError as err:
        return jsonify({'message': err.messages}), 400
    except Exception as e:
        app.logger.error(f"Update proposal error: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

@app.route('/api/proposals/<int:id>', methods=['DELETE'])
@token_required
def delete_proposal(current_user, id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'message': 'Database connection failed'}), 500

        user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
        proposal = conn.execute('SELECT * FROM proposals WHERE id = ?', (id,)).fetchone()

        if not user:
            conn.close()
            return jsonify({'message': 'User not found!'}), 404
        if not proposal:
            conn.close()
            return jsonify({'message': 'Proposal not found!'}), 404

        if user['role'] == 'accountant':
            conn.close()
            return jsonify({'message': 'Accountants cannot delete proposals!'}), 403

        if user['role'] != 'admin' and user['branch'] != proposal['branch']:
            conn.close()
            return jsonify({'message': 'Unauthorized!'}), 403

        conn.execute('DELETE FROM proposals WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Proposal deleted successfully!'})
    except Exception as e:
        app.logger.error(f"Delete proposal error: {str(e)}")
        return jsonify({'message': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()  # Khởi tạo cơ sở dữ liệu khi chạy cục bộ
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)