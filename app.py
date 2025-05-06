
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

DATABASE = 'data.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return jsonify({"message": "Backend Flask hoạt động thành công!"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        session['user'] = {
            "username": user['username'],
            "role": user['role'],
            "branch": user['branch']
        }
        return jsonify(session['user'])

    return jsonify({"error": "Tên đăng nhập hoặc mật khẩu không đúng"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Đã đăng xuất"})

@app.route('/api/proposals', methods=['GET', 'POST'])
def proposals():
    if request.method == 'POST':
        data = request.get_json()
        conn = get_db()
        conn.execute(
            "INSERT INTO proposals (nguoi_de_nghi, noi_dung, chi_nhanh) VALUES (?, ?, ?)",
            (data['nguoiDeNghi'], data['noiDung'], data['chiNhanh'])
        )
        conn.commit()
        conn.close()
        return jsonify({"message": "Đã lưu đề xuất thành công"})

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proposals")
    proposals = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(proposals)

if __name__ == '__main__':
    app.run(debug=True)
