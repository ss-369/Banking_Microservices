import os
import json
import logging
import random
import string
import re
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_random_string(length=10):
    """Generate a random string of fixed length"""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def validate_email(email):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_date(date_str):
    """Format ISO date string to user-friendly format"""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime('%B %d, %Y %I:%M %p')
    except (ValueError, TypeError):
        return date_str

def format_account_number(account_number):
    """Format account number for display (show last 4 digits)"""
    if not account_number:
        return ''
        
    return f"****{account_number[-4:]}"

def safe_json_loads(json_str, default=None):
    """Safely load JSON string"""
    if not json_str:
        return default
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON: {json_str}")
        return default

def get_transaction_description(transaction):
    """Get a user-friendly description for a transaction"""
    if transaction.get('description'):
        return transaction['description']
    
    transaction_type = transaction.get('transaction_type', '')
    
    if transaction_type == 'deposit':
        return 'Deposit'
    elif transaction_type == 'withdrawal':
        return 'Withdrawal'
    elif transaction_type == 'transfer':
        transfer_type = transaction.get('transfer_type', 'internal')
        return f"{transfer_type.upper()} Transfer"
    
    return 'Transaction'

def get_service_url(service_name):
    """Get URL for a specific microservice"""
    service_urls = {
        'auth': os.environ.get('AUTH_SERVICE_URL', 'http://0.0.0.0:8001'),
        'account': os.environ.get('ACCOUNT_SERVICE_URL', 'http://0.0.0.0:8002'),
        'transaction': os.environ.get('TRANSACTION_SERVICE_URL', 'http://0.0.0.0:8003'),
        'reporting': os.environ.get('REPORTING_SERVICE_URL', 'http://0.0.0.0:8004')
    }
    
    return service_urls.get(service_name.lower(), '')

def truncate_text(text, max_length=100):
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length] + '...'
