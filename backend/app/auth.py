#!/usr/bin/env python3
"""
Authentication blueprint
"""
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from .config import Config

bp = Blueprint('auth', __name__)

# Import login manager from __init__.py
from . import login_manager

@login_manager.user_loader
def load_user(username):
    """Load user for Flask-Login"""
    return User.get(username)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login endpoint"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        if request.is_json:
            # API request
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '')
        else:
            # Form request
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
        
        # Debug logging
        print(f"Login attempt - Username: '{username}', Password length: {len(password)}")
        
        if User.verify_password(username, password):
            user = User(username)
            login_user(user, remember=True)
            print(f"Login successful for user: {username}")
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': username
                })
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('main.dashboard'))
        else:
            print(f"Login failed - Username: '{username}', Expected: '{Config.ADMIN_USERNAME}', Password match: {password == Config.ADMIN_PASSWORD}")
            if request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Invalid username or password'
                }), 401
            else:
                flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout endpoint"""
    logout_user()
    if request.is_json:
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    else:
        flash('You have been logged out.', 'info')
        return redirect(url_for('auth.login'))

@bp.route('/api/check-auth')
def check_auth():
    """Check authentication status"""
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'username': current_user.username if current_user.is_authenticated else None
    })