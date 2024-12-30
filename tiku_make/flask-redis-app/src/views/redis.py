from flask import Blueprint, request, jsonify
from flask_httpauth import HTTPTokenAuth
import json
from src.extensions import redis_client

redis_bp = Blueprint('redis', __name__)
auth = HTTPTokenAuth(scheme='Bearer')

tokens = {"mysecrettoken"}

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return True
    return redis_client.sismember('tokens', token)

@redis_bp.route('/lpop', methods=['POST'])
@auth.login_required
def lpop():
    data = request.json
    key = data.get('key')
    value = redis_client.lpop(key)
    return jsonify({"value": value}), 200

@redis_bp.route('/clean_up_no_answer_entries', methods=['POST'])
@auth.login_required
def clean_up_no_answer_entries():
    keys = redis_client.keys('question_*')
    for key in keys:
        data = redis_client.get(key)
        data = json.loads(data)
        if not data or not any([d.get('answer') for d in data]):
            redis_client.delete(key)
    return jsonify({"message": "清理完成"}), 200

@redis_bp.route('/get_unique_question', methods=['POST'])
@auth.login_required
def get_unique_question():
    question = redis_client.lpop('questions')
    return jsonify({"question": question}), 200