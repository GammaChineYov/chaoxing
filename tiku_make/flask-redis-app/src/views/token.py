import uuid
from flask import Blueprint, jsonify, request
from flask_httpauth import HTTPTokenAuth, HTTPBasicAuth
from werkzeug.security import check_password_hash
from src.extensions import redis_client
from src.models.user import User

token_bp = Blueprint('token', __name__)
auth = HTTPTokenAuth(scheme='Bearer')
basic_auth = HTTPBasicAuth()

redis_client = redis_client

@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return user

@token_bp.route('/generate', methods=['POST'])
@basic_auth.login_required
def generate_token():
    username = basic_auth.current_user().username
    token = str(uuid.uuid4())  # 使用UUID生成唯一token
    redis_client.sadd('tokens', token)
    redis_client.set(token, username)
    return jsonify({"token": token}), 201

@token_bp.route('/validate', methods=['POST'])
@auth.login_required
def validate_token():
    return jsonify({"message": "Token 验证成功"}), 200

@auth.verify_token
def verify_token(token):
    return redis_client.sismember('tokens', token)