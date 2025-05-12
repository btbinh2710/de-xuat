from flask import Blueprint, request, jsonify, current_app, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import jwt
from .models import Proposal, db, proposal_schema, APIError

proposals_bp = Blueprint('proposals', __name__)

limiter = Limiter(key_func=get_remote_address)

@proposals_bp.record
def record_params(setup_state):
    limiter.init_app(setup_state.app)

@proposals_bp.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify({'message': error.message, 'status_code': error.status_code})
    response.status_code = error.status_code
    current_app.logger.error(f'APIError: {error.message} (Status: {error.status_code})')
    return response

def authenticate_token():
    token = request.headers.get('Authorization', '').split(' ')[1] if 'Authorization' in request.headers else None
    if not token:
        raise APIError('Token bắt buộc', 401)
    try:
        user = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        current_app.logger.info(f'Token xác thực thành công cho người dùng: {user["username"]}')
        return user
    except jwt.ExpiredSignatureError:
        raise APIError('Token đã hết hạn', 401)
    except jwt.InvalidTokenError:
        raise APIError('Token không hợp lệ', 403)

@proposals_bp.route('/api/proposals', methods=['GET'])
@limiter.limit("100/hour")
def get_proposals():
    user = authenticate_token()
    if user['role'] == 'admin':
        proposals = Proposal.query.all()
    else:
        proposals = Proposal.query.filter_by(branch=user['branch']).all()

    current_app.logger.info(f'Lấy {len(proposals)} đề xuất cho người dùng: {user["username"]}')
    return jsonify([{
        'branch': p.branch,
        'id': p.id,
        'proposer': p.proposer,
        'room': p.room,
        'department': p.department,
        'date': p.date,
        'code': p.code,
        'proposal': p.proposal,
        'content': p.content,
        'purpose': p.purpose,
        'supplier': p.supplier,
        'estimated_cost': p.estimated_cost,
        'budget': p.budget,
        'approved_amount': p.approved_amount,
        'transfer_code': p.transfer_code,
        'payment_date': p.payment_date,
        'notes': p.notes,
        'status': p.status,
        'approver': p.approver,
        'approval_date': p.approval_date,
        'completed': p.completed
    } for p in proposals])

@proposals_bp.route('/api/proposals', methods=['POST'])
@limiter.limit("50/hour")
def add_proposal():
    user = authenticate_token()
    if user['role'] == 'admin':
        raise APIError('Admin không thể thêm đề xuất!', 403)

    data = request.get_json()
    try:
        validated_data = proposal_schema.load(data)
    except ValidationError as err:
        raise APIError(f'Lỗi validation: {err.messages}', 400)

    proposal = Proposal(
        proposer=validated_data.get('proposer'),
        room=validated_data.get('room'),
        branch=user['branch'],
        department=validated_data.get('department'),
        date=validated_data.get('date'),
        code=validated_data.get('code'),
        proposal=validated_data.get('proposal'),
        content=validated_data.get('content'),
        purpose=validated_data.get('purpose'),
        supplier=validated_data.get('supplier'),
        estimated_cost=validated_data.get('estimated_cost'),
        budget=validated_data.get('budget'),
        approved_amount=validated_data.get('approved_amount'),
        transfer_code=validated_data.get('transfer_code'),
        payment_date=validated_data.get('payment_date'),
        notes=validated_data.get('notes'),
        status=validated_data.get('status'),
        approver=validated_data.get('approver'),
        approval_date=validated_data.get('approval_date'),
        completed=validated_data.get('completed')
    )

    db.session.add(proposal)
    db.session.commit()

    current_app.logger.info(f'Tạo đề xuất mới ID {proposal.id} bởi người dùng: {user["username"]}')
    return jsonify({
        'branch': proposal.branch,
        'id': proposal.id,
        'proposer': proposal.proposer,
        'room': proposal.room,
        'department': proposal.department,
        'date': proposal.date,
        'code': proposal.code,
        'proposal': proposal.proposal,
        'content': proposal.content,
        'purpose': proposal.purpose,
        'supplier': proposal.supplier,
        'estimated_cost': proposal.estimated_cost,
        'budget': proposal.budget,
        'approved_amount': proposal.approved_amount,
        'transfer_code': proposal.transfer_code,
        'payment_date': proposal.payment_date,
        'notes': proposal.notes,
        'status': proposal.status,
        'approver': proposal.approver,
        'approval_date': proposal.approval_date,
        'completed': proposal.completed
    }), 201

@proposals_bp.route('/api/proposals/<int:id>', methods=['PUT'])
@limiter.limit("50/hour")
def update_proposal(id):
    user = authenticate_token()
    proposal = Proposal.query.get(id)
    
    if not proposal:
        raise APIError('Đề xuất không tồn tại!', 404)
    if user['role'] != 'admin' and proposal.branch != user['branch']:
        raise APIError('Bạn không có quyền chỉnh sửa đề xuất này!', 403)

    data = request.get_json()
    try:
        validated_data = proposal_schema.load(data, partial=True)
    except ValidationError as err:
        raise APIError(f'Lỗi validation: {err.messages}', 400)

    for key, value in validated_data.items():
        if value is not None:
            setattr(proposal, key, value)

    db.session.commit()

    current_app.logger.info(f'Cập nhật đề xuất ID {id} bởi người dùng: {user["username"]}')
    return jsonify({
        'branch': proposal.branch,
        'id': proposal.id,
        'proposer': proposal.proposer,
        'room': proposal.room,
        'department': proposal.department,
        'date': proposal.date,
        'code': proposal.code,
        'proposal': proposal.proposal,
        'content': proposal.content,
        'purpose': proposal.purpose,
        'supplier': proposal.supplier,
        'estimated_cost': proposal.estimated_cost,
        'budget': proposal.budget,
        'approved_amount': proposal.approved_amount,
        'transfer_code': proposal.transfer_code,
        'payment_date': proposal.payment_date,
        'notes': proposal.notes,
        'status': proposal.status,
        'approver': proposal.approver,
        'approval_date': proposal.approval_date,
        'completed': proposal.completed
    })

@proposals_bp.route('/api/proposals/<int:id>', methods=['DELETE'])
@limiter.limit("50/hour")
def delete_proposal(id):
    user = authenticate_token()
    proposal = Proposal.query.get(id)
    
    if not proposal:
        raise APIError('Đề xuất không tồn tại!', 404)
    if user['role'] != 'admin' and proposal.branch != user['branch']:
        raise APIError('Bạn không có quyền xóa đề xuất này!', 403)

    db.session.delete(proposal)
    db.session.commit()

    current_app.logger.info(f'Xóa đề xuất ID {id} bởi người dùng: {user["username"]}')
    return '', 204

@proposals_bp.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
    return response