import os
import json
import logging
import requests
from flask import Flask, request, jsonify, session, redirect, url_for, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "api_gateway_secret_key")
app.config["JWT_SECRET_KEY"] = os.environ.get("SESSION_SECRET", "api_gateway_secret_key")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Custom Jinja filters
@app.template_filter('format_date')
def format_date(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a date time to a readable format"""
    if not value:
        return ''
    if isinstance(value, str):
        # Try to parse the string
        try:
            from datetime import datetime
            if 'T' in value:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            else:
                # Assuming yyyy-mm-dd format
                value = datetime.strptime(value[:10], '%Y-%m-%d')
        except:
            return value
    try:
        return value.strftime(format)
    except:
        return value

# Service URLs - now using environment variables for service discovery
AUTH_SERVICE_URL = os.environ.get("AUTH_SERVICE_URL", "http://localhost:8001")
ACCOUNT_SERVICE_URL = os.environ.get("ACCOUNT_SERVICE_URL", "http://localhost:8002")
TRANSACTION_SERVICE_URL = os.environ.get("TRANSACTION_SERVICE_URL", "http://localhost:8003")
REPORTING_SERVICE_URL = os.environ.get("REPORTING_SERVICE_URL", "http://localhost:8004")

# Define User class for Flask-Login
class User:
    def __init__(self, user_data, token):
        self.id = user_data['user_id']
        self.username = user_data['username']
        self.email = user_data.get('email', '')
        self.role = user_data['role']
        self.token = token
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.id

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    if 'token' not in session:
        return None

    try:
        response = requests.get(
            f"{AUTH_SERVICE_URL}/api/auth/verify_token",
            headers={'Authorization': f'Bearer {session["token"]}'}
        )

        if response.ok:
            user_data = response.json()
            return User(user_data, session["token"])

    except requests.RequestException:
        logger.error("Failed to verify token with auth service")

    return None

# Helper functions for making service requests
def make_service_request(service_url, endpoint, method='GET', data=None, params=None, headers=None):
    """Helper function to make requests to microservices"""
    url = f"{service_url}{endpoint}"

    # Add authentication token if available
    if current_user and hasattr(current_user, 'token') and current_user.token:
        if not headers:
            headers = {}
        headers['Authorization'] = f'Bearer {current_user.token}'

    try:
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return {'error': 'Unsupported HTTP method'}, 400

        # Try to parse as JSON
        try:
            result = response.json()
        except:
            result = {'data': response.text}

        return result, response.status_code

    except requests.RequestException as e:
        logger.error(f"Service request failed: {str(e)}")
        return {'error': 'Service unavailable'}, 503

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', error='Username and password are required')

        # Authenticate with auth service
        response, status_code = make_service_request(
            AUTH_SERVICE_URL,
            '/api/auth/login',
            method='POST',
            data={'username': username, 'password': password}
        )

        if status_code != 200:
            return render_template('login.html', error=response.get('message', 'Authentication failed'))

        # Create user object and login
        user = User(response, response['token'])
        login_user(user)
        session['token'] = response['token']

        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('token', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password:
            return render_template('register.html', error='All fields are required')

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        # Register with auth service
        response, status_code = make_service_request(
            AUTH_SERVICE_URL,
            '/api/auth/register',
            method='POST',
            data={'username': username, 'email': email, 'password': password}
        )

        if status_code != 201:
            return render_template('register.html', error=response.get('message', 'Registration failed'))

        return redirect(url_for('login', registered=True))

    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get accounts
    accounts_response, accounts_status = make_service_request(
        ACCOUNT_SERVICE_URL,
        '/api/accounts/list'
    )

    # Get recent transactions
    transactions_response, transactions_status = make_service_request(
        TRANSACTION_SERVICE_URL,
        '/api/transactions/recent'
    )

    accounts = accounts_response.get('accounts', []) if accounts_status == 200 else []
    transactions = transactions_response.get('transactions', []) if transactions_status == 200 else []

    return render_template(
        'dashboard.html',
        accounts=accounts,
        transactions=transactions
    )

@app.route('/accounts')
@login_required
def accounts():
    # Get accounts
    response, status = make_service_request(
        ACCOUNT_SERVICE_URL,
        '/api/accounts/list'
    )

    accounts = response.get('accounts', []) if status == 200 else []

    return render_template('accounts.html', accounts=accounts)

@app.route('/accounts/create', methods=['GET', 'POST'])
@login_required
def create_account():
    if request.method == 'POST':
        account_type = request.form.get('account_type')
        initial_deposit = request.form.get('initial_deposit', 0)

        if not account_type:
            return render_template('create_account.html', error='Account type is required')

        # Create account with account service
        response, status = make_service_request(
            ACCOUNT_SERVICE_URL,
            '/api/accounts/create',
            method='POST',
            data={'account_type': account_type, 'initial_deposit': float(initial_deposit)}
        )

        if status != 201:
            return render_template('create_account.html', error=response.get('message', 'Failed to create account'))

        return redirect(url_for('accounts'))

    return render_template('create_account.html')

@app.route('/accounts/<account_id>')
@login_required
def view_account(account_id):
    # Get account details
    account_response, account_status = make_service_request(
        ACCOUNT_SERVICE_URL,
        f'/api/accounts/details/{account_id}'
    )

    # Get account transactions
    transactions_response, transactions_status = make_service_request(
        TRANSACTION_SERVICE_URL,
        f'/api/transactions/account/{account_id}'
    )

    if account_status != 200:
        return render_template('error.html', error=account_response.get('message', 'Failed to retrieve account'))

    account = account_response
    transactions = transactions_response.get('transactions', []) if transactions_status == 200 else []

    return render_template(
        'account_details.html',
        account=account,
        transactions=transactions
    )

@app.route('/accounts/<account_id>/close', methods=['POST'])
@login_required
def close_account(account_id):
    # Close account with account service
    response, status = make_service_request(
        ACCOUNT_SERVICE_URL,
        f'/api/accounts/close/{account_id}',
        method='DELETE'
    )

    if status != 200:
        # Return JSON response for AJAX requests
        return jsonify({'success': False, 'message': response.get('message', 'Failed to close account')}), status

    return jsonify({'success': True})

@app.route('/transactions')
@login_required
def transactions():
    # Get all transactions
    response, status = make_service_request(
        TRANSACTION_SERVICE_URL,
        '/api/transactions/list'
    )

    transactions = response.get('transactions', []) if status == 200 else []

    return render_template('transactions.html', transactions=transactions)

@app.route('/transactions/<transaction_id>')
@login_required
def transaction_detail(transaction_id):
    # Get transaction details
    response, status = make_service_request(
        TRANSACTION_SERVICE_URL,
        f'/api/transactions/details/{transaction_id}'
    )

    if status != 200:
        return render_template('error.html', error=response.get('message', 'Failed to retrieve transaction'))

    transaction = response

    return render_template('transaction_details.html', transaction=transaction)
    
@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html')

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    data = {'email': email}
    if password:
        data['password'] = password
    
    # Update profile with auth service
    response, status = make_service_request(
        AUTH_SERVICE_URL,
        '/api/auth/update_profile',
        method='POST',
        data=data
    )
    
    if status != 200:
        return render_template('profile.html', error=response.get('message', 'Failed to update profile'))
    
    return redirect(url_for('profile'))

@app.route('/settings')
@login_required
def settings():
    """User settings page"""
    # Default settings
    user_settings = {
        'email_notifications': True,
        'login_alerts': True,
        'transaction_notifications': True,
        'theme': 'dark',
        'default_view': 'dashboard',
        'two_factor_auth': False
    }
    
    # Here you would normally fetch user settings from a database
    # For demonstration purposes, we're using default settings
    
    return render_template('settings.html', settings=user_settings)

@app.route('/settings/update', methods=['POST'])
@login_required
def update_settings():
    """Update user settings"""
    # Get form data
    email_notifications = 'email_notifications' in request.form
    login_alerts = 'login_alerts' in request.form
    transaction_notifications = 'transaction_notifications' in request.form
    theme = request.form.get('theme', 'dark')
    default_view = request.form.get('default_view', 'dashboard')
    two_factor_auth = 'two_factor_auth' in request.form
    
    # Here you would normally save these settings to a database
    # For demonstration purposes, we're just redirecting with success message
    
    # Store updated settings in session for persistence during the session
    session['user_settings'] = {
        'email_notifications': email_notifications,
        'login_alerts': login_alerts,
        'transaction_notifications': transaction_notifications,
        'theme': theme,
        'default_view': default_view,
        'two_factor_auth': two_factor_auth
    }
    
    # Update the session to reflect saved settings
    user_settings = session.get('user_settings', {})
    
    return render_template(
        'settings.html', 
        settings=user_settings,
        success='Settings updated successfully'
    )

@app.route('/transactions/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'POST':
        from_account_id = request.form.get('from_account_id')
        to_account_id = request.form.get('to_account_id')
        amount = request.form.get('amount')
        description = request.form.get('description', '')

        if not from_account_id or not to_account_id or not amount:
            return render_template('transfer.html', error='All fields are required')

        # Create transfer with transaction service
        response, status = make_service_request(
            TRANSACTION_SERVICE_URL,
            '/api/transactions/transfer',
            method='POST',
            data={
                'from_account_id': from_account_id,
                'to_account_id': to_account_id,
                'amount': float(amount),
                'description': description
            }
        )

        if status != 201:
            # Get accounts for retry
            accounts_response, accounts_status = make_service_request(
                ACCOUNT_SERVICE_URL,
                '/api/accounts/list'
            )

            accounts = accounts_response.get('accounts', []) if accounts_status == 200 else []

            return render_template(
                'transfer.html',
                error=response.get('message', 'Failed to process transfer'),
                accounts=accounts
            )

        return redirect(url_for('transactions'))

    # Get accounts for the form
    response, status = make_service_request(
        ACCOUNT_SERVICE_URL,
        '/api/accounts/list'
    )

    accounts = response.get('accounts', []) if status == 200 else []

    return render_template('transfer.html', accounts=accounts)

@app.route('/transactions/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Deposit')

        if not account_id or not amount:
            return render_template('deposit.html', error='All fields are required')

        # Create deposit with transaction service
        response, status = make_service_request(
            TRANSACTION_SERVICE_URL,
            '/api/transactions/deposit',
            method='POST',
            data={
                'account_id': account_id,
                'amount': float(amount),
                'description': description
            }
        )

        if status != 201:
            # Get accounts for retry
            accounts_response, accounts_status = make_service_request(
                ACCOUNT_SERVICE_URL,
                '/api/accounts/list'
            )

            accounts = accounts_response.get('accounts', []) if accounts_status == 200 else []

            return render_template(
                'deposit.html',
                error=response.get('message', 'Failed to process deposit'),
                accounts=accounts
            )

        return redirect(url_for('transactions'))

    # Get accounts for the form
    response, status = make_service_request(
        ACCOUNT_SERVICE_URL,
        '/api/accounts/list'
    )

    accounts = response.get('accounts', []) if status == 200 else []

    return render_template('deposit.html', accounts=accounts)

@app.route('/transactions/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        amount = request.form.get('amount')
        description = request.form.get('description', 'Withdrawal')

        if not account_id or not amount:
            return render_template('withdraw.html', error='All fields are required')

        # Create withdrawal with transaction service
        response, status = make_service_request(
            TRANSACTION_SERVICE_URL,
            '/api/transactions/withdraw',
            method='POST',
            data={
                'account_id': account_id,
                'amount': float(amount),
                'description': description
            }
        )

        if status != 201:
            # Get accounts for retry
            accounts_response, accounts_status = make_service_request(
                ACCOUNT_SERVICE_URL,
                '/api/accounts/list'
            )

            accounts = accounts_response.get('accounts', []) if accounts_status == 200 else []

            return render_template(
                'withdraw.html',
                error=response.get('message', 'Failed to process withdrawal'),
                accounts=accounts
            )

        return redirect(url_for('transactions'))

    # Get accounts for the form
    response, status = make_service_request(
        ACCOUNT_SERVICE_URL,
        '/api/accounts/list'
    )

    accounts = response.get('accounts', []) if status == 200 else []

    return render_template('withdraw.html', accounts=accounts)

@app.route('/reports')
@login_required
def reports():
    # Get all reports
    response, status = make_service_request(
        REPORTING_SERVICE_URL,
        '/api/reports/list'
    )

    reports = response.get('reports', []) if status == 200 else []

    return render_template('reports.html', reports=reports)

@app.route('/reports/account/<account_id>')
@login_required
def account_report(account_id):
    # Get account report
    response, status = make_service_request(
        REPORTING_SERVICE_URL,
        f'/api/reports/account/{account_id}'
    )

    if status != 200:
        return render_template('error.html', error=response.get('message', 'Failed to generate report'))

    report = response.get('report')

    # Get basic account info
    account_response, account_status = make_service_request(
        ACCOUNT_SERVICE_URL,
        f'/api/accounts/details/{account_id}'
    )
    
    account = account_response if account_status == 200 else {}

    return render_template('report_details.html', report=report, account=account)

@app.route('/reports/transactions')
@login_required
def transaction_report():
    # Get transaction report parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    
    # Build query params
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    
    # Get transaction report
    response, status = make_service_request(
        REPORTING_SERVICE_URL,
        '/api/reports/transactions',
        params=params
    )

    if status != 200:
        return render_template('error.html', error=response.get('message', 'Failed to generate report'))

    report = response.get('report')

    return render_template('report_details.html', report=report)

@app.route('/admin')
@login_required
def admin_dashboard():
    # Verify admin status
    try:
        response, status = make_service_request(
            AUTH_SERVICE_URL,
            '/api/auth/verify_admin'
        )
        
        if status != 200 or not response.get('is_admin', False):
            return render_template('error.html', error='Admin access required')
            
        # Store admin role in session
        session['role'] = 'admin'
        
        # Get all users
        users_response, users_status = make_service_request(
            AUTH_SERVICE_URL,
            '/api/auth/users'
        )
        
        if users_status != 200:
            logger.error(f"Failed to get users: {users_response}")
        
        # Get all accounts
        accounts_response, accounts_status = make_service_request(
            ACCOUNT_SERVICE_URL,
            '/api/accounts/all'
        )
        
        if accounts_status != 200:
            logger.error(f"Failed to get accounts: {accounts_response}")
        
        # Get system report
        report_response, report_status = make_service_request(
            REPORTING_SERVICE_URL,
            '/api/reports/system'
        )
        
        if report_status != 200:
            logger.error(f"Failed to get system report: {report_response}")
        
        # Use data from responses
        users = users_response.get('users', []) if users_status == 200 else []
        accounts = accounts_response.get('accounts', []) if accounts_status == 200 else []
        
        # Extract the report data directly
        report = {}
        if report_status == 200 and 'report' in report_response:
            report = report_response.get('report', {})
            # Extract report_data if it exists (nested structure from Report model)
            if 'report_data' in report:
                report = report['report_data']
        
        return render_template(
            'admin.html',
            users=users,
            accounts=accounts,
            report=report
        )
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        return render_template('error.html', error=f'Error accessing admin dashboard: {str(e)}')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    # Check all services
    auth_health, auth_status = make_service_request(AUTH_SERVICE_URL, '/api/health')
    account_health, account_status = make_service_request(ACCOUNT_SERVICE_URL, '/api/health')
    transaction_health, transaction_status = make_service_request(TRANSACTION_SERVICE_URL, '/api/health')
    reporting_health, reporting_status = make_service_request(REPORTING_SERVICE_URL, '/api/health')

    all_healthy = all(status == 200 for status in [auth_status, account_status, transaction_status, reporting_status])

    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'services': {
            'api-gateway': 'healthy',
            'auth-service': 'healthy' if auth_status == 200 else 'unhealthy',
            'account-service': 'healthy' if account_status == 200 else 'unhealthy',
            'transaction-service': 'healthy' if transaction_status == 200 else 'unhealthy',
            'reporting-service': 'healthy' if reporting_status == 200 else 'unhealthy'
        }
    }), 200 if all_healthy else 503

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Server error'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)