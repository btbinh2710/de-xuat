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
        app.logger.error(f"Kết nối cơ sở dữ liệu thất bại: {str(e)}")
        return None

def init_db():
    try:
        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể khởi tạo cơ sở dữ liệu: Kết nối thất bại")
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
        ]
        for user in users:
            username, password, branch, role = user
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            c.execute('INSERT OR IGNORE INTO users (username, password, branch, role) VALUES (?, ?, ?, ?)',
                      (username, hashed.decode('utf-8'), branch, role))
        conn.commit()
        conn.close()
        app.logger.info("Khởi tạo cơ sở dữ liệu thành công")
        return True
    except Exception as e:
        app.logger.error(f"Lỗi khởi tạo cơ sở dữ liệu: {str(e)}")
        return False

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            app.logger.warning("Yêu cầu không có token")
            return jsonify({'message': 'Thiếu token xác thực!'}), 401
        try:
            token = token.split(" ")[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['username']
        except jwt.InvalidTokenError:
            app.logger.warning("Token không hợp lệ")
            return jsonify({'message': 'Token không hợp lệ!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

class ProposalSchema(Schema):
    proposer = fields.Str(required=True, validate=validate.Length(min=1))
    room = fields.Str(required=True, validate=validate.Length(min=1))
    branch = fields.Str(required=True, validate=validate.Length(min=1))
    department = fields.Str(required=True, validate=validate.Length(min=1))
    date = fields.Str(required=True, validate=validate.Regexp(r'^\d{2}/\d{2}/\d{4}$|^$'))
    code = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    purpose = fields.Str(allow_none=True)
    supplier = fields.Str(required=True, validate=validate.Length(min=1))
    estimated_cost = fields.Float(required=True, validate=validate.Range(min=0))
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
            app.logger.warning("Thiếu tên đăng nhập hoặc mật khẩu")
            return jsonify({'message': 'Thiếu tên đăng nhập hoặc mật khẩu'}), 400
        username = data.get('username')
        password = data.get('password')
        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong đăng nhập")
            return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại'}), 500
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not c.fetchone():
            conn.close()
            if not init_db():
                app.logger.error("Không thể khởi tạo cơ sở dữ liệu trong đăng nhập")
                return jsonify({'message': 'Khởi tạo cơ sở dữ liệu thất bại'}), 500
            conn = get_db_connection()
            if not conn:
                app.logger.error("Kết nối cơ sở dữ liệu thất bại sau khi khởi tạo")
                return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại sau khi khởi tạo'}), 500
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if not user:
            conn.close()
            app.logger.warning(f"Thông tin đăng nhập không hợp lệ: {username}")
            return jsonify({'message': 'Thông tin đăng nhập không hợp lệ!'}), 401
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            token = jwt.encode({
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            conn.close()
            app.logger.info(f"Đăng nhập thành công: {username}")
            return jsonify({
                'token': token,
                'username': user['username'],
                'branch': user['branch'],
                'role': user['role']
            })
        else:
            conn.close()
            app.logger.warning(f"Thông tin đăng nhập không hợp lệ: {username}")
            return jsonify({'message': 'Thông tin đăng nhập không hợp lệ!'}), 401
    except Exception as e:
        app.logger.error(f"Lỗi đăng nhập: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

@app.route('/api/proposals', methods=['GET'])
@token_required
def get_proposals(current_user):
    try:
        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong lấy danh sách đề xuất")
            return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại'}), 500
        user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
        if not user:
            conn.close()
            app.logger.warning(f"Người dùng không tồn tại: {current_user}")
            return jsonify({'message': 'Người dùng không tồn tại!'}), 404
        if user['role'] == 'accountant':
            proposals = conn.execute('SELECT * FROM proposals').fetchall()
        else:
            proposals = conn.execute('SELECT * FROM proposals WHERE branch = ?', (user['branch'],)).fetchall()
        conn.close()
        app.logger.info(f"Lấy danh sách đề xuất thành công cho người dùng: {current_user}")
        return jsonify([dict(row) for row in proposals])
    except Exception as e:
        app.logger.error(f"Lỗi lấy danh sách đề xuất: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

@app.route('/api/proposals', methods=['POST'])
@token_required
def create_proposal(current_user):
    try:
        if request.headers.get('Content-Type') != 'application/json':
            app.logger.warning("Content-Type không phải application/json")
            return jsonify({'message': 'Content-Type phải là application/json'}), 415
        data = request.get_json()
        schema = ProposalSchema()
        validated_data = schema.load(data)
        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong tạo đề xuất")
            return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại'}), 500
        user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
        if not user:
            conn.close()
            app.logger.warning(f"Người dùng không tồn tại: {current_user}")
            return jsonify({'message': 'Người dùng không tồn tại!'}), 404
        if user['role'] == 'accountant':
            conn.close()
            app.logger.warning(f"Tài khoản kế toán không được phép tạo đề xuất: {current_user}")
            return jsonify({'message': 'Tài khoản kế toán không được phép tạo đề xuất!'}), 403
        validated_data['branch'] = user['branch']
        conn.execute('''
            INSERT INTO proposals (proposer, room, branch, department, date, code, content, purpose, supplier, 
            estimated_cost, approved_amount, transfer_code, payment_date, notes, status, approver, approval_date, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            validated_data['proposer'], validated_data['room'], validated_data['branch'], validated_data['department'],
            validated_data['date'], validated_data['code'], validated_data['content'], validated_data['purpose'],
            validated_data['supplier'], validated_data['estimated_cost'], validated_data['approved_amount'], 
            validated_data['transfer_code'], validated_data['payment_date'], validated_data['notes'], 
            validated_data['status'], validated_data['approver'], validated_data['approval_date'], 
            validated_data['completed']
        ))
        conn.commit()
        conn.close()
        app.logger.info(f"Tạo đề xuất thành công bởi: {current_user}, mã: {validated_data['code']}")
        return jsonify({'message': 'Tạo đề xuất thành công!'}), 201
    except ValidationError as err:
        app.logger.warning(f"Lỗi xác thực dữ liệu đề xuất: {err.messages}")
        return jsonify({'message': f'Dữ liệu không hợp lệ: {err.messages}'}), 400
    except sqlite3.IntegrityError as e:
        conn.close()
        app.logger.warning(f"Mã đề xuất trùng lặp: {data.get('code', 'Không xác định')} cho chi nhánh {user['branch']}")
        return jsonify({'message': 'Mã đề xuất đã tồn tại cho chi nhánh này!'}), 400
    except Exception as e:
        app.logger.error(f"Lỗi tạo đề xuất: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

@app.route('/api/proposals/<int:id>', methods=['PUT'])
@token_required
def update_proposal(current_user, id):
    try:
        data = request.get_json()
        schema = ProposalSchema()
        validated_data = schema.load(data, partial=True)
        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong cập nhật đề xuất")
            return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại'}), 500
        user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
        proposal = conn.execute('SELECT * FROM proposals WHERE id = ?', (id,)).fetchone()
        if not user:
            conn.close()
            app.logger.warning(f"Người dùng không tồn tại: {current_user}")
            return jsonify({'message': 'Người dùng không tồn tại!'}), 404
        if not proposal:
            conn.close()
            app.logger.warning(f"Đề xuất không tồn tại: ID {id}")
            return jsonify({'message': 'Đề xuất không tồn tại!'}), 404
        if user['role'] != 'admin' and user['branch'] != proposal['branch'] and user['role'] != 'accountant':
            conn.close()
            app.logger.warning(f"Không có quyền cập nhật đề xuất: {current_user} trên đề xuất ID {id}")
            return jsonify({'message': 'Không có quyền truy cập!'}), 403
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
        app.logger.info(f"Cập nhật đề xuất thành công: ID {id} bởi {current_user}")
        return jsonify({'message': 'Cập nhật đề xuất thành công!'})
    except ValidationError as err:
        app.logger.warning(f"Lỗi xác thực dữ liệu cập nhật đề xuất: {err.messages}")
        return jsonify({'message': f'Dữ liệu không hợp lệ: {err.messages}'}), 400
    except Exception as e:
        app.logger.error(f"Lỗi cập nhật đề xuất: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

@app.route('/api/proposals/<int:id>', methods=['DELETE'])
@token_required
def delete_proposal(current_user, id):
    try:
        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong xóa đề xuất")
            return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại'}), 500
        user = conn.execute('SELECT * FROM users WHERE username = ?', (current_user,)).fetchone()
        proposal = conn.execute('SELECT * FROM proposals WHERE id = ?', (id,)).fetchone()
        if not user:
            conn.close()
            app.logger.warning(f"Người dùng không tồn tại: {current_user}")
            return jsonify({'message': 'Người dùng không tồn tại!'}), 404
        if not proposal:
            conn.close()
            app.logger.warning(f"Đề xuất không tồn tại: ID {id}")
            return jsonify({'message': 'Đề xuất không tồn tại!'}), 404
        if user['role'] == 'accountant':
            conn.close()
            app.logger.warning(f"Tài khoản kế toán không được phép xóa đề xuất: {current_user}")
            return jsonify({'message': 'Tài khoản kế toán không được phép xóa đề xuất!'}), 403
        if user['role'] != 'admin' and user['branch'] != proposal['branch']:
            conn.close()
            app.logger.warning(f"Không có quyền xóa đề xuất: {current_user} trên đề xuất ID {id}")
            return jsonify({'message': 'Không có quyền truy cập!'}), 403
        conn.execute('DELETE FROM proposals WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        app.logger.info(f"Xóa đề xuất thành công: ID {id} bởi {current_user}")
        return jsonify({'message': 'Xóa đề xuất thành công!'})
    except Exception as e:
        app.logger.error(f"Lỗi xóa đề xuất: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)