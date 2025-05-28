#!/usr/bin/env python3
"""
User Management System for FastFounder Daily Bot
Handles storing and managing multiple Telegram users.
"""

import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserManager:
    """Manages bot users and their preferences."""
    
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self.users = self._load_users()
    
    def _load_users(self):
        """Load users from JSON file."""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Error loading users file: {e}")
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file."""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Users saved to {self.users_file}")
        except Exception as e:
            logger.error(f"❌ Error saving users file: {e}")
    
    def add_user(self, chat_id, username=None, first_name=None, last_name=None):
        """Add a new user or update existing user info."""
        chat_id = str(chat_id)  # Ensure string key
        
        user_data = {
            'chat_id': chat_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'joined_date': datetime.now().isoformat(),
            'active': True,
            'message_count': self.users.get(chat_id, {}).get('message_count', 0)
        }
        
        # If user exists, preserve some data
        if chat_id in self.users:
            user_data['joined_date'] = self.users[chat_id].get('joined_date', user_data['joined_date'])
            user_data['message_count'] = self.users[chat_id].get('message_count', 0)
            logger.info(f"👤 Updated existing user: {chat_id}")
        else:
            logger.info(f"👤 Added new user: {chat_id}")
        
        self.users[chat_id] = user_data
        self._save_users()
        return True
    
    def remove_user(self, chat_id):
        """Remove a user (mark as inactive)."""
        chat_id = str(chat_id)
        if chat_id in self.users:
            self.users[chat_id]['active'] = False
            self._save_users()
            logger.info(f"👤 Deactivated user: {chat_id}")
            return True
        return False
    
    def get_active_users(self):
        """Get list of active user chat IDs."""
        active_users = []
        for chat_id, user_data in self.users.items():
            if user_data.get('active', True):
                active_users.append(chat_id)
        return active_users
    
    def get_user_count(self):
        """Get total number of active users."""
        return len(self.get_active_users())
    
    def increment_message_count(self, chat_id):
        """Increment message count for a user."""
        chat_id = str(chat_id)
        if chat_id in self.users:
            self.users[chat_id]['message_count'] = self.users[chat_id].get('message_count', 0) + 1
            self._save_users()
    
    def get_user_info(self, chat_id):
        """Get user information."""
        chat_id = str(chat_id)
        return self.users.get(chat_id, None)
    
    def get_all_users_info(self):
        """Get information about all users."""
        return self.users 