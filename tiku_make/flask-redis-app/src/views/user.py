from flask import Blueprint, request, jsonify, render_template, redirect, url_for, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from src.extensions import db
from src.models.user import User
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_login_at = datetime.now()
            db.session.commit()
            if user.is_admin and not user.password_changed:
                return jsonify({"message": "请尽快修改默认管理员密码"}), 200
            return jsonify({"message": "登录成功"}), 200
        return jsonify({"message": "用户名或密码错误"}), 401
    return render_template('user/login.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))

@user_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        data = request.json
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if check_password_hash(current_user.password, old_password):
            current_user.password = generate_password_hash(new_password)
            current_user.password_changed = True
            db.session.commit()
            return jsonify({"message": "密码修改成功"}), 200
        return jsonify({"message": "旧密码错误"}), 401
    return render_template('user/change_password.html')
