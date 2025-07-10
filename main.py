#!/usr/bin/env python3
"""
ByteDohm.de - PHP Router
Serves PHP files through Python for Replit compatibility
"""

import subprocess
import os
import sys
from flask import Flask, request, Response
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def execute_php(php_file, query_string=''):
    """Execute PHP file and return response"""
    try:
        # Set environment variables for PHP
        env = os.environ.copy()
        env['REQUEST_METHOD'] = request.method
        env['QUERY_STRING'] = query_string
        env['REQUEST_URI'] = request.path
        env['SCRIPT_NAME'] = php_file
        
        # Add POST data if available
        if request.method == 'POST':
            env['CONTENT_TYPE'] = request.content_type or 'application/x-www-form-urlencoded'
            env['CONTENT_LENGTH'] = str(len(request.data))
        
        # Prepare PHP command
        cmd = ['/nix/store/8xs6a2mh8vhb0r5ds4wh5nm6a59x66z6-php-with-extensions-8.2.23/bin/php', php_file]
        
        # Execute PHP
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            env=env,
            cwd='/home/runner/workspace'
        )
        
        # Send POST data if available
        stdin_data = request.data if request.method == 'POST' else None
        stdout, stderr = process.communicate(input=stdin_data)
        
        if stderr:
            logger.error(f"PHP Error: {stderr.decode()}")
        
        return stdout.decode('utf-8', errors='ignore')
        
    except Exception as e:
        logger.error(f"Error executing PHP: {e}")
        return f"Error: {e}"

@app.route('/')
def index():
    """Serve index.php"""
    return Response(execute_php('index.php'), mimetype='text/html')

@app.route('/<path:filename>')
def serve_php(filename):
    """Serve PHP files"""
    # Handle PHP files
    if filename.endswith('.php'):
        php_file = filename
    else:
        # Try to find corresponding PHP file
        php_file = filename + '.php'
        if not os.path.exists(php_file):
            php_file = filename + '/index.php'
            if not os.path.exists(php_file):
                return f"File not found: {filename}", 404
    
    if not os.path.exists(php_file):
        return f"PHP file not found: {php_file}", 404
    
    query_string = request.query_string.decode()
    response_content = execute_php(php_file, query_string)
    
    return Response(response_content, mimetype='text/html')

# Handle POST requests
@app.route('/<path:filename>', methods=['POST'])
def serve_php_post(filename):
    """Handle POST requests to PHP files"""
    return serve_php(filename)

if __name__ == "__main__":
    logger.info("Starting ByteDohm PHP Router...")
    logger.info("Available PHP files:")
    for root, dirs, files in os.walk('/home/runner/workspace'):
        for file in files:
            if file.endswith('.php'):
                logger.info(f"  {os.path.join(root, file)}")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
