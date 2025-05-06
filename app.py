
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
from werkzeug.security import check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Bật CORS toàn bộ + hỗ trợ credentials
CORS(app, supports_credentials=True)

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
    try:
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
            return jsonify(session['user']), 200
        else:
            return jsonify({"error": "Tên đăng nhập hoặc mật khẩu không đúng"}), 401

    except Exception as e:
        return jsonify({"error": "Lỗi xử lý login", "details": str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Đã đăng xuất"}), 200

if __name__ == '__main__':
    app.run(debug=True)
  