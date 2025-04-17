import os
import uuid
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """User model for authentication service"""
    
    def __init__(self, username, email, password_hash, role='customer', id=None):
        """Initialize a new User object"""
        self.id = id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = datetime.now().isoformat()
        self.status = 'active'
    
    @staticmethod
    def hash_password(password):
        """Hash password for storage"""
        return generate_password_hash(password)
    
    def verify_password(self, password):
        """Verify a password against the hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert User object to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create User object from dictionary"""
        user = cls(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            role=data.get('role', 'customer'),
            id=data.get('id')
        )
        user.created_at = data.get('created_at', user.created_at)
        user.status = data.get('status', 'active')
        return user

class Account:
    """Account model for account service"""
    
    def __init__(self, user_id, account_type, balance=0, status='active', id=None, account_number=None):
        """Initialize a new Account object"""
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.account_number = account_number or f"ACC{uuid.uuid4().hex[:8].upper()}"
        self.account_type = account_type
        self.balance = balance
        self.status = status
        self.created_at = datetime.now().isoformat()
    
    def to_dict(self):
        """Convert Account object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'balance': self.balance,
            'status': self.status,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Account object from dictionary"""
        account = cls(
            user_id=data.get('user_id'),
            account_type=data.get('account_type'),
            balance=data.get('balance', 0),
            status=data.get('status', 'active'),
            id=data.get('id'),
            account_number=data.get('account_number')
        )
        account.created_at = data.get('created_at', account.created_at)
        return account

class Transaction:
    """Transaction model for transaction service"""
    
    def __init__(self, transaction_type, amount, description='', status='pending', id=None):
        """Initialize a new Transaction object"""
        self.id = id or str(uuid.uuid4())
        self.transaction_type = transaction_type
        self.amount = amount
        self.description = description
        self.status = status
        self.timestamp = datetime.now().isoformat()
        
        # These will be set by set_deposit_withdrawal_data or set_transfer_data
        self.account_id = None
        self.from_account_id = None
        self.to_account_id = None
        self.transfer_type = None
    
    def set_deposit_withdrawal_data(self, account_id):
        """Set data for deposit or withdrawal transaction"""
        self.account_id = account_id
    
    def set_transfer_data(self, from_account_id, to_account_id, transfer_type='internal'):
        """Set data for transfer transaction"""
        self.from_account_id = from_account_id
        self.to_account_id = to_account_id
        self.transfer_type = transfer_type
    
    def to_dict(self):
        """Convert Transaction object to dictionary"""
        data = {
            'id': self.id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'description': self.description,
            'status': self.status,
            'timestamp': self.timestamp
        }
        
        if self.transaction_type in ['deposit', 'withdrawal']:
            data['account_id'] = self.account_id
        elif self.transaction_type == 'transfer':
            data['from_account_id'] = self.from_account_id
            data['to_account_id'] = self.to_account_id
            data['transfer_type'] = self.transfer_type
            
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create Transaction object from dictionary"""
        transaction = cls(
            transaction_type=data.get('transaction_type'),
            amount=data.get('amount', 0),
            description=data.get('description', ''),
            status=data.get('status', 'pending'),
            id=data.get('id')
        )
        transaction.timestamp = data.get('timestamp', transaction.timestamp)
        
        if data.get('transaction_type') in ['deposit', 'withdrawal']:
            transaction.account_id = data.get('account_id')
        elif data.get('transaction_type') == 'transfer':
            transaction.from_account_id = data.get('from_account_id')
            transaction.to_account_id = data.get('to_account_id')
            transaction.transfer_type = data.get('transfer_type', 'internal')
            
        return transaction

class Report:
    """Report model for reporting service"""
    
    def __init__(self, report_type, parameters=None, id=None):
        """Initialize a new Report object"""
        self.id = id or str(uuid.uuid4())
        self.report_type = report_type
        self.parameters = parameters or {}
        self.generated_at = datetime.now().isoformat()
        self.data = {}
    
    def set_data(self, data):
        """Set report data"""
        self.data = data
    
    def to_dict(self):
        """Convert Report object to dictionary"""
        return {
            'id': self.id,
            'report_type': self.report_type,
            'parameters': self.parameters,
            'generated_at': self.generated_at,
            'data': self.data
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Report object from dictionary"""
        report = cls(
            report_type=data.get('report_type'),
            parameters=data.get('parameters', {}),
            id=data.get('id')
        )
        report.generated_at = data.get('generated_at', report.generated_at)
        report.data = data.get('data', {})
        return report