import os
import json
import logging
import requests
from datetime import datetime, timedelta
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

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Sessions last for 1 day
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

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
            
        # Verify token is still valid by making a request to auth service
        try:
            verify_response = make_auth_request('GET', 'verify_token', token=session['token'])
            
            # If token verification fails, clear session and redirect to login
            if not verify_response or verify_response.status_code != 200:
                logger.warning(f"Invalid token detected. Forcing logout. Response: {verify_response}")
                session.clear()
                flash('Your session has expired. Please log in again.', 'warning')
                return redirect(url_for('login'))
                
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            # Allow the request to continue even if auth service is down temporarily
            # This prevents users from being locked out if auth service has a brief outage
            
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

def make_auth_request(method, endpoint, data=None, token=None, params=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    # Try to get service URL from Consul
    auth_service_url = get_service_url("auth-service")
    
    # Fall back to hardcoded URL if Consul fails
    if not auth_service_url:
        logger.warning("Auth service not found in Consul, falling back to direct URL")
        auth_service_url = AUTH_SERVICE_URL

    url = f"{auth_service_url}/api/auth/{endpoint}"
    logger.debug(f"Making {method} request to {url}")

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        logger.debug(f"Response status: {response.status_code}")
        return response
    except requests.RequestException as e:
        logger.error(f"Auth service request failed: {e}")
        return None

import consul

CONSUL_HOST = os.environ.get("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.environ.get("CONSUL_PORT", 8500))

consul_client = consul.Consul(host=CONSUL_HOST, port=CONSUL_PORT)

def get_service_url(service_name):
    """Get service URL from Consul or fall back to hardcoded URL."""
    try:
        index, data = consul_client.health.service(service_name, passing=True)
        if data:
            service = data[0]['Service']
            address = service['Address']
            port = service['Port']
            return f"http://{address}:{port}"
        else:
            logger.warning(f"No healthy instances of {service_name} found in Consul")
            # Fall back to hardcoded URLs
            if service_name == "auth-service":
                return AUTH_SERVICE_URL
            elif service_name == "account-service":
                return ACCOUNT_SERVICE_URL
            elif service_name == "transaction-service":
                return TRANSACTION_SERVICE_URL
            elif service_name == "reporting-service":
                return REPORTING_SERVICE_URL
            else:
                return None
    except Exception as e:
        logger.error(f"Error querying Consul for {service_name}: {e}")
        # Fall back to hardcoded URLs
        if service_name == "auth-service":
            return AUTH_SERVICE_URL
        elif service_name == "account-service":
            return ACCOUNT_SERVICE_URL
        elif service_name == "transaction-service":
            return TRANSACTION_SERVICE_URL
        elif service_name == "reporting-service":
            return REPORTING_SERVICE_URL
        else:
            return None

def make_account_request(method, endpoint, data=None, token=None, params=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    # Try to get service URL from Consul
    account_service_url = get_service_url("account-service")
    
    # Fall back to hardcoded URL if Consul fails
    if not account_service_url:
        logger.warning("Account service not found in Consul, falling back to direct URL")
        account_service_url = ACCOUNT_SERVICE_URL

    url = f"{account_service_url}/api/accounts/{endpoint}"
    logger.debug(f"Making {method} request to {url}")

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        logger.debug(f"Response status: {response.status_code}")
        return response
    except requests.RequestException as e:
        logger.error(f"Account service request failed: {e}")
        return None

def make_transaction_request(method, endpoint, data=None, token=None, params=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    # Try to get service URL from Consul
    transaction_service_url = get_service_url("transaction-service")
    
    # Fall back to hardcoded URL if Consul fails
    if not transaction_service_url:
        logger.warning("Transaction service not found in Consul, falling back to direct URL")
        transaction_service_url = TRANSACTION_SERVICE_URL

    url = f"{transaction_service_url}/api/transactions/{endpoint}"
    logger.debug(f"Making {method} request to {url}")

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        logger.debug(f"Response status: {response.status_code}")
        return response
    except requests.RequestException as e:
        logger.error(f"Transaction service request failed: {e}")
        return None

def make_reporting_request(method, endpoint, data=None, token=None, params=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    # Try to get service URL from Consul
    reporting_service_url = get_service_url("reporting-service")
    
    # Fall back to hardcoded URL if Consul fails
    if not reporting_service_url:
        logger.warning("Reporting service not found in Consul, falling back to direct URL")
        reporting_service_url = REPORTING_SERVICE_URL

    url = f"{reporting_service_url}/api/reports/{endpoint}"
    logger.debug(f"Making {method} request to {url}")

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params if params else data)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        logger.debug(f"Response status: {response.status_code}")
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
    """Handle user login"""
    # Check if user is already logged in
    if 'token' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Both username and password are required', 'danger')
            return render_template('login.html')
            
        try:
            # Log the request for debugging
            logger.debug(f"Making login request for user: {username}")
            
            response = make_auth_request('POST', 'login', {
                'username': username,
                'password': password
            })
            
            if response and response.status_code == 200:
                data = response.json()
                # Store auth data in session
                session['token'] = data.get('token')
                session['user_id'] = data.get('user_id')
                session['username'] = username
                session['role'] = data.get('role', 'customer')
                
                # Set session permanent to extend lifetime
                session.permanent = True
                
                flash('You have been logged in successfully', 'success')
                return redirect(url_for('dashboard'))
            elif response and response.status_code == 401:
                flash('Invalid username or password', 'danger')
            elif response:
                error_data = response.json() if response and hasattr(response, 'json') else {}
                flash(f'Login failed: {error_data.get("message", "Unknown error")}', 'danger')
            else:
                flash('Authentication service is currently unavailable. Please try again later.', 'danger')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again later.', 'danger')
    
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

# Add profile route
@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    try:
        # Get user profile info from auth service with additional error handling
        profile_response = make_auth_request('GET', 'users/profile', token=session['token'])
        
        if profile_response and profile_response.status_code == 200:
            profile_data = profile_response.json()
            logger.debug(f"Successfully loaded profile data for user: {session.get('username')}")
            return render_template('profile.html', profile=profile_data)
        elif profile_response and profile_response.status_code == 401:
            # Token is invalid/expired - clear session and redirect to login
            logger.warning("Invalid token detected in profile route")
            session.clear()
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('login'))
        else:
            # Other API error
            error_msg = "Failed to load profile information"
            if profile_response and hasattr(profile_response, 'json'):
                try:
                    error_data = profile_response.json()
                    if 'message' in error_data:
                        error_msg = error_data['message']
                except:
                    pass
            
            flash(error_msg, 'danger')
            return redirect(url_for('dashboard'))
    except Exception as e:
        logger.error(f"Error loading profile: {str(e)}")
        flash('An error occurred while loading your profile. Please try again.', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Validate password if provided
    if password and password != confirm_password:
        flash('Passwords do not match', 'danger')
        return redirect(url_for('profile'))
    
    # Prepare data for the update
    data = {}
    if email:
        data['email'] = email
    if password:
        data['password'] = password
    
    # Send update request to auth service
    response = make_auth_request('PUT', 'users/profile', data=data, token=session['token'])
    
    if response and response.status_code == 200:
        flash('Profile updated successfully', 'success')
    else:
        error_data = response.json() if response else {"message": "Service unavailable"}
        flash(f'Failed to update profile: {error_data.get("message", "Unknown error")}', 'danger')
    
    return redirect(url_for('profile'))

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
    """Comprehensive health check endpoint"""
    services_status = {
        "api_gateway": "healthy"
    }
    
    # Define service mappings for cleaner code
    service_mappings = {
        "auth-service": {"key": "auth_service", "url": AUTH_SERVICE_URL},
        "account-service": {"key": "account_service", "url": ACCOUNT_SERVICE_URL},
        "transaction-service": {"key": "transaction_service", "url": TRANSACTION_SERVICE_URL},
        "reporting-service": {"key": "reporting_service", "url": REPORTING_SERVICE_URL}
    }
    
    all_healthy = True
    
    # Check each service with improved error handling
    for service_name, service_info in service_mappings.items():
        key = service_info["key"]
        direct_url = service_info["url"]
        
        # First try consul service discovery
        service_url = get_service_url(service_name)
        
        # If consul fails, use direct URL
        if not service_url:
            service_url = direct_url
            
        if service_url:
            try:
                health_response = requests.get(f"{service_url}/api/health", timeout=2)
                if health_response.status_code == 200:
                    services_status[key] = "healthy"
                else:
                    services_status[key] = "unhealthy"
                    all_healthy = False
                    logger.warning(f"Service {service_name} returned unhealthy status: {health_response.status_code}")
            except requests.RequestException as e:
                services_status[key] = "unreachable"
                all_healthy = False
                logger.error(f"Error reaching {service_name}: {str(e)}")
        else:
            services_status[key] = "unknown"
            all_healthy = False
            logger.error(f"Could not resolve URL for {service_name}")
    
    return jsonify({
        "status": "healthy" if all_healthy else "degraded",
        "services": services_status,
        "timestamp": datetime.now().isoformat()
    }), 200

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
