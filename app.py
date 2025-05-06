from flask import Flask, request, jsonify
import sqlite3
import hashlib
import jwt
import datetime

app = Flask(__name__)
JWT_SECRET = 'PhuongAnhLogistics2025!'  # Lưu trong biến môi trường

def get_db():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = hashlib.sha256(data['password'].encode()).hexdigest()
    branch = data['branch']
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password, branch) VALUES (?, ?, ?)',
                  (username, password, branch))
        conn.commit()
        return jsonify({'message': 'User created'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = hashlib.sha256(data['password'].encode()).hexdigest()
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        token = jwt.encode({
            'username': username,
            'branch': user['branch'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, JWT_SECRET, algorithm='HS256')
        return jsonify({'token': token, 'branch': user['branch']})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/proposals', methods=['POST'])
def create_proposal():
    token = request.headers.get('Authorization', '').split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        data = request.get_json()
        data['branch'] = payload['branch']
        conn = get_db()
        c = conn.cursor()
        c.execute('''INSERT INTO proposals (maHang, tenHang, donVi, soLuong, donGia, thanhTien, nhaCungCap, ghiChu, branch)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (data['maHang'], data['tenHang'], data['donVi'], data['soLuong'], data['donGia'],
                   data['thanhTien'], data['nhaCungCap'], data['ghiChu'], data['branch']))
        conn.commit()
        conn.close()
        return jsonify(data), 201
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/api/proposals', methods=['GET'])
def get_proposals():
    token = request.headers.get('Authorization', '').split(' ')[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM proposals WHERE branch = ?', (payload['branch'],))
        proposals = [dict(row) for row in c.fetchall()]
        conn.close()
        return jsonify(proposals)
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))