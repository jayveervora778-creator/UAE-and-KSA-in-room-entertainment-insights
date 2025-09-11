#!/usr/bin/env python3
"""
Survey Dashboard Flask Application
"""
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from .config import Config

# Initialize login manager
login_manager = LoginManager()

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    CORS(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access the dashboard'
    
    # Register blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from .main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app