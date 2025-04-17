import os
import json
import logging
from pathlib import Path
from models import User, Account, Transaction, Report

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Storage:
    """Base storage class for all services"""
    
    def __init__(self, data_dir='./data'):
        """Initialize storage with data directory"""
        self.data_dir = Path(data_dir)
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        
    def _get_file_path(self, collection, id=None):
        """Get the file path for a collection or specific document"""
        if id:
            return self.data_dir / f"{collection}_{id}.json"
        return self.data_dir / f"{collection}.json"
    
    def _save_to_file(self, file_path, data):
        """Save data to a file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_from_file(self, file_path):
        """Load data from a file"""
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def _save_collection(self, collection, items):
        """Save a collection of items"""
        file_path = self._get_file_path(collection)
        self._save_to_file(file_path, items)
    
    def _load_collection(self, collection):
        """Load a collection of items"""
        file_path = self._get_file_path(collection)
        return self._load_from_file(file_path) or []

class UserStorage(Storage):
    """Storage handler for authentication service"""
    
    def __init__(self, data_dir='./data'):
        """Initialize storage with data directory"""
        super().__init__(data_dir)
        self.collection = 'users'
    
    def get_all_users(self):
        """Get all users from storage"""
        users_data = self._load_collection(self.collection)
        return [User.from_dict(user_data) for user_data in users_data]
    
    def get_user(self, user_id):
        """Get user by ID"""
        users = self.get_all_users()
        for user in users:
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        users = self.get_all_users()
        for user in users:
            if user.username == username:
                return user
        return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        users = self.get_all_users()
        for user in users:
            if user.email == email:
                return user
        return None
    
    def create_user(self, user_data):
        """Create a new user"""
        # Check if username or email already exists
        if self.get_user_by_username(user_data.username):
            raise ValueError("Username already exists")
        
        if self.get_user_by_email(user_data.email):
            raise ValueError("Email already exists")
        
        # Save user
        users = self.get_all_users()
        users.append(user_data)
        
        self._save_collection(self.collection, [user.to_dict() for user in users])
        return user_data
    
    def update_user(self, user_id, update_data):
        """Update an existing user"""
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update user fields
        for key, value in update_data.items():
            if key in ['username', 'email', 'role', 'status']:
                setattr(user, key, value)
        
        # Save updated user
        users = self.get_all_users()
        for i, u in enumerate(users):
            if u.id == user_id:
                users[i] = user
                break
                
        self._save_collection(self.collection, [user.to_dict() for user in users])
        return user
    
    def delete_user(self, user_id):
        """Delete a user"""
        users = self.get_all_users()
        updated_users = [user for user in users if user.id != user_id]
        
        if len(updated_users) == len(users):
            raise ValueError("User not found")
            
        self._save_collection(self.collection, [user.to_dict() for user in updated_users])
        return True

class AccountStorage(Storage):
    """Storage handler for account service"""
    
    def __init__(self, data_dir='./data'):
        """Initialize storage with data directory"""
        super().__init__(data_dir)
        self.collection = 'accounts'
    
    def get_all_accounts(self):
        """Get all accounts from storage"""
        accounts_data = self._load_collection(self.collection)
        return [Account.from_dict(account_data) for account_data in accounts_data]
    
    def get_account(self, account_id):
        """Get account by ID"""
        accounts = self.get_all_accounts()
        for account in accounts:
            if account.id == account_id:
                return account
        return None
    
    def get_account_by_account_number(self, account_number):
        """Get account by account number"""
        accounts = self.get_all_accounts()
        for account in accounts:
            if account.account_number == account_number:
                return account
        return None
    
    def get_accounts_by_user_id(self, user_id):
        """Get all accounts for a specific user"""
        accounts = self.get_all_accounts()
        return [account for account in accounts if account.user_id == user_id]
    
    def create_account(self, account_data):
        """Create a new account"""
        # Save account
        accounts = self.get_all_accounts()
        accounts.append(account_data)
        
        self._save_collection(self.collection, [account.to_dict() for account in accounts])
        return account_data
    
    def update_account(self, account_id, update_data):
        """Update an existing account"""
        account = self.get_account(account_id)
        if not account:
            raise ValueError("Account not found")
        
        # Update account fields
        for key, value in update_data.items():
            if key in ['balance', 'status']:
                setattr(account, key, value)
        
        # Save updated account
        accounts = self.get_all_accounts()
        for i, a in enumerate(accounts):
            if a.id == account_id:
                accounts[i] = account
                break
                
        self._save_collection(self.collection, [account.to_dict() for account in accounts])
        return account
    
    def delete_account(self, account_id):
        """Delete an account"""
        accounts = self.get_all_accounts()
        updated_accounts = [account for account in accounts if account.id != account_id]
        
        if len(updated_accounts) == len(accounts):
            raise ValueError("Account not found")
            
        self._save_collection(self.collection, [account.to_dict() for account in updated_accounts])
        return True

class TransactionStorage(Storage):
    """Storage handler for transaction service"""
    
    def __init__(self, data_dir='./data'):
        """Initialize storage with data directory"""
        super().__init__(data_dir)
        self.collection = 'transactions'
    
    def get_all_transactions(self):
        """Get all transactions from storage"""
        transactions_data = self._load_collection(self.collection)
        return [Transaction.from_dict(transaction_data) for transaction_data in transactions_data]
    
    def get_transaction(self, transaction_id):
        """Get transaction by ID"""
        transactions = self.get_all_transactions()
        for transaction in transactions:
            if transaction.id == transaction_id:
                return transaction
        return None
    
    def get_transactions_by_account_id(self, account_id):
        """Get all transactions for a specific account"""
        transactions = self.get_all_transactions()
        return [t for t in transactions if 
                (t.transaction_type in ['deposit', 'withdrawal'] and t.account_id == account_id) or
                (t.transaction_type == 'transfer' and (t.from_account_id == account_id or t.to_account_id == account_id))]
    
    def get_transactions_by_user_accounts(self, account_ids):
        """Get all transactions for a list of account IDs"""
        transactions = self.get_all_transactions()
        result = []
        
        for t in transactions:
            if t.transaction_type in ['deposit', 'withdrawal'] and t.account_id in account_ids:
                result.append(t)
            elif t.transaction_type == 'transfer' and (t.from_account_id in account_ids or t.to_account_id in account_ids):
                result.append(t)
                
        return result
    
    def create_transaction(self, transaction_data):
        """Create a new transaction"""
        # Save transaction
        transactions = self.get_all_transactions()
        transactions.append(transaction_data)
        
        self._save_collection(self.collection, [transaction.to_dict() for transaction in transactions])
        return transaction_data
    
    def update_transaction(self, transaction_id, update_data):
        """Update an existing transaction"""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        # Update transaction fields
        for key, value in update_data.items():
            if key in ['status', 'description']:
                setattr(transaction, key, value)
        
        # Save updated transaction
        transactions = self.get_all_transactions()
        for i, t in enumerate(transactions):
            if t.id == transaction_id:
                transactions[i] = transaction
                break
                
        self._save_collection(self.collection, [transaction.to_dict() for transaction in transactions])
        return transaction
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction"""
        transactions = self.get_all_transactions()
        updated_transactions = [transaction for transaction in transactions if transaction.id != transaction_id]
        
        if len(updated_transactions) == len(transactions):
            raise ValueError("Transaction not found")
            
        self._save_collection(self.collection, [transaction.to_dict() for transaction in updated_transactions])
        return True

class ReportStorage(Storage):
    """Storage handler for reporting service"""
    
    def __init__(self, data_dir='./data'):
        """Initialize storage with data directory"""
        super().__init__(data_dir)
        self.collection = 'reports'
    
    def get_all_reports(self):
        """Get all reports from storage"""
        reports_data = self._load_collection(self.collection)
        return [Report.from_dict(report_data) for report_data in reports_data]
    
    def get_report(self, report_id):
        """Get report by ID"""
        reports = self.get_all_reports()
        for report in reports:
            if report.id == report_id:
                return report
        return None
    
    def get_reports_by_user_id(self, user_id):
        """Get all reports for a specific user"""
        reports = self.get_all_reports()
        return [report for report in reports if report.parameters.get('user_id') == user_id]
    
    def save_report(self, report_data):
        """Save a report"""
        # Save report
        reports = self.get_all_reports()
        
        # Update if exists, otherwise add
        found = False
        for i, r in enumerate(reports):
            if r.id == report_data.id:
                reports[i] = report_data
                found = True
                break
                
        if not found:
            reports.append(report_data)
        
        self._save_collection(self.collection, [report.to_dict() for report in reports])
        return report_data
    
    def delete_report(self, report_id):
        """Delete a report"""
        reports = self.get_all_reports()
        updated_reports = [report for report in reports if report.id != report_id]
        
        if len(updated_reports) == len(reports):
            raise ValueError("Report not found")
            
        self._save_collection(self.collection, [report.to_dict() for report in updated_reports])
        return True