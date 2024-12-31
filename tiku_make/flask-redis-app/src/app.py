import os 
import sys
import json
sys.path.append(os.path.dirname(__file__))
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
from redis_client import RedisClient
from views.redis import redis_blueprint
from views.token import token_blueprint
from src.extensions import redis_client
from src.extensions import db
from src.models.user import User
from src.views.user import user_bp
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, current_user
from src.views.admin import admin_bp
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from src.views.study import study_bp, socketio, jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'

db.init_app(app)
socketio.init_app(app)
jwt.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password=generate_password_hash('admin'), is_admin=True)
        db.session.add(admin)
        db.session.commit()

app.register_blueprint(redis_blueprint, url_prefix='/redis')
app.register_blueprint(token_blueprint, url_prefix='/token')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(study_bp, url_prefix='/study')

CORS(app)

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('user.login'))
    return render_template('index.html')


@app.cli.command('get-token')
def get_token():
    """获取验证token"""
    print("Your token is: mysecrettoken")


if __name__ == '__main__':
    socketio.run(app, debug=True)