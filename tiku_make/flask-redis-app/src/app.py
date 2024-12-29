import os 
import sys
sys.path.append(os.path.dirname(__file__))
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
from redis_client import RedisClient


app = Flask(__name__)
CORS(app)
auth = HTTPTokenAuth(scheme='Bearer')

# 配置Redis客户端
redis_client = RedisClient(password='question_scraper')


# 存储token的字典
tokens = {
    "mysecrettoken": "user1"
}

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]
    return None

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if auth.login(username, password):
        return jsonify({"message": "登录成功"}), 200
    return jsonify({"message": "登录失败"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if auth.register(username, password):
        return jsonify({"message": "注册成功"}), 201
    return jsonify({"message": "注册失败"}), 400

@app.route('/data', methods=['GET'])
def get_data():
    key = request.args.get('key')
    if key:
        value = redis_client.get(key)
        if value:
            return jsonify({"key": key, "value": value}), 200
        return jsonify({"message": "未找到数据"}), 404
    else:
        keys = redis_client.keys('question_*')
        return jsonify(keys), 200

@app.route('/data', methods=['POST'])
@auth.login_required
def set_data():
    data = request.json
    key = data.get('key')
    value = data.get('value')
    redis_client.set(key, value)
    return jsonify({"message": "数据已保存"}), 201

@app.route('/data', methods=['DELETE'])
@auth.login_required
def delete_data():
    key = request.args.get('key')
    redis_client.delete(key)
    return jsonify({"message": "数据已删除"}), 200



@app.route('/lpop', methods=['POST'])
@auth.login_required
def lpop():
    data = request.json
    key = data.get('key')
    value = redis_client.lpop(key)
    return jsonify({"value": value}), 200

@app.cli.command('get-token')
def get_token():
    """获取验证token"""
    print("Your token is: mysecrettoken")

if __name__ == '__main__':
    app.run(debug=True)