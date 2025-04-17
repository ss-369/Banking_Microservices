import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AuthStorage:
    """Storage handler for authentication service"""
    
    def __init__(self, data_dir='./data'):
        """Initialize storage with data directory"""
        self.data_dir = data_dir
        self.users_file = f"{data_dir}/users.json"
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Create users file if it doesn't exist
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump([], f)
    
    def get_all_users(self):
        """Get all users from storage"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading users file: {e}")
            return []
    
    def get_user(self, user_id):
        """Get user by ID"""
        users = self.get_all_users()
        
        for user in users:
            if user['id'] == user_id:
                return user
        
        return None
    
    def get_user_by_username(self, username):
        """Get user by username"""
        users = self.get_all_users()
        
        for user in users:
            if user['username'].lower() == username.lower():
                return user
        
        return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        users = self.get_all_users()
        
        for user in users:
            if user['email'].lower() == email.lower():
                return user
        
        return None
    
    def create_user(self, user_data):
        """Create a new user"""
        users = self.get_all_users()
        
        # Check for duplicate ID just in case
        for user in users:
            if user['id'] == user_data['id']:
                return False
        
        users.append(user_data)
        
        try:
            with open(self.users_file, 'w') as f:
                json.dump(users, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error writing user data: {e}")
            return False
    
    def update_user(self, user_id, update_data):
        """Update an existing user"""
        users = self.get_all_users()
        
        for i, user in enumerate(users):
            if user['id'] == user_id:
                # Update fields
                for key, value in update_data.items():
                    users[i][key] = value
                
                try:
                    with open(self.users_file, 'w') as f:
                        json.dump(users, f, indent=2)
                    return True
                except Exception as e:
                    logger.error(f"Error updating user data: {e}")
                    return False
        
        return False
    
    def delete_user(self, user_id):
        """Delete a user"""
        users = self.get_all_users()
        
        for i, user in enumerate(users):
            if user['id'] == user_id:
                users.pop(i)
                
                try:
                    with open(self.users_file, 'w') as f:
                        json.dump(users, f, indent=2)
                    return True
                except Exception as e:
                    logger.error(f"Error deleting user data: {e}")
                    return False
        
        return False
