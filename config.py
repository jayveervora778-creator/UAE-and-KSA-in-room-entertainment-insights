#!/usr/bin/env python3
"""
Configuration settings for the Survey Dashboard application
"""
import os
from pathlib import Path

basedir = Path(__file__).parent.parent

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Database settings (using simple file-based auth for this demo)
    DATA_DIR = basedir / 'data'
    SURVEY_DATA_FILE = DATA_DIR / 'survey_data.xlsx'
    
    # Authentication settings
    # In production, these should be in environment variables or a proper database
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'surveydash2024'
    
    # NLP settings
    SPACY_MODEL = 'en_core_web_sm'
    
    # Dashboard settings
    MAX_UPLOAD_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}
    
    @staticmethod
    def init_app(app):
        pass