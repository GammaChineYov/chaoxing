from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from src.extensions import db
from src.models.user import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403

    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        is_vip = data.get('is_vip', False)
        if User.query.filter_by(username=username).first():
            return jsonify({"message": "用户名已存在"}), 400
        new_user = User(username=username, password=generate_password_hash(password), created_by='admin', is_vip=is_vip)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "用户创建成功"}), 201

    user_count = User.query.count()
    users = User.query.all()
    return render_template('admin.html', user_count=user_count, users=users)

@admin_bp.route('/admin/change_password', methods=['POST'])
@login_required
def change_user_password():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403

    data = request.json
    username = data.get('username')
    new_password = data.get('new_password')
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({"message": "密码修改成功"}), 200
    return jsonify({"message": "用户不存在"}), 404

@admin_bp.route('/admin/usernames', methods=['GET'])
@login_required
def get_usernames():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403

    query = request.args.get('query', '')
    users = User.query.filter(User.username.like(f'%{query}%')).limit(10).all()
    usernames = [user.username for user in users]
    return jsonify(usernames)

@admin_bp.route('/admin/user_info', methods=['GET'])
@login_required
def get_user_info():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403

    username = request.args.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({
            "username": user.username,
            "is_vip": user.is_vip,
            "is_admin": user.is_admin,
            "created_by": user.created_by,
            "password_changed": user.password_changed,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at
        })
    return jsonify({"message": "用户不存在"}), 404

@admin_bp.route('/admin/toggle_vip', methods=['POST'])
@login_required
def toggle_vip():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403

    data = request.json
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        user.is_vip = not user.is_vip
        db.session.commit()
        return jsonify({"message": "VIP 状态切换成功"}), 200
    return jsonify({"message": "用户不存在"}), 404

@admin_bp.route('/admin/toggle_admin', methods=['POST'])
@login_required
def toggle_admin():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403

    data = request.json
    username = data.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        user.is_admin = not user.is_admin
        db.session.commit()
        return jsonify({"message": "管理员状态切换成功"}), 200
    return jsonify({"message": "用户不存在"}), 404
