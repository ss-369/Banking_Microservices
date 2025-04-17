import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TransactionStorage:
    """Storage handler for transaction service"""
    
    def __init__(self, data_dir='./data'):
        """Initialize storage with data directory"""
        self.data_dir = data_dir
        self.transactions_file = f"{data_dir}/transactions.json"
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Create transactions file if it doesn't exist
        if not os.path.exists(self.transactions_file):
            with open(self.transactions_file, 'w') as f:
                json.dump([], f)
    
    def get_all_transactions(self):
        """Get all transactions from storage"""
        try:
            with open(self.transactions_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading transactions file: {e}")
            return []
    
    def get_transaction(self, transaction_id):
        """Get transaction by ID"""
        transactions = self.get_all_transactions()
        
        for transaction in transactions:
            if transaction['id'] == transaction_id:
                return transaction
        
        return None
    
    def get_transactions_by_account_id(self, account_id):
        """Get all transactions for a specific account"""
        transactions = self.get_all_transactions()
        
        # Filter transactions by account_id
        # For both direct account transactions and transfers
        account_transactions = []
        
        for transaction in transactions:
            if transaction.get('transaction_type') in ['deposit', 'withdrawal']:
                if transaction.get('account_id') == account_id:
                    account_transactions.append(transaction)
            elif transaction.get('transaction_type') == 'transfer':
                if transaction.get('from_account_id') == account_id or transaction.get('to_account_id') == account_id:
                    account_transactions.append(transaction)
        
        return account_transactions
    
    def create_transaction(self, transaction_data):
        """Create a new transaction"""
        transactions = self.get_all_transactions()
        
        # Check for duplicate ID
        for transaction in transactions:
            if transaction['id'] == transaction_data['id']:
                return False
        
        transactions.append(transaction_data)
        
        try:
            with open(self.transactions_file, 'w') as f:
                json.dump(transactions, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error writing transaction data: {e}")
            return False
    
    def update_transaction(self, transaction_id, update_data):
        """Update an existing transaction"""
        transactions = self.get_all_transactions()
        
        for i, transaction in enumerate(transactions):
            if transaction['id'] == transaction_id:
                # Update fields
                for key, value in update_data.items():
                    transactions[i][key] = value
                
                try:
                    with open(self.transactions_file, 'w') as f:
                        json.dump(transactions, f, indent=2)
                    return True
                except Exception as e:
                    logger.error(f"Error updating transaction data: {e}")
                    return False
        
        return False
    
    def delete_transaction(self, transaction_id):
        """Delete a transaction"""
        transactions = self.get_all_transactions()
        
        for i, transaction in enumerate(transactions):
            if transaction['id'] == transaction_id:
                transactions.pop(i)
                
                try:
                    with open(self.transactions_file, 'w') as f:
                        json.dump(transactions, f, indent=2)
                    return True
                except Exception as e:
                    logger.error(f"Error deleting transaction data: {e}")
                    return False
        
        return False
