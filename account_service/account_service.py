import os
import logging
import requests
import jwt
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify
from account_service.account_models import db, Account

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["JWT_SECRET_KEY"] = os.environ.get("SESSION_SECRET", "account_service_secret_key")

# Initialize extensions
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Authentication service URL
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:8001")

# Helper functions
def token_required(f):
    """Decorator for endpoints that require a valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Verify token with auth service
            response = requests.get(
                f"{AUTH_SERVICE_URL}/api/auth/verify_token",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if not response.ok:
                return jsonify({'message': 'Invalid or expired token'}), 401
            
            current_user = response.json()
                
        except requests.RequestException:
            return jsonify({'message': 'Authorization service unavailable'}), 503
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator for endpoints that require admin privileges"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        # Verify admin role with auth service
        token = request.headers.get('Authorization').split(' ')[1]
        
        try:
            response = requests.get(
                f"{AUTH_SERVICE_URL}/api/auth/verify_admin",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if not response.ok or not response.json().get('is_admin'):
                return jsonify({'message': 'Admin privilege required'}), 403
                
        except requests.RequestException:
            return jsonify({'message': 'Authorization service unavailable'}), 503
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def generate_account_number():
    """Generate a unique account number"""
    prefix = "ACC"
    random_part = os.urandom(4).hex().upper()
    return f"{prefix}{random_part}"

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'account-service'}), 200

@app.route('/api/accounts/list', methods=['GET'])
@token_required
def list_accounts(current_user):
    """List all accounts for the current user"""
    with app.app_context():
        accounts = Account.query.filter_by(user_id=current_user['user_id']).all()
        return jsonify({
            'accounts': [account.to_dict() for account in accounts]
        }), 200

@app.route('/api/accounts/create', methods=['POST'])
@token_required
def create_account(current_user):
    """Create a new account for the current user"""
    data = request.json
    
    # Validate required fields
    if 'account_type' not in data:
        return jsonify({'message': 'Account type is required'}), 400
    
    # Check for valid account types
    valid_types = ['checking', 'savings', 'fixed_deposit']
    if data['account_type'] not in valid_types:
        return jsonify({'message': f'Invalid account type. Must be one of: {", ".join(valid_types)}'}), 400
    
    initial_deposit = float(data.get('initial_deposit', 0))
    if initial_deposit < 0:
        return jsonify({'message': 'Initial deposit cannot be negative'}), 400
    
    with app.app_context():
        # Create new account
        new_account = Account(
            user_id=current_user['user_id'],
            account_type=data['account_type'],
            balance=initial_deposit
        )
        
        db.session.add(new_account)
        db.session.commit()
        
        return jsonify({
            'message': 'Account created successfully',
            'account': new_account.to_dict()
        }), 201

@app.route('/api/accounts/details/<account_id>', methods=['GET'])
@token_required
def get_account_details(current_user, account_id):
    """Get details of a specific account"""
    with app.app_context():
        account = Account.query.filter_by(id=account_id).first()
        
        if not account:
            return jsonify({'message': 'Account not found'}), 404
        
        # Check if the account belongs to the current user
        if account.user_id != current_user['user_id'] and current_user['role'] != 'admin':
            return jsonify({'message': 'Access denied'}), 403
            
        return jsonify(account.to_dict()), 200

@app.route('/api/accounts/close/<account_id>', methods=['DELETE'])
@token_required
def close_account(current_user, account_id):
    """Close an account"""
    with app.app_context():
        account = Account.query.filter_by(id=account_id).first()
        
        if not account:
            return jsonify({'message': 'Account not found'}), 404
        
        # Check if the account belongs to the current user
        if account.user_id != current_user['user_id'] and current_user['role'] != 'admin':
            return jsonify({'message': 'Access denied'}), 403
        
        # Check if the account already closed
        if account.status != 'active':
            return jsonify({'message': 'Account is already closed'}), 400
        
        # Check if the account has zero balance
        if account.balance > 0:
            return jsonify({'message': 'Account must have zero balance before closing'}), 400
        
        # Close the account
        account.status = 'closed'
        db.session.commit()
        
        return jsonify({
            'message': 'Account closed successfully',
            'account': account.to_dict()
        }), 200

@app.route('/api/accounts/all', methods=['GET'])
@token_required
@admin_required
def get_all_accounts(current_user):
    """Get all accounts (admin only)"""
    with app.app_context():
        accounts = Account.query.all()
        return jsonify({
            'accounts': [account.to_dict() for account in accounts]
        }), 200

@app.route('/api/accounts/update/<account_id>', methods=['PUT'])
@token_required
@admin_required
def update_account(current_user, account_id):
    """Update account details (admin only)"""
    data = request.json
    
    with app.app_context():
        account = Account.query.filter_by(id=account_id).first()
        
        if not account:
            return jsonify({'message': 'Account not found'}), 404
        
        # Fields that admins can update
        allowed_fields = ['account_type', 'status']
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        
        for key, value in updates.items():
            setattr(account, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Account updated successfully',
            'account': account.to_dict()
        }), 200

@app.route('/api/accounts/user/<user_id>', methods=['GET'])
@token_required
@admin_required
def get_user_accounts(current_user, user_id):
    """Get accounts for a specific user (admin only)"""
    with app.app_context():
        accounts = Account.query.filter_by(user_id=user_id).all()
        return jsonify({
            'accounts': [account.to_dict() for account in accounts]
        }), 200

@app.route('/api/accounts/balance/update', methods=['POST'])
def update_balance():
    """Update account balance (internal use by transaction service)"""
    # This endpoint should be protected in production but is left open for the demo
    data = request.json
    
    # Validate required fields
    required_fields = ['account_id', 'amount', 'operation']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    account_id = data['account_id']
    amount = float(data['amount'])
    operation = data['operation']
    
    if operation not in ['credit', 'debit']:
        return jsonify({'message': 'Invalid operation. Must be either "credit" or "debit"'}), 400
    
    with app.app_context():
        account = Account.query.filter_by(id=account_id).first()
        
        if not account:
            return jsonify({'message': 'Account not found'}), 404
        
        if account.status != 'active':
            return jsonify({'message': 'Account is not active'}), 400
        
        if operation == 'credit':
            account.balance += amount
        else:  # debit
            if account.balance < amount:
                return jsonify({'message': 'Insufficient funds'}), 400
            account.balance -= amount
        
        db.session.commit()
        
        return jsonify({
            'message': 'Balance updated successfully',
            'account': account.to_dict()
        }), 200

@app.route('/api/accounts/validate/<account_id>', methods=['GET'])
def validate_account(account_id):
    """Validate if an account exists and is active (internal use)"""
    # This endpoint should be protected in production but is left open for the demo
    with app.app_context():
        account = Account.query.filter_by(id=account_id).first()
        
        if not account:
            return jsonify({
                'valid': False,
                'message': 'Account not found'
            }), 200
        
        if account.status != 'active':
            return jsonify({
                'valid': False,
                'message': 'Account is not active'
            }), 200
        
        return jsonify({
            'valid': True,
            'account': account.to_dict()
        }), 200

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8002)