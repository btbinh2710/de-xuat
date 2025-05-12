from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
import datetime

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://btbinh2710.github.io"}})

# Danh sách người dùng giả lập
users = [
    {"username": "admin", "password": bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "role": "admin", "branch": "All"}
]
for i in range(1, 19):
    users.append({"username": f"chi_nhanh_{i}_manager1", "password": bcrypt.hashpw("manager123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "role": "manager", "branch": f"Chi Nhánh {i}"})
    users.append({"username": f"chi_nhanh_{i}_manager2", "password": bcrypt.hashpw("manager123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "role": "manager", "branch": f"Chi Nhánh {i}"})

# Danh sách đề xuất giả lập
proposals = [
    {"id": 1, "proposer": "Nguyễn Văn A", "department": "KD", "date": "2025-05-01", "code": "DX001", "proposal": "Mua laptop", "content": "Mua laptop phục vụ công việc", "supplier": "Công ty ABC", "estimated_cost": 15000000, "approved_amount": 0, "notes": "", "completed": "", "branch": "Chi Nhánh 1"}
]

def authenticate_token():
    token = request.headers.get('Authorization', '').split(' ')[1] if 'Authorization' in request.headers else None
    if not token:
        return None, jsonify({"error": "Token required"}), 401
    try:
        user = jwt.decode(token, 'your-secret-key', algorithms=['HS256'])
        return user, None, None
    except:
        return None, jsonify({"error": "Invalid token"}), 403

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = next((u for u in users if u['username'] == username), None)
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"error": "Tên đăng nhập hoặc mật khẩu không đúng!"}), 401

    token = jwt.encode({
        'username': user['username'],
        'role': user['role'],
        'branch': user['branch'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, 'your-secret-key')
    return jsonify({"token": token, "role": user['role'], "branch": user['branch']})

@app.route('/api/proposals', methods=['GET'])
def get_proposals():
    user, error, status = authenticate_token()
    if error:
        return error, status
    if user['role'] == 'admin':
        return jsonify(proposals)
    return jsonify([p for p in proposals if p['branch'] == user['branch']])

@app.route('/api/proposals', methods=['POST'])
def add_proposal():
    user, error, status = authenticate_token()
    if error:
        return error, status
    if user['role'] == 'admin':
        return jsonify({"error": "Admin không thể thêm đề xuất!"}), 403

    data = request.get_json()
    new_proposal = {
        "id": len(proposals) + 1,
        **data,
        "branch": user['branch']
    }
    proposals.append(new_proposal)
    return jsonify(new_proposal), 201

@app.route('/api/proposals/<int:id>', methods=['PUT'])
def update_proposal(id):
    user, error, status = authenticate_token()
    if error:
        return error, status
    proposal = next((p for p in proposals if p['id'] == id), None)
    if not proposal:
        return jsonify({"error": "Đề xuất không tồn tại!"}), 404
    if user['role'] != 'admin' and proposal['branch'] != user['branch']:
        return jsonify({"error": "Bạn không có quyền chỉnh sửa đề xuất này!"}), 403

    data = request.get_json()
    for key, value in data.items():
        proposal[key] = value
    return jsonify(proposal)

@app.route('/api/proposals/<int:id>', methods=['DELETE'])
def delete_proposal(id):
    user, error, status = authenticate_token()
    if error:
        return error, status
    proposal_index = next((i for i, p in enumerate(proposals) if p['id'] == id), None)
    if proposal_index is None:
        return jsonify({"error": "Đề xuất không tồn tại!"}), 404
    if user['role'] != 'admin' and proposals[proposal_index]['branch'] != user['branch']:
        return jsonify({"error": "Bạn không có quyền xóa đề xuất này!"}), 403

    proposals.pop(proposal_index)
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)