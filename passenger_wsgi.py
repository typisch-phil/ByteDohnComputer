#!/usr/bin/python
"""
Passenger WSGI file for Plesk hosting deployment
This file is required for Python applications on Plesk hosting
"""
import os
import sys

# Add the application directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment for production
os.environ['FLASK_ENV'] = 'production'

# Import the Flask application
from app import app

# Set the WSGI application object that Passenger will use
application = app

# Configure for production
app.config['DEBUG'] = False
app.config['TESTING'] = False

if __name__ == "__main__":
    app.run(debug=False)