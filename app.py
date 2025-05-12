```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from marshmallow import Schema, fields, validates, ValidationError
from datetime import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
load_dotenv()

# Cấu hình CORS
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8000", "https://btbinh2710.github.io"]}})

# Cấu hình ứng dụng Flask
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///proposals.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['PORT'] = int(os.getenv('PORT', 10000))

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Định nghĩa mô hình Proposal
class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposer = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(100), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    purpose = db.Column(db.Text)
    supplier = db.Column(db.String(100), nullable=False)
    estimated_cost = db.Column(db.Float, nullable=False)
    budget = db.Column(db.Float)
    approved_amount = db.Column(db.Float)
    transfer_code = db.Column(db.String(50))
    payment_date = db.Column(db.String(10))
    notes = db.Column(db.Text)
    status = db.Column(db.String(50))
    approver = db.Column(db.String(100))
    approval_date = db.Column(db.String(10))
    completed = db.Column(db.String(10))

# Định nghĩa mô hình User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    branch = db.Column(db.String(100))

# Schema để xác thực dữ liệu Proposal
class ProposalSchema(Schema):
    proposer = fields.Str(required=True)
    room = fields.Str(required=True)
    branch = fields.Str(required=True)
    department = fields.Str(required=True)
    date = fields.Str(required=True)
    code = fields.Str(required=True)
    content = fields.Str(required=True)
    purpose = fields.Str(allow_none=True)
    supplier = fields.Str(required=True)
    estimated_cost = fields.Float(required=True)
    budget = fields.Float(allow_none=True)
    approved_amount = fields.Float(allow_none=True)
    transfer_code = fields.Str(allow_none=True)
    payment_date = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    approver = fields.Str(allow_none=True)
    approval_date = fields.Str(allow_none=True)
    completed = fields.Str(allow_none=True)

    @validates('date')
    def validate_date(self, value):
        if value and not self._is_valid_date(value):
            raise ValidationError('Date must be in DD/MM/YYYY format')

    @validates('payment_date')
    def validate_payment_date(self, value):
        if value and not self._is_valid_date(value):
            raise ValidationError('Payment date must be in DD/MM/YYYY format')

    @validates('approval_date')
    def validate_approval_date(self, value):
        if value and not self._is_valid_date(value):
            raise ValidationError('Approval date must be in DD/MM/YYYY format')

    @validates('estimated_cost')
    def validate_estimated_cost(self, value):
        if value < 0:
            raise ValidationError('Estimated cost must be non-negative')

    @validates('budget')
    def validate_budget(self, value):
        if value is not None and value < 0:
            raise ValidationError('Budget must be non-negative')

    @validates('approved_amount')
    def validate_approved_amount(self, value):
        if value is not None and value < 0:
            raise ValidationError('Approved amount must be non-negative')

    def _is_valid_date(self, date_str):
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False

proposal_schema = ProposalSchema()
proposals_schema = ProposalSchema(many=True)

# Endpoint đăng nhập
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'username': user.username, 'role': user.role, 'branch': user.branch})
    return jsonify({
        'token': access_token,
        'role': user.role,
        'branch': user.branch
    })

# Endpoint lấy danh sách đề xuất
@app.route('/api/proposals', methods=['GET'])
@jwt_required()
def get_proposals():
    current_user = get_jwt_identity()
    role = current_user['role']
    branch = current_user['branch']

    if role == 'accountant':
        proposals = Proposal.query.all()
    elif role == 'admin':
        proposals = Proposal.query.all()
    else:
        proposals = Proposal.query.filter_by(branch=branch).all()

    return jsonify(proposals_schema.dump(proposals))

# Endpoint thêm đề xuất
@app.route('/api/proposals', methods=['POST'])
@jwt_required()
def add_proposal():
    current_user = get_jwt_identity()
    if current_user['role'] == 'accountant':
        return jsonify({'message': 'Accountants cannot create proposals'}), 403

    try:
        data = proposal_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': err.messages}), 400

    new_proposal = Proposal(**data)
    db.session.add(new_proposal)
    db.session.commit()
    return jsonify(proposal_schema.dump(new_proposal)), 201

# Endpoint cập nhật đề xuất
@app.route('/api/proposals/<int:id>', methods=['PUT'])
@jwt_required()
def update_proposal(id):
    current_user = get_jwt_identity()
    role = current_user['role']
    branch = current_user['branch']

    proposal = Proposal.query.get_or_404(id)

    if role != 'admin' and proposal.branch != branch and role != 'accountant':
        return jsonify({'message': 'Unauthorized access'}), 403

    try:
        data = proposal_schema.load(request.get_json(), partial=(role == 'accountant'))
    except ValidationError as err:
        return jsonify({'message': err.messages}), 400

    if role == 'accountant':
        allowed_fields = ['approved_amount', 'transfer_code', 'payment_date', 'notes', 'completed', 'status']
        for key, value in data.items():
            if key in allowed_fields:
                setattr(proposal, key, value)
    else:
        for key, value in data.items():
            setattr(proposal, key, value)

    db.session.commit()
    return jsonify(proposal_schema.dump(proposal))

# Endpoint xóa đề xuất
@app.route('/api/proposals/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_proposal(id):
    current_user = get_jwt_identity()
    role = current_user['role']
    branch = current_user['branch']

    if role == 'accountant':
        return jsonify({'message': 'Accountants cannot delete proposals'}), 403

    proposal = Proposal.query.get_or_404(id)

    if role != 'admin' and proposal.branch != branch:
        return jsonify({'message': 'Unauthorized access'}), 403

    db.session.delete(proposal)
    db.session.commit()
    return jsonify({'message': 'Proposal deleted'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'])
```