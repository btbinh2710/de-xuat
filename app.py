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

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://btbinh2710.github.io", "https://de-xuat-ea0h.onrender.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Authorization", "Content-Type"]
    }
})

if not os.path.exists('logs'):
    os.makedirs('logs')
handler = RotatingFileHandler('logs/app.log', maxBytes=1000000, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Ung dung khoi dong')

class APIError(Exception):
    def __init__(self, message, status_code):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class ProposalSchema(Schema):
    proposer = fields.Str(required=True, validate=validate.Length(min=1))
    room = fields.Str(required=True, validate=validate.Length(min=1))
    department = fields.Str(required=True, validate=validate.Length(min=1))
    date = fields.Str(required=True, validate=validate.Regexp(r'^\d{2}/\d{2}/\d{4}$'))
    code = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    purpose = fields.Str(allow_none=True)
    supplier = fields.Str(required=True, validate=validate.Length(min=1))
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

proposal_schema = ProposalSchema()

def get_db_connection():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

def format_proposal(proposal):
    return {
        'branch': proposal['branch'],
        'id': proposal['id'],
        'proposer': proposal['proposer'],
        'room': proposal['room'],
        'department': proposal['department'],
        'date': proposal['date'],
        'code': proposal['code'],
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

@app.route('/', methods=['GET', 'HEAD'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify({'message': error.message, 'status_code': error.status_code})
    response.status_code = error.status_code
    app.logger.error(f'APIError: {error.message} (Status: {error.status_code})')
    return response

@app.errorhandler(Exception)
def handle_general_error(error):
    response = jsonify({'message': 'Loi server noi bo', 'status_code': 500})
    response.status_code = 500
    app.logger.error(f'Loi khong mong muon: {str(error)}')
    return response

@app.route('/api/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = make_response()
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
    return response

def authenticate_token():
    token = request.headers.get('Authorization', '').split(' ')[1] if 'Authorization' in request.headers else None
    if not token:
        raise APIError('Token bat buoc', 401)
    try:
        user = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        app.logger.info(f'Token xac thuc thanh cong cho nguoi dung: {user["username"]}')
        return user, None, None
    except Exception as e:
        app.logger.error(f'Token khong hop le: {str(e)}')
        raise APIError('Token khong hop le', 403)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')