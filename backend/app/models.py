#!/usr/bin/env python3
"""
User models for authentication
"""
from flask_login import UserMixin
from .config import Config

class User(UserMixin):
    """Simple user model for authentication"""
    
    def __init__(self, username):
        self.id = username
        self.username = username
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @staticmethod
    def get(username):
        """Get user by username"""
        # Simple authentication - in production use proper database
        if username == Config.ADMIN_USERNAME:
            return User(username)
        return None
    
    @staticmethod
    def verify_password(username, password):
        """Verify user password"""
        # Simple authentication - in production use proper hashing
        return (username == Config.ADMIN_USERNAME and 
                password == Config.ADMIN_PASSWORD)