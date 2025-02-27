
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password required"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409

    # Create new user
    hashed_password = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.__dict__), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password required"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    # In a real app, you would create a session or token here
    return jsonify(user.__dict__), 200

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    # In a real app, you would clear the session or invalidate the token
    return '', 200

@auth_bp.route('/api/user', methods=['GET'])
def get_user():
    # Placeholder for authentication middleware
    # In a real app, you would get the user from the session or token
    user_id = 1  # Temporary
    user = User.query.get(user_id)
    if not user:
        return '', 401
    return jsonify(user.__dict__), 200

