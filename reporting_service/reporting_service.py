import os
import logging
import requests
import jwt
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from reporting_service.reporting_models import db, Report

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
app.config["JWT_SECRET_KEY"] = os.environ.get("SESSION_SECRET", "reporting_service_secret_key")

# Initialize extensions
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Service URLs
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:8001")
ACCOUNT_SERVICE_URL = os.environ.get("ACCOUNT_SERVICE_URL", "http://localhost:8002")
TRANSACTION_SERVICE_URL = os.environ.get("TRANSACTION_SERVICE_URL", "http://localhost:8003")

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

def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

def filter_transactions_by_date(transactions, start_date, end_date):
    """Filter transactions by date range"""
    filtered = []
    for transaction in transactions:
        transaction_date = datetime.fromisoformat(transaction['timestamp'].replace('Z', '+00:00'))
        if start_date <= transaction_date.date() <= end_date:
            filtered.append(transaction)
    return filtered

def calculate_summary(transactions):
    """Calculate summary statistics for transactions"""
    summary = {
        'total_count': len(transactions),
        'total_amount': sum(t['amount'] for t in transactions),
        'by_type': {},
    }
    
    # Count by transaction type
    for t in transactions:
        t_type = t['transaction_type']
        if t_type not in summary['by_type']:
            summary['by_type'][t_type] = {
                'count': 0,
                'amount': 0
            }
        summary['by_type'][t_type]['count'] += 1
        summary['by_type'][t_type]['amount'] += t['amount']
    
    return summary

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'reporting-service'}), 200

@app.route('/api/reports/account/<account_id>', methods=['GET'])
@token_required
def account_report(current_user, account_id):
    """Generate report for specific account"""
    # Get parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Parse dates
    start_date = parse_date(start_date_str) if start_date_str else (datetime.now() - timedelta(days=30)).date()
    end_date = parse_date(end_date_str) if end_date_str else datetime.now().date()
    
    # Verify account access
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/details/{account_id}",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to access account'}), response.status_code
        
        account = response.json()
            
    except requests.RequestException:
        return jsonify({'message': 'Account service unavailable'}), 503
    
    # Get transactions for this account
    try:
        response = requests.get(
            f"{TRANSACTION_SERVICE_URL}/api/transactions/account/{account_id}",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to retrieve transactions'}), response.status_code
            
        transactions = response.json().get('transactions', [])
        
    except requests.RequestException:
        return jsonify({'message': 'Transaction service unavailable'}), 503
    
    # Filter transactions by date
    filtered_transactions = filter_transactions_by_date(transactions, start_date, end_date)
    
    # Calculate summary statistics
    summary = calculate_summary(filtered_transactions)
    
    # Create report
    report_data = {
        'account': account,
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'summary': summary,
        'transactions': filtered_transactions
    }
    
    # Save report
    with app.app_context():
        report = Report(
            user_id=current_user['user_id'],
            report_type='account',
            title=f"Account Report: {account['account_number']}",
            description=f"Account activity report from {start_date.isoformat()} to {end_date.isoformat()}",
            parameters={
                'account_id': account_id,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            report_data=report_data
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'report': report.to_dict()
        }), 200

@app.route('/api/reports/transactions', methods=['GET'])
@token_required
def transaction_report(current_user):
    """Generate transaction report for user's accounts"""
    # Get parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Parse dates
    start_date = parse_date(start_date_str) if start_date_str else (datetime.now() - timedelta(days=30)).date()
    end_date = parse_date(end_date_str) if end_date_str else datetime.now().date()
    
    # Get all accounts for the user
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/list",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to retrieve accounts'}), response.status_code
            
        accounts = response.json().get('accounts', [])
        
    except requests.RequestException:
        return jsonify({'message': 'Account service unavailable'}), 503
    
    # Get all transactions for the user
    try:
        response = requests.get(
            f"{TRANSACTION_SERVICE_URL}/api/transactions/list",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to retrieve transactions'}), response.status_code
            
        transactions = response.json().get('transactions', [])
        
    except requests.RequestException:
        return jsonify({'message': 'Transaction service unavailable'}), 503
    
    # Filter transactions by date
    filtered_transactions = filter_transactions_by_date(transactions, start_date, end_date)
    
    # Calculate summary statistics
    summary = calculate_summary(filtered_transactions)
    
    # Create report
    report_data = {
        'accounts': accounts,
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'summary': summary,
        'transactions': filtered_transactions
    }
    
    # Save report
    with app.app_context():
        report = Report(
            user_id=current_user['user_id'],
            report_type='transaction',
            title=f"Transaction Report",
            description=f"Transaction report from {start_date.isoformat()} to {end_date.isoformat()}",
            parameters={
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            report_data=report_data
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'report': report.to_dict()
        }), 200

@app.route('/api/reports/system', methods=['GET'])
@token_required
@admin_required
def system_report(current_user):
    """Generate system-wide report (admin only)"""
    # Get parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Parse dates
    start_date = parse_date(start_date_str) if start_date_str else (datetime.now() - timedelta(days=30)).date()
    end_date = parse_date(end_date_str) if end_date_str else datetime.now().date()
    
    # Get all users
    try:
        token = request.headers.get('Authorization').split(' ')[1]
        response = requests.get(
            f"{AUTH_SERVICE_URL}/api/auth/users",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to retrieve users'}), response.status_code
            
        users = response.json().get('users', [])
        
    except requests.RequestException:
        return jsonify({'message': 'Auth service unavailable'}), 503
    
    # Get all accounts
    try:
        response = requests.get(
            f"{ACCOUNT_SERVICE_URL}/api/accounts/all",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to retrieve accounts'}), response.status_code
            
        accounts = response.json().get('accounts', [])
        
    except requests.RequestException:
        return jsonify({'message': 'Account service unavailable'}), 503
    
    # Get all transactions
    try:
        response = requests.get(
            f"{TRANSACTION_SERVICE_URL}/api/transactions/all",
            headers={'Authorization': f'Bearer {token}'}
        )
        
        if not response.ok:
            return jsonify({'message': 'Failed to retrieve transactions'}), response.status_code
            
        transactions = response.json().get('transactions', [])
        
    except requests.RequestException:
        return jsonify({'message': 'Transaction service unavailable'}), 503
    
    # Filter transactions by date
    filtered_transactions = filter_transactions_by_date(transactions, start_date, end_date)
    
    # Calculate summary statistics
    transaction_summary = calculate_summary(filtered_transactions)
    
    # Calculate additional system stats
    system_stats = {
        'total_users': len(users),
        'total_accounts': len(accounts),
        'total_balance': sum(a['balance'] for a in accounts),
        'active_accounts': sum(1 for a in accounts if a['status'] == 'active'),
        'closed_accounts': sum(1 for a in accounts if a['status'] == 'closed'),
        'account_types': {}
    }
    
    # Count by account type
    for a in accounts:
        a_type = a['account_type']
        if a_type not in system_stats['account_types']:
            system_stats['account_types'][a_type] = {
                'count': 0,
                'balance': 0
            }
        system_stats['account_types'][a_type]['count'] += 1
        system_stats['account_types'][a_type]['balance'] += a['balance']
    
    # Create report
    report_data = {
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'system_stats': system_stats,
        'transaction_summary': transaction_summary
    }
    
    # Save report
    with app.app_context():
        report = Report(
            user_id=current_user['user_id'],
            report_type='system',
            title=f"System Report",
            description=f"System-wide report from {start_date.isoformat()} to {end_date.isoformat()}",
            parameters={
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            report_data=report_data
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'report': report.to_dict()
        }), 200

@app.route('/api/reports/list', methods=['GET'])
@token_required
def list_reports(current_user):
    """List reports for the current user"""
    with app.app_context():
        reports = Report.query.filter_by(user_id=current_user['user_id']).order_by(Report.created_at.desc()).all()
        return jsonify({
            'reports': [report.to_dict() for report in reports]
        }), 200

@app.route('/api/reports/details/<report_id>', methods=['GET'])
@token_required
def report_details(current_user, report_id):
    """Get details of a specific report"""
    with app.app_context():
        report = Report.query.filter_by(id=report_id).first()
        
        if not report:
            return jsonify({'message': 'Report not found'}), 404
        
        # Check if the report belongs to the current user or user is admin
        if report.user_id != current_user['user_id'] and current_user['role'] != 'admin':
            return jsonify({'message': 'Access denied'}), 403
            
        return jsonify(report.to_dict()), 200

@app.route('/api/reports/all', methods=['GET'])
@token_required
@admin_required
def all_reports(current_user):
    """Get all reports (admin only)"""
    with app.app_context():
        reports = Report.query.order_by(Report.created_at.desc()).all()
        return jsonify({
            'reports': [report.to_dict() for report in reports]
        }), 200

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8004)