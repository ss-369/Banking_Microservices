import consul
import os
import logging
import requests
import jwt
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify
from transaction_service.transaction_models import db, Transaction

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("TRANSACTION_DATABASE_URL")
app.config["JWT_SECRET_KEY"] = os.environ.get("SESSION_SECRET", "transaction_service_secret_key")

# Initialize extensions
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Consul configuration
CONSUL_HOST = os.environ.get("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.environ.get("CONSUL_PORT", 8500))
SERVICE_NAME = "transaction-service"
SERVICE_ID = f"{SERVICE_NAME}-{os.urandom(8).hex()}"
SERVICE_PORT = 8003

# Initialize Consul client
consul_client = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

# Register service with Consul
def register_service():
    consul_client.agent.service.register(
        name=SERVICE_NAME,
        service_id=SERVICE_ID,
        address="localhost",
        port=SERVICE_PORT,
        check=consul.Check.http(
            f"http://localhost:{SERVICE_PORT}/api/health",
            interval="10s",
            timeout="5s",
        ),
    )
    logger.info(f"Registered service with Consul as {SERVICE_ID}")

# Deregister service from Consul
def deregister_service():
    consul_client.agent.service.deregister(SERVICE_ID)
    logger.info(f"Deregistered service from Consul: {SERVICE_ID}")

# Register service on startup
with app.app_context():
    register_service()

# Deregister service on shutdown
import atexit
atexit.register(deregister_service)

# Service URLs
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:8001")
ACCOUNT_SERVICE_URL = os.environ.get("ACCOUNT_SERVICE_URL", "http://localhost:8002")

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

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'transaction-service'}), 200

@app.route('/api/transactions/list', methods=['GET'])
@token_required
def list_transactions(current_user):
    """List all transactions for the current user"""
    # First get all accounts for the user
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/list",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to retrieve accounts'}), response.status_code
            
        accounts = response.json().get('accounts', [])
        account_ids = [account['id'] for account in accounts]
        
    except requests.RequestException:
        return jsonify({'message': 'Account service unavailable'}), 503
    
    # Now get transactions for these accounts
    with app.app_context():
        # Query for deposit/withdrawal transactions
        deposit_withdrawal_transactions = Transaction.query.filter(
            Transaction.transaction_type.in_(['deposit', 'withdrawal']),
            Transaction.account_id.in_(account_ids)
        ).all()
        
        # Query for transfer transactions
        transfer_transactions = Transaction.query.filter(
            Transaction.transaction_type == 'transfer',
            (Transaction.from_account_id.in_(account_ids) | Transaction.to_account_id.in_(account_ids))
        ).all()
        
        # Combine and sort by timestamp (descending)
        all_transactions = deposit_withdrawal_transactions + transfer_transactions
        all_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return jsonify({
            'transactions': [transaction.to_dict() for transaction in all_transactions]
        }), 200

@app.route('/api/transactions/recent', methods=['GET'])
@token_required
def recent_transactions(current_user):
    """Get recent transactions for the current user"""
    limit = int(request.args.get('limit', 5))
    
    # First get all accounts for the user
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/list",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to retrieve accounts'}), response.status_code
            
        accounts = response.json().get('accounts', [])
        account_ids = [account['id'] for account in accounts]
        
    except requests.RequestException:
        return jsonify({'message': 'Account service unavailable'}), 503
    
    # Now get recent transactions for these accounts
    with app.app_context():
        # Query for deposit/withdrawal transactions
        deposit_withdrawal_transactions = Transaction.query.filter(
            Transaction.transaction_type.in_(['deposit', 'withdrawal']),
            Transaction.account_id.in_(account_ids)
        ).order_by(Transaction.timestamp.desc()).limit(limit).all()
        
        # Query for transfer transactions
        transfer_transactions = Transaction.query.filter(
            Transaction.transaction_type == 'transfer',
            (Transaction.from_account_id.in_(account_ids) | Transaction.to_account_id.in_(account_ids))
        ).order_by(Transaction.timestamp.desc()).limit(limit).all()
        
        # Combine, sort by timestamp (descending), and limit
        all_transactions = deposit_withdrawal_transactions + transfer_transactions
        all_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        recent_transactions = all_transactions[:limit]
        
        return jsonify({
            'transactions': [transaction.to_dict() for transaction in recent_transactions]
        }), 200

@app.route('/api/transactions/account/<account_id>', methods=['GET'])
@token_required
def account_transactions(current_user, account_id):
    """Get transactions for a specific account"""
    # Verify account access
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/details/{account_id}",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to access account'}), response.status_code
            
    except requests.RequestException:
        return jsonify({'message': 'Account service unavailable'}), 503
    
    # Get transactions for this account
    with app.app_context():
        # Query for deposit/withdrawal transactions
        deposit_withdrawal_transactions = Transaction.query.filter(
            Transaction.transaction_type.in_(['deposit', 'withdrawal']),
            Transaction.account_id == account_id
        ).all()
        
        # Query for transfer transactions
        transfer_transactions = Transaction.query.filter(
            Transaction.transaction_type == 'transfer',
            (Transaction.from_account_id == account_id) | (Transaction.to_account_id == account_id)
        ).all()
        
        # Combine and sort by timestamp (descending)
        all_transactions = deposit_withdrawal_transactions + transfer_transactions
        all_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        
        return jsonify({
            'transactions': [transaction.to_dict() for transaction in all_transactions]
        }), 200

@app.route('/api/transactions/details/<transaction_id>', methods=['GET'])
@token_required
def transaction_details(current_user, transaction_id):
    """Get details of a specific transaction"""
    with app.app_context():
        transaction = Transaction.query.filter_by(id=transaction_id).first()
        
        if not transaction:
            return jsonify({'message': 'Transaction not found'}), 404
        
        # Check if the user has access to this transaction
        # For deposit/withdrawal, check if the account belongs to the user
        # For transfer, check if either the from or to account belongs to the user
        
        # Get user's accounts
        try:
            token = request.headers.get('Authorization').split(' ')[1]
            response = requests.get(
                f"{ACCOUNT_SERVICE_URL}/api/accounts/list",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if not response.ok:
                return jsonify({'message': 'Failed to retrieve accounts'}), response.status_code
                
            accounts = response.json().get('accounts', [])
            account_ids = [account['id'] for account in accounts]
            
            # Check if user has access to the transaction
            has_access = False
            if transaction.transaction_type in ['deposit', 'withdrawal']:
                has_access = transaction.account_id in account_ids
            elif transaction.transaction_type == 'transfer':
                has_access = (transaction.from_account_id in account_ids or 
                              transaction.to_account_id in account_ids)
            
            # Admin can access any transaction
            if current_user['role'] == 'admin':
                has_access = True
                
            if not has_access:
                return jsonify({'message': 'Access denied'}), 403
                
        except requests.RequestException:
            return jsonify({'message': 'Account service unavailable'}), 503
        
        return jsonify(transaction.to_dict()), 200

@app.route('/api/transactions/transfer', methods=['POST'])
@token_required
def transfer(current_user):
    """Create a transfer between accounts"""
    data = request.json
    
    # Validate required fields
    required_fields = ['from_account_id', 'to_account_id', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    from_account_id = data['from_account_id']
    to_account_id = data['to_account_id']
    amount = float(data['amount'])
    transfer_type = data.get('transfer_type', 'internal')
    description = data.get('description', '')
    
    if amount <= 0:
        return jsonify({'message': 'Transfer amount must be positive'}), 400
    
    if from_account_id == to_account_id:
        return jsonify({'message': 'Cannot transfer to the same account'}), 400
    
    # Verify from_account belongs to the user and has sufficient funds
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        
        # Verify source account
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/details/{from_account_id}",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Source account not accessible'}), response.status_code
            
        from_account = response.json()
        
        # Verify target account is valid
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/validate/{to_account_id}"
        )
        
        if not response.ok or not response.json().get('valid', False):
            return jsonify({'message': 'Target account is invalid or inactive'}), 400
            
        # Check if source account has sufficient funds
        if from_account['balance'] < amount:
            return jsonify({'message': 'Insufficient funds'}), 400
            
        # Process transfer
        with app.app_context():
            # Create transaction record
            transaction = Transaction(
                transaction_type='transfer',
                amount=amount,
                description=description,
                status='pending',
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                transfer_type=transfer_type
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            # Debit source account
            response = requests.post(
                f"{ACCOUNT_SERVICE_URL}/api/accounts/balance/update",
                json={
                    'account_id': from_account_id,
                    'amount': amount,
                    'operation': 'debit'
                }
            )
            
            if not response.ok:
                # Rollback on failure
                transaction.status = 'failed'
                db.session.commit()
                return jsonify({'message': 'Failed to debit source account'}), 500
                
            # Credit target account
            response = requests.post(
                f"{ACCOUNT_SERVICE_URL}/api/accounts/balance/update",
                json={
                    'account_id': to_account_id,
                    'amount': amount,
                    'operation': 'credit'
                }
            )
            
            if not response.ok:
                # Attempt to refund source account
                requests.post(
                    f"{ACCOUNT_SERVICE_URL}/api/accounts/balance/update",
                    json={
                        'account_id': from_account_id,
                        'amount': amount,
                        'operation': 'credit'
                    }
                )
                
                transaction.status = 'failed'
                db.session.commit()
                return jsonify({'message': 'Failed to credit target account'}), 500
                
            # Update transaction status to completed
            transaction.status = 'completed'
            db.session.commit()
            
            return jsonify({
                'message': 'Transfer completed successfully',
                'transaction': transaction.to_dict()
            }), 201
            
    except requests.RequestException:
        return jsonify({'message': 'Account service unavailable'}), 503

@app.route('/api/transactions/deposit', methods=['POST'])
@token_required
def deposit(current_user):
    """Create a deposit transaction"""
    data = request.json
    
    # Validate required fields
    required_fields = ['account_id', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    account_id = data['account_id']
    amount = float(data['amount'])
    description = data.get('description', 'Deposit')
    
    if amount <= 0:
        return jsonify({'message': 'Deposit amount must be positive'}), 400
    
    # Verify account belongs to the user
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/details/{account_id}",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Account not accessible'}), response.status_code
            
        account = response.json()
        
        # Process deposit
        with app.app_context():
            # Create transaction record
            transaction = Transaction(
                transaction_type='deposit',
                amount=amount,
                description=description,
                status='pending',
                account_id=account_id
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            # Credit account
            response = requests.post(
                f"{ACCOUNT_SERVICE_URL}/api/accounts/balance/update",
                json={
                    'account_id': account_id,
                    'amount': amount,
                    'operation': 'credit'
                }
            )
            
            if not response.ok:
                transaction.status = 'failed'
                db.session.commit()
                return jsonify({'message': 'Failed to credit account'}), 500
                
            # Update transaction status to completed
            transaction.status = 'completed'
            db.session.commit()
            
            return jsonify({
                'message': 'Deposit completed successfully',
                'transaction': transaction.to_dict()
            }), 201
            
    except requests.RequestException:
        return jsonify({'message': 'Account service unavailable'}), 503

@app.route('/api/transactions/withdraw', methods=['POST'])
@token_required
def withdraw(current_user):
    """Create a withdrawal transaction"""
    data = request.json
    
    # Validate required fields
    required_fields = ['account_id', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    account_id = data['account_id']
    amount = float(data['amount'])
    description = data.get('description', 'Withdrawal')
    
    if amount <= 0:
        return jsonify({'message': 'Withdrawal amount must be positive'}), 400
    
    # Verify account belongs to the user and has sufficient funds
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/details/{account_id}",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Account not accessible'}), response.status_code
            
        account = response.json()
        
        # Check if account has sufficient funds
        if account['balance'] < amount:
            return jsonify({'message': 'Insufficient funds'}), 400
            
        # Process withdrawal
        with app.app_context():
            # Create transaction record
            transaction = Transaction(
                transaction_type='withdrawal',
                amount=amount,
                description=description,
                status='pending',
                account_id=account_id
            )
            
            db.session.add(transaction)
            db.session.commit()
            
            # Debit account
            response = requests.post(
                f"{ACCOUNT_SERVICE_URL}/api/accounts/balance/update",
                json={
                    'account_id': account_id,
                    'amount': amount,
                    'operation': 'debit'
                }
            )
            
            if not response.ok:
                transaction.status = 'failed'
                db.session.commit()
                return jsonify({'message': 'Failed to debit account'}), 500
                
            # Update transaction status to completed
            transaction.status = 'completed'
            db.session.commit()
            
            return jsonify({
                'message': 'Withdrawal completed successfully',
                'transaction': transaction.to_dict()
            }), 201
            
    except requests.RequestException:
        return jsonify({'message': 'Account service unavailable'}), 503

@app.route('/api/transactions/record', methods=['POST'])
def record_transaction():
    """Record a transaction (internal use by other services)"""
    # This endpoint should be protected in production but is left open for the demo
    data = request.json
    
    # Validate required fields
    required_fields = ['transaction_type', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    transaction_type = data['transaction_type']
    amount = float(data['amount'])
    
    # Additional validation based on transaction type
    if transaction_type in ['deposit', 'withdrawal'] and 'account_id' not in data:
        return jsonify({'message': 'account_id is required for deposit/withdrawal'}), 400
        
    if transaction_type == 'transfer' and ('from_account_id' not in data or 'to_account_id' not in data):
        return jsonify({'message': 'from_account_id and to_account_id are required for transfer'}), 400
    
    # Create transaction record
    with app.app_context():
        transaction = Transaction(
            transaction_type=transaction_type,
            amount=amount,
            description=data.get('description', ''),
            status=data.get('status', 'completed')
        )
        
        if transaction_type in ['deposit', 'withdrawal']:
            transaction.account_id = data['account_id']
        elif transaction_type == 'transfer':
            transaction.from_account_id = data['from_account_id']
            transaction.to_account_id = data['to_account_id']
            transaction.transfer_type = data.get('transfer_type', 'internal')
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction recorded successfully',
            'transaction': transaction.to_dict()
        }), 201

@app.route('/api/transactions/all', methods=['GET'])
@token_required
@admin_required
def get_all_transactions(current_user):
    """Get all transactions (admin only)"""
    with app.app_context():
        transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
        return jsonify({
            'transactions': [transaction.to_dict() for transaction in transactions]
        }), 200

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8003)