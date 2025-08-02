#!/usr/bin/env python3
"""
Web Dashboard for MAN Scraper Suite
Interactive web-based user management interface
"""

from flask import Flask, render_template, jsonify, request
from omniscraper.core.user_manager import UserManager
from omniscraper.core.config import Config
import os

app = Flask(__name__, template_folder='templates')
config = Config()
user_manager = UserManager(config.config)

@app.route('/')
def index():
    """Render the main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/users')
def list_users():
    """API endpoint to get list of users"""
    users = user_manager.get_user_stats()
    return jsonify(users)

@app.route('/api/user/<email>', methods=['GET'])
def get_user(email):
    """Get individual user details"""
    user = user_manager.get_user(email)
    return jsonify(user) if user else (jsonify({'error': 'User not found'}), 404)

@app.route('/api/ban_user', methods=['POST'])
def ban_user():
    """Ban a user API"""
    email = request.json.get('email')
    reason = request.json.get('reason', 'No reason provided')
    result = user_manager.ban_user(email, reason)
    return jsonify({'success': result})

# Add more routes and handlers for dashboard functionalities

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
