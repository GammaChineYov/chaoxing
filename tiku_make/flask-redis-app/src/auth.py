from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import redis

auth_bp = Blueprint('auth', __name__)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400
    
    hashed_password = generate_password_hash(password)
    redis_client.hset('users', username, hashed_password)
    
    return jsonify({"message": "User registered successfully."}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400
    
    stored_password = redis_client.hget('users', username)
    
    if stored_password and check_password_hash(stored_password, password):
        return jsonify({"message": "Login successful."}), 200
    else:
        return jsonify({"message": "Invalid username or password."}), 401

@auth_bp.route('/auth', methods=['GET'])
def auth():
    return jsonify({"message": "Authentication service is running."}), 200