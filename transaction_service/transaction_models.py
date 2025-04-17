import os
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Transaction(db.Model):
    """Transaction model for transaction service"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_type = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # For deposit/withdrawal
    account_id = db.Column(db.String(36))
    
    # For transfers
    from_account_id = db.Column(db.String(36))
    to_account_id = db.Column(db.String(36))
    transfer_type = db.Column(db.String(20))
    
    def to_dict(self):
        """Convert Transaction object to dictionary"""
        data = {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'description': self.description,
            'status': self.status,
            'timestamp': self.timestamp.isoformat()
        }
        
        if self.transaction_type in ['deposit', 'withdrawal']:
            data['account_id'] = self.account_id
        elif self.transaction_type == 'transfer':
            data['from_account_id'] = self.from_account_id
            data['to_account_id'] = self.to_account_id
            data['transfer_type'] = self.transfer_type
            
        return data