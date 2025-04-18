import os
import consul
import logging
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, request, jsonify
from auth_service.auth_models import db, User

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import os
import consul

# Consul configuration
CONSUL_HOST = os.environ.get("CONSUL_HOST", "localhost")
CONSUL_PORT = int(os.environ.get("CONSUL_PORT", 8500))
SERVICE_NAME = "auth-service"
SERVICE_ID = f"{SERVICE_NAME}-{os.urandom(8).hex()}"
SERVICE_PORT = 8001

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

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("AUTH_DATABASE_URL")
app.config["JWT_SECRET_KEY"] = os.environ.get("SESSION_SECRET", "auth_service_secret_key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

# Initialize extensions
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
# Register service on startup
with app.app_context():
    register_service()

# Deregister service on shutdown
import atexit
atexit.register(deregister_service)

import os
import consul
import logging
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash

import logging

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("AUTH_DATABASE_URL")
app.config["JWT_SECRET_KEY"] = os.environ.get("SESSION_SECRET", "auth_service_secret_key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

# Initialize extensions
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Helper functions
def generate_token(user_id, username, role):
    """Generate a JWT token for a user"""
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': user_id,
        'username': username,
        'role': role
    }
    return jwt.encode(
        payload,
        app.config.get('JWT_SECRET_KEY'),
        algorithm='HS256'
    )

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
            payload = jwt.decode(
                token,
                app.config.get('JWT_SECRET_KEY'),
                algorithms=['HS256']
            )
            
            # Get user from database
            with app.app_context():
                current_user = User.query.filter_by(id=payload['sub']).first()
            
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
                
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
        if current_user.role != 'admin':
            return jsonify({'message': 'Admin privilege required'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

# Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'auth-service'}), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.json
    
    # Validate required fields
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Check if username or email already exists
    with app.app_context():
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already exists'}), 400
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=User.hash_password(data['password']),
            role=data.get('role', 'customer')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate a user and return a token"""
    data = request.json
    
    # Validate required fields
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    with app.app_context():
        # Find user by username
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.verify_password(data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
        
        if user.status != 'active':
            return jsonify({'message': 'Account is not active'}), 403
        
        # Generate JWT token
        token = generate_token(user.id, user.username, user.role)
        
        return jsonify({
            'token': token,
            'user_id': user.id,
            'username': user.username,
            'role': user.role
        }), 200

@app.route('/api/auth/verify_token', methods=['GET'])
@token_required
def verify_token(current_user):
    """Verify if a token is valid and return user info"""
    return jsonify({
        'user_id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'role': current_user.role,
        'status': current_user.status
    }), 200

@app.route('/api/auth/verify_admin', methods=['GET'])
@token_required
def verify_admin(current_user):
    """Verify if a user has admin privileges"""
    is_admin = current_user.role == 'admin'
    return jsonify({'is_admin': is_admin}), 200

@app.route('/api/auth/users/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get current user's profile"""
    return jsonify(current_user.to_dict()), 200

@app.route('/api/auth/users/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """Update current user's profile"""
    data = request.json
    
    # Fields that users can update
    allowed_fields = ['email']
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    
    with app.app_context():
        for key, value in updates.items():
            setattr(current_user, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200

@app.route('/api/auth/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """Get all users (admin only)"""
    with app.app_context():
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200

@app.route('/api/auth/users/<user_id>', methods=['GET'])
@token_required
@admin_required
def get_user_by_id(current_user, user_id):
    """Get user by ID (admin only)"""
    with app.app_context():
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        return jsonify(user.to_dict()), 200

@app.route('/api/auth/users/<user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user(current_user, user_id):
    """Update a user (admin only)"""
    data = request.json
    
    with app.app_context():
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Fields that admins can update
        allowed_fields = ['email', 'role', 'status']
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        
        for key, value in updates.items():
            setattr(user, key, value)
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200

@app.route('/api/auth/users/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user(current_user, user_id):
    """Delete a user (admin only)"""
    with app.app_context():
        user = User.query.filter_by(id=user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200

def create_default_admin():
    """Create a default admin user if no users exist"""
    with app.app_context():
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=User.hash_password('admin123'),
                role='admin'
            )
            
            db.session.add(admin_user)
            db.session.commit()
            logger.info("Created default admin user")

# Create default admin user
create_default_admin()

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8001)