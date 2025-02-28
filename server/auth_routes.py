from flask import Blueprint, request, jsonify, session
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
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256',  salt_length=8)
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Set session
    session['user_id'] = new_user.id
    
    return jsonify({
        "id": new_user.id,
        "username": new_user.username
    }), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password required"}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({"error": "Invalid credentials"}), 401

    # Set session
    session['user_id'] = user.id
    
    return jsonify({
        "id": user.id,
        "username": user.username
    }), 200

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    # Clear the session
    session.pop('user_id', None)
    return '', 200

@auth_bp.route('/api/user', methods=['GET'])
def get_user():
    # Get user from session
    user_id = session.get('user_id')
    if not user_id:
        return '', 401
    
    user = User.query.get(user_id)
    if not user:
        return '', 401
        
    return jsonify({
        "id": user.id,
        "username": user.username
    }), 200
