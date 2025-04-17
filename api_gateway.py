import os
import json
import logging
import requests
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Microservice URLs
AUTH_SERVICE_URL = "http://0.0.0.0:8001"
ACCOUNT_SERVICE_URL = "http://0.0.0.0:8002"
TRANSACTION_SERVICE_URL = "http://0.0.0.0:8003"
REPORTING_SERVICE_URL = "http://0.0.0.0:8004"

# Helper functions
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        
        # Verify admin role
        headers = {'Authorization': f'Bearer {session["token"]}'}
        response = requests.get(f"{AUTH_SERVICE_URL}/api/auth/verify_admin", headers=headers)
        
        if not response.ok or not response.json().get('is_admin'):
            flash('You do not have admin privileges', 'danger')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

def make_auth_request(method, endpoint, data=None, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    url = f"{AUTH_SERVICE_URL}/api/auth/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response
    except requests.RequestException as e:
        logger.error(f"Auth service request failed: {e}")
        return None

def make_account_request(method, endpoint, data=None, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    url = f"{ACCOUNT_SERVICE_URL}/api/accounts/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response
    except requests.RequestException as e:
        logger.error(f"Account service request failed: {e}")
        return None

def make_transaction_request(method, endpoint, data=None, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    url = f"{TRANSACTION_SERVICE_URL}/api/transactions/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response
    except requests.RequestException as e:
        logger.error(f"Transaction service request failed: {e}")
        return None

def make_reporting_request(method, endpoint, data=None, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    url = f"{REPORTING_SERVICE_URL}/api/reports/{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        return response
    except requests.RequestException as e:
        logger.error(f"Reporting service request failed: {e}")
        return None

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        response = make_auth_request('POST', 'login', {
            'username': username,
            'password': password
        })
        
        if response and response.status_code == 200:
            data = response.json()
            session['token'] = data.get('token')
            session['user_id'] = data.get('user_id')
            session['username'] = username
            session['role'] = data.get('role', 'customer')
            
            flash('You have been logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        response = make_auth_request('POST', 'register', {
            'username': username,
            'email': email,
            'password': password
        })
        
        if response and response.status_code == 201:
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            error_data = response.json() if response else {"message": "Service unavailable"}
            flash(f'Registration failed: {error_data.get("message", "Unknown error")}', 'danger')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user profile info
    profile_response = make_auth_request('GET', f'users/profile', token=session['token'])
    profile_data = profile_response.json() if profile_response and profile_response.status_code == 200 else {}
    
    # Get account summary
    accounts_response = make_account_request('GET', 'list', token=session['token'])
    accounts_data = accounts_response.json() if accounts_response and accounts_response.status_code == 200 else {"accounts": []}
    
    # Get recent transactions
    transactions_response = make_transaction_request('GET', 'recent', token=session['token'])
    transactions_data = transactions_response.json() if transactions_response and transactions_response.status_code == 200 else {"transactions": []}
    
    return render_template(
        'dashboard.html',
        profile=profile_data,
        accounts=accounts_data.get('accounts', []),
        transactions=transactions_data.get('transactions', [])
    )

# Account Routes
@app.route('/accounts')
@login_required
def accounts():
    response = make_account_request('GET', 'list', token=session['token'])
    
    if response and response.status_code == 200:
        data = response.json()
        return render_template('accounts.html', accounts=data.get('accounts', []))
    else:
        flash('Failed to retrieve accounts', 'danger')
        return render_template('accounts.html', accounts=[])

@app.route('/accounts/create', methods=['GET', 'POST'])
@login_required
def create_account():
    if request.method == 'POST':
        account_type = request.form.get('account_type')
        initial_deposit = request.form.get('initial_deposit')
        
        response = make_account_request('POST', 'create', {
            'account_type': account_type,
            'initial_deposit': float(initial_deposit) if initial_deposit else 0
        }, session['token'])
        
        if response and response.status_code == 201:
            flash('Account created successfully', 'success')
            return redirect(url_for('accounts'))
        else:
            error_data = response.json() if response else {"message": "Service unavailable"}
            flash(f'Failed to create account: {error_data.get("message", "Unknown error")}', 'danger')
    
    return render_template('account_create.html')

@app.route('/accounts/<account_id>')
@login_required
def view_account(account_id):
    response = make_account_request('GET', f'details/{account_id}', token=session['token'])
    
    if response and response.status_code == 200:
        account_data = response.json()
        
        # Get recent transactions for this account
        tx_response = make_transaction_request('GET', f'account/{account_id}', token=session['token'])
        transactions = tx_response.json().get('transactions', []) if tx_response and tx_response.status_code == 200 else []
        
        return render_template('account_view.html', account=account_data, transactions=transactions)
    else:
        flash('Failed to retrieve account details', 'danger')
        return redirect(url_for('accounts'))

@app.route('/accounts/<account_id>/close', methods=['GET', 'POST'])
@login_required
def close_account(account_id):
    if request.method == 'POST':
        confirmation = request.form.get('confirmation')
        
        if confirmation == 'CLOSE':
            response = make_account_request('DELETE', f'close/{account_id}', token=session['token'])
            
            if response and response.status_code == 200:
                flash('Account closed successfully', 'success')
                return redirect(url_for('accounts'))
            else:
                error_data = response.json() if response else {"message": "Service unavailable"}
                flash(f'Failed to close account: {error_data.get("message", "Unknown error")}', 'danger')
        else:
            flash('Invalid confirmation text', 'danger')
    
    # Get account details
    response = make_account_request('GET', f'details/{account_id}', token=session['token'])
    account_data = response.json() if response and response.status_code == 200 else {}
    
    return render_template('account_close.html', account=account_data)

# Transaction Routes
@app.route('/transactions')
@login_required
def transactions():
    response = make_transaction_request('GET', 'list', token=session['token'])
    
    if response and response.status_code == 200:
        data = response.json()
        return render_template('transactions.html', transactions=data.get('transactions', []))
    else:
        flash('Failed to retrieve transactions', 'danger')
        return render_template('transactions.html', transactions=[])

@app.route('/transactions/<transaction_id>')
@login_required
def transaction_detail(transaction_id):
    response = make_transaction_request('GET', f'details/{transaction_id}', token=session['token'])
    
    if response and response.status_code == 200:
        transaction_data = response.json()
        return render_template('transaction_detail.html', transaction=transaction_data)
    else:
        flash('Failed to retrieve transaction details', 'danger')
        return redirect(url_for('transactions'))

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        from_account_id = request.form.get('from_account')
        to_account_id = request.form.get('to_account')
        amount = request.form.get('amount')
        transfer_type = request.form.get('transfer_type')
        description = request.form.get('description', '')
        
        response = make_transaction_request('POST', 'transfer', {
            'from_account_id': from_account_id,
            'to_account_id': to_account_id,
            'amount': float(amount),
            'transfer_type': transfer_type,
            'description': description
        }, session['token'])
        
        if response and response.status_code == 201:
            flash('Transfer completed successfully', 'success')
            return redirect(url_for('transactions'))
        else:
            error_data = response.json() if response else {"message": "Service unavailable"}
            flash(f'Transfer failed: {error_data.get("message", "Unknown error")}', 'danger')
    
    # Get user accounts for dropdown
    accounts_response = make_account_request('GET', 'list', token=session['token'])
    accounts = accounts_response.json().get('accounts', []) if accounts_response and accounts_response.status_code == 200 else []
    
    return render_template('transfer.html', accounts=accounts)

# Report Routes
@app.route('/reports/account/<account_id>')
@login_required
def account_report(account_id):
    response = make_reporting_request('GET', f'account/{account_id}', token=session['token'])
    
    if response and response.status_code == 200:
        report_data = response.json()
        
        # Get basic account details
        account_response = make_account_request('GET', f'details/{account_id}', token=session['token'])
        account_data = account_response.json() if account_response and account_response.status_code == 200 else {}
        
        return render_template('account_report.html', report=report_data, account=account_data)
    else:
        flash('Failed to generate account report', 'danger')
        return redirect(url_for('accounts'))

@app.route('/reports/transactions')
@login_required
def transaction_report():
    start_date = request.args.get('start_date', (datetime.now().replace(day=1)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
    
    response = make_reporting_request('GET', 'transactions', {
        'start_date': start_date,
        'end_date': end_date
    }, session['token'])
    
    if response and response.status_code == 200:
        report_data = response.json()
        return render_template('transaction_report.html', report=report_data, start_date=start_date, end_date=end_date)
    else:
        flash('Failed to generate transaction report', 'danger')
        return render_template('transaction_report.html', report={"transactions": [], "summary": {}}, start_date=start_date, end_date=end_date)

# Health check endpoint
@app.route('/health')
def health_check():
    services_status = {
        "api_gateway": "healthy",
        "auth_service": "unknown",
        "account_service": "unknown",
        "transaction_service": "unknown",
        "reporting_service": "unknown"
    }
    
    # Check auth service
    try:
        auth_response = requests.get(f"{AUTH_SERVICE_URL}/api/health")
        services_status["auth_service"] = "healthy" if auth_response.status_code == 200 else "unhealthy"
    except:
        services_status["auth_service"] = "unreachable"
    
    # Check account service
    try:
        account_response = requests.get(f"{ACCOUNT_SERVICE_URL}/api/health")
        services_status["account_service"] = "healthy" if account_response.status_code == 200 else "unhealthy"
    except:
        services_status["account_service"] = "unreachable"
    
    # Check transaction service
    try:
        transaction_response = requests.get(f"{TRANSACTION_SERVICE_URL}/api/health")
        services_status["transaction_service"] = "healthy" if transaction_response.status_code == 200 else "unhealthy"
    except:
        services_status["transaction_service"] = "unreachable"
    
    # Check reporting service
    try:
        reporting_response = requests.get(f"{REPORTING_SERVICE_URL}/api/health")
        services_status["reporting_service"] = "healthy" if reporting_response.status_code == 200 else "unhealthy"
    except:
        services_status["reporting_service"] = "unreachable"
    
    return jsonify(services_status)

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
