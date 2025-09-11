#!/usr/bin/env python3
"""
Main routes for the survey dashboard
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Legacy dashboard page"""
    return render_template('enhanced_dashboard.html', user=current_user.username)

@bp.route('/osn-analytics')
@login_required
def osn_enterprise_dashboard():
    """OSN Enterprise Analytics Dashboard"""
    return render_template('osn_enterprise_dashboard.html', user=current_user.username)

@bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'survey-dashboard',
        'version': '1.0.0'
    })