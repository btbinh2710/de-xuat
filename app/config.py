from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
    branch = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.Index('idx_user_username', 'username'),
    )

class Proposal(db.Model):
    __tablename__ = 'proposals'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    proposer = db.Column(db.String(255), nullable=False)
    room = db.Column(db.String(255))
    branch = db.Column(db.String(255), nullable=False, index=True)
    department = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    code = db.Column(db.String(50))
    proposal = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    purpose = db.Column(db.Text)
    supplier = db.Column(db.String(255))
    estimated_cost = db.Column(db.Float)
    budget = db.Column(db.Float)
    approved_amount = db.Column(db.Float)
    transfer_code = db.Column(db.String(50))
    payment_date = db.Column(db.String(10))
    notes = db.Column(db.Text)
    status = db.Column(db.String(50))
    approver = db.Column(db.String(255))
    approval_date = db.Column(db.String(10))
    completed = db.Column(db.String(50))

    __table_args__ = (
        db.Index('idx_proposal_branch', 'branch'),
        db.Index('idx_proposal_date', 'date'),
    )

class ProposalSchema(Schema):
    proposer = fields.Str(required=True, validate=validate.Length(min=1))
    room = fields.Str(allow_none=True)
    department = fields.Str(required=True, validate=validate.Length(min=1))
    date = fields.Str(required=True, validate=validate.Regexp(r'^\d{2}/\d{2}/\d{4}$'))
    code = fields.Str(allow_none=True)
    proposal = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    purpose = fields.Str(allow_none=True)
    supplier = fields.Str(allow_none=True)
    estimated_cost = fields.Float(allow_none=True, validate=validate.Range(min=0))
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