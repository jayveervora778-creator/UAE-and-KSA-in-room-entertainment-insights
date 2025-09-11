#!/usr/bin/env python3
"""
Main application entry point for Survey Dashboard
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Set environment variables for development
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    print("Starting Survey Dashboard...")
    print(f"Access the dashboard at: http://localhost:{port}")
    print("Login credentials: admin / surveydash2024")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )