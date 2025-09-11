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
    """Redirect legacy dashboard to unified dashboard"""
    from flask import redirect, url_for
    return redirect(url_for('main.unified_dashboard'))

@bp.route('/osn-analytics')
@login_required
def osn_enterprise_dashboard():
    """OSN Enterprise Analytics Dashboard"""
    return render_template('osn_enterprise_dashboard.html', user=current_user.username)

@bp.route('/dynamic-questions')
@login_required
def dynamic_questions_dashboard():
    """Dynamic Multi-Question Analytics Dashboard"""
    return render_template('dynamic_questions_dashboard.html', user=current_user.username)

@bp.route('/unified-dashboard')
@login_required
def unified_dashboard():
    """Unified OSN Analytics Dashboard - All Features in One Page"""
    return render_template('unified_osn_dashboard.html', user=current_user.username)

@bp.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'survey-dashboard',
        'version': '1.0.0'
    })