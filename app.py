import sqlite3
import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import bcrypt
import jwt
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'e0e55e5f584ef6555aa9bb957a4b75fb0d674e0693c54da243ee8dcbefff7258'
logging.basicConfig(level=logging.INFO)

# Cấu hình CORS chi tiết
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "https://btbinh2710.github.io", "https://btbinh2710.github.io/de-xuat", "null"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

def get_db_connection():
    try:
        conn = sqlite3.connect('proposals.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        app.logger.error(f"Lỗi kết nối cơ sở dữ liệu: {str(e)}")
        return None

def init_db():
    try:
        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong init_db")
            return False
        c = conn.cursor()
        
        # Xóa bảng cũ để khởi tạo lại
        c.execute('DROP TABLE IF EXISTS users')
        c.execute('DROP TABLE IF EXISTS proposals')

        # Tạo bảng users
        c.execute('''CREATE TABLE users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            branch TEXT NOT NULL,
            role TEXT NOT NULL
        )''')

        # Tạo bảng proposals
        c.execute('''CREATE TABLE proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposer TEXT NOT NULL,
            room TEXT NOT NULL,
            branch TEXT NOT NULL,
            department TEXT NOT NULL,
            date TEXT NOT NULL,
            code TEXT NOT NULL,
            content TEXT NOT NULL,
            purpose TEXT,
            supplier TEXT NOT NULL,
            estimated_cost REAL NOT NULL,
            approved_amount REAL,
            transfer_code TEXT,
            payment_date TEXT,
            status TEXT,
            approver TEXT,
            approval_date TEXT,
            completed TEXT,
            notes TEXT,
            UNIQUE(code, branch)
        )''')

        # Thêm dữ liệu người dùng mẫu
        users = [
            ('admin', 'admin123', 'Admin', 'admin'),
            ('accountant', 'accountant123', 'Accountant', 'accountant'),
            ('xdv_thaodien_manager1', 'manager123', 'XDV_ThaoDien', 'manager'),
            ('xdv_thaodien_employee1', 'employee123', 'XDV_ThaoDien', 'employee'),
        ]
        for user in users:
            username, password, branch, role = user
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            c.execute('INSERT INTO users (username, password, branch, role) VALUES (?, ?, ?, ?)',
                     (username, hashed.decode('utf-8'), branch, role))

        # Thêm dữ liệu đề xuất mẫu
        proposals = [
            ('Nguyễn Văn A', 'Phòng Kinh Doanh', 'XDV_ThaoDien', 'Bộ phận Bán hàng', '01/05/2025', 'DX001', 'Mua máy in', 'Hỗ trợ in ấn tài liệu', 'Công ty ABC', 5000000, 5000000, 'CK001', '02/05/2025', 'Đã xong', 'Trần Văn B', '02/05/2025', 'Yes', 'Đã thanh toán'),
            ('Trần Thị B', 'Phòng Hành Chính', 'XDV_ThaoDien', 'Bộ phận Nhân sự', '03/05/2025', 'DX002', 'Mua bàn ghế', 'Nâng cấp văn phòng', 'Công ty XYZ', 10000000, null, null, null, 'Đang xử lý', null, null, 'No', null),
        ]
        for proposal in proposals:
            c.execute('''INSERT INTO proposals (proposer, room, branch, department, date, code, content, purpose, 
                        supplier, estimated_cost, approved_amount, transfer_code, payment_date, status, approver, 
                        approval_date, completed, notes) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', proposal)

        conn.commit()
        conn.close()
        app.logger.info("Khởi tạo cơ sở dữ liệu thành công")
        return True
    except sqlite3.Error as e:
        app.logger.error(f"Lỗi khởi tạo cơ sở dữ liệu: {str(e)}")
        return False

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        # Xử lý yêu cầu preflight
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

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
        app.logger.info(f"User data: {dict(user) if user else None}")
        if not user:
            conn.close()
            app.logger.warning(f"Không tìm thấy người dùng: {username}")
            return jsonify({'message': 'Thông tin đăng nhập không hợp lệ!'}), 401
        app.logger.info(f"Password provided: {password}")
        app.logger.info(f"Stored hashed password: {user['password']}")
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            app.logger.info("Mật khẩu khớp")
            token = jwt.encode({
                'username': username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            conn.close()
            app.logger.info(f"Đăng nhập thành công: {username}")
            response = jsonify({
                'token': token,
                'username': user['username'],
                'branch': user['branch'],
                'role': user['role']
            })
            response.headers.add('Access-Control-Allow-Origin', 'https://btbinh2710.github.io')
            return response
        else:
            conn.close()
            app.logger.warning(f"Mật khẩu không khớp: {username}")
            return jsonify({'message': 'Thông tin đăng nhập không hợp lệ!'}), 401
    except Exception as e:
        app.logger.error(f"Lỗi đăng nhập: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

@app.route('/api/proposals', methods=['GET', 'OPTIONS'])
def get_proposals():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            app.logger.warning("Yêu cầu không có token hoặc token không hợp lệ")
            return jsonify({'message': 'Token không hợp lệ!'}), 401
        token = token.split(' ')[1]
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            app.logger.warning("Token đã hết hạn")
            return jsonify({'message': 'Token đã hết hạn!'}), 401
        except jwt.InvalidTokenError:
            app.logger.warning("Token không hợp lệ")
            return jsonify({'message': 'Token không hợp lệ!'}), 401

        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong get_proposals")
            return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại'}), 500
        proposals = conn.execute('SELECT * FROM proposals').fetchall()
        conn.close()
        app.logger.info("Lấy danh sách đề xuất thành công")
        response = jsonify([dict(row) for row in proposals])
        response.headers.add('Access-Control-Allow-Origin', 'https://btbinh2710.github.io')
        return response
    except Exception as e:
        app.logger.error(f"Lỗi khi lấy đề xuất: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

@app.route('/api/proposals', methods=['POST', 'OPTIONS'])
def create_proposal():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            app.logger.warning("Yêu cầu không có token hoặc token không hợp lệ")
            return jsonify({'message': 'Token không hợp lệ!'}), 401
        token = token.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            app.logger.warning("Token đã hết hạn")
            return jsonify({'message': 'Token đã hết hạn!'}), 401
        except jwt.InvalidTokenError:
            app.logger.warning("Token không hợp lệ")
            return jsonify({'message': 'Token không hợp lệ!'}), 401

        data = request.get_json()
        if not data:
            app.logger.warning("Dữ liệu yêu cầu trống")
            return jsonify({'message': 'Dữ liệu trống!'}), 400

        required_fields = ['proposer', 'room', 'branch', 'department', 'date', 'code', 'content', 'supplier', 'estimated_cost']
        for field in required_fields:
            if field not in data or not data[field]:
                app.logger.warning(f"Thiếu trường bắt buộc: {field}")
                return jsonify({'message': f"Thiếu trường bắt buộc: {field}"}), 400

        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong create_proposal")
            return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại'}), 500
        c = conn.cursor()
        try:
            c.execute('''INSERT INTO proposals (proposer, room, branch, department, date, code, content, purpose, 
                        supplier, estimated_cost, approved_amount, transfer_code, payment_date, status, approver, 
                        approval_date, completed, notes) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (data['proposer'], data['room'], data['branch'], data['department'], data['date'], data['code'],
                      data['content'], data.get('purpose'), data['supplier'], data['estimated_cost'],
                      data.get('approved_amount'), data.get('transfer_code'), data.get('payment_date'),
                      data.get('status'), data.get('approver'), data.get('approval_date'),
                      data.get('completed'), data.get('notes')))
            conn.commit()
            conn.close()
            app.logger.info(f"Tạo đề xuất thành công: {data['code']}")
            response = jsonify({'message': 'Tạo đề xuất thành công'})
            response.headers.add('Access-Control-Allow-Origin', 'https://btbinh2710.github.io')
            return response, 201
        except sqlite3.IntegrityError:
            conn.close()
            app.logger.warning(f"Mã đề xuất đã tồn tại: {data['code']}")
            return jsonify({'message': 'Mã đề xuất đã tồn tại cho chi nhánh này!'}), 400
    except Exception as e:
        app.logger.error(f"Lỗi khi tạo đề xuất: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

@app.route('/api/proposals/<int:id>', methods=['PUT', 'OPTIONS'])
def update_proposal(id):
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            app.logger.warning("Yêu cầu không có token hoặc token không hợp lệ")
            return jsonify({'message': 'Token không hợp lệ!'}), 401
        token = token.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            app.logger.warning("Token đã hết hạn")
            return jsonify({'message': 'Token đã hết hạn!'}), 401
        except jwt.InvalidTokenError:
            app.logger.warning("Token không hợp lệ")
            return jsonify({'message': 'Token không hợp lệ!'}), 401

        data = request.get_json()
        if not data:
            app.logger.warning("Dữ liệu yêu cầu trống")
            return jsonify({'message': 'Dữ liệu trống!'}), 400

        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong update_proposal")
            return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại'}), 500
        c = conn.cursor()
        c.execute('SELECT * FROM proposals WHERE id = ?', (id,))
        proposal = c.fetchone()
        if not proposal:
            conn.close()
            app.logger.warning(f"Đề xuất không tồn tại: ID {id}")
            return jsonify({'message': 'Đề xuất không tồn tại!'}), 404

        update_fields = []
        update_values = []
        for field in ['proposer', 'room', 'branch', 'department', 'date', 'code', 'content', 'purpose', 'supplier',
                      'estimated_cost', 'approved_amount', 'transfer_code', 'payment_date', 'status', 'approver',
                      'approval_date', 'completed', 'notes']:
            if field in data:
                update_fields.append(f"{field} = ?")
                update_values.append(data[field])
        
        if not update_fields:
            conn.close()
            app.logger.warning("Không có trường nào để cập nhật")
            return jsonify({'message': 'Không có trường nào để cập nhật!'}), 400

        update_values.append(id)
        query = f"UPDATE proposals SET {', '.join(update_fields)} WHERE id = ?"
        c.execute(query, update_values)
        conn.commit()
        conn.close()
        app.logger.info(f"Cập nhật đề xuất thành công: ID {id}")
        response = jsonify({'message': 'Cập nhật đề xuất thành công'})
        response.headers.add('Access-Control-Allow-Origin', 'https://btbinh2710.github.io')
        return response
    except Exception as e:
        app.logger.error(f"Lỗi khi cập nhật đề xuất: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

@app.route('/api/proposals/<int:id>', methods=['DELETE', 'OPTIONS'])
def delete_proposal(id):
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

    try:
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            app.logger.warning("Yêu cầu không có token hoặc token không hợp lệ")
            return jsonify({'message': 'Token không hợp lệ!'}), 401
        token = token.split(' ')[1]
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            app.logger.warning("Token đã hết hạn")
            return jsonify({'message': 'Token đã hết hạn!'}), 401
        except jwt.InvalidTokenError:
            app.logger.warning("Token không hợp lệ")
            return jsonify({'message': 'Token không hợp lệ!'}), 401

        conn = get_db_connection()
        if not conn:
            app.logger.error("Không thể kết nối cơ sở dữ liệu trong delete_proposal")
            return jsonify({'message': 'Kết nối cơ sở dữ liệu thất bại'}), 500
        c = conn.cursor()
        c.execute('SELECT * FROM proposals WHERE id = ?', (id,))
        proposal = c.fetchone()
        if not proposal:
            conn.close()
            app.logger.warning(f"Đề xuất không tồn tại: ID {id}")
            return jsonify({'message': 'Đề xuất không tồn tại!'}), 404

        c.execute('DELETE FROM proposals WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        app.logger.info(f"Xóa đề xuất thành công: ID {id}")
        response = jsonify({'message': 'Xóa đề xuất thành công'})
        response.headers.add('Access-Control-Allow-Origin', 'https://btbinh2710.github.io')
        return response
    except Exception as e:
        app.logger.error(f"Lỗi khi xóa đề xuất: {str(e)}")
        return jsonify({'message': 'Lỗi server nội bộ'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)