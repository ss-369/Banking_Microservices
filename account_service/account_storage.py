import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AccountStorage:
    """Storage handler for account service"""
    
    def __init__(self, data_dir='./data'):
        """Initialize storage with data directory"""
        self.data_dir = data_dir
        self.accounts_file = f"{data_dir}/accounts.json"
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Create accounts file if it doesn't exist
        if not os.path.exists(self.accounts_file):
            with open(self.accounts_file, 'w') as f:
                json.dump([], f)
    
    def get_all_accounts(self):
        """Get all accounts from storage"""
        try:
            with open(self.accounts_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading accounts file: {e}")
            return []
    
    def get_account(self, account_id):
        """Get account by ID"""
        accounts = self.get_all_accounts()
        
        for account in accounts:
            if account['id'] == account_id:
                return account
        
        return None
    
    def get_account_by_account_number(self, account_number):
        """Get account by account number"""
        accounts = self.get_all_accounts()
        
        for account in accounts:
            if account['account_number'] == account_number:
                return account
        
        return None
    
    def get_accounts_by_user_id(self, user_id):
        """Get all accounts for a specific user"""
        accounts = self.get_all_accounts()
        
        # Filter accounts by user_id
        user_accounts = [account for account in accounts if account['user_id'] == user_id]
        
        return user_accounts
    
    def create_account(self, account_data):
        """Create a new account"""
        accounts = self.get_all_accounts()
        
        # Check for duplicate ID
        for account in accounts:
            if account['id'] == account_data['id']:
                return False
        
        accounts.append(account_data)
        
        try:
            with open(self.accounts_file, 'w') as f:
                json.dump(accounts, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error writing account data: {e}")
            return False
    
    def update_account(self, account_id, update_data):
        """Update an existing account"""
        accounts = self.get_all_accounts()
        
        for i, account in enumerate(accounts):
            if account['id'] == account_id:
                # Update fields
                for key, value in update_data.items():
                    accounts[i][key] = value
                
                try:
                    with open(self.accounts_file, 'w') as f:
                        json.dump(accounts, f, indent=2)
                    return True
                except Exception as e:
                    logger.error(f"Error updating account data: {e}")
                    return False
        
        return False
    
    def delete_account(self, account_id):
        """Delete an account"""
        accounts = self.get_all_accounts()
        
        for i, account in enumerate(accounts):
            if account['id'] == account_id:
                accounts.pop(i)
                
                try:
                    with open(self.accounts_file, 'w') as f:
                        json.dump(accounts, f, indent=2)
                    return True
                except Exception as e:
                    logger.error(f"Error deleting account data: {e}")
                    return False
        
        return False
