from flask import Blueprint, request, jsonify, session
from flask_socketio import SocketIO, emit
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from src.models.user import User
from src.study_models import StudySession, StudyProgress
from src.extensions import db
from api.base import Chaoxing, Account
from datetime import datetime

study_bp = Blueprint('study', __name__)
socketio = SocketIO()
jwt = JWTManager()

@study_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        session['chaoxing'] = Chaoxing(Account(username, password))
        access_token = create_access_token(identity=username)
        return jsonify(success=True, token=access_token)
    return jsonify(success=False, message="用户名或密码错误")

@study_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_courses():
    chaoxing = session.get('chaoxing')
    if not chaoxing:
        return jsonify(message="请先登录"), 401
    courses = chaoxing.get_course_list()
    return jsonify(courses=courses)

@study_bp.route('/start', methods=['POST'])
@jwt_required()
def start_study():
    data = request.json
    courses = data.get('courses')
    chaoxing = session.get('chaoxing')
    if not chaoxing:
        return jsonify(success=False, message="请先登录"), 401
    study_session = StudySession(user_id=get_jwt_identity(), start_time=datetime.utcnow(), courses=courses)
    db.session.add(study_session)
    db.session.commit()
    # 启动学习线程
    # ...
    return jsonify(success=True)

@study_bp.route('/progress', methods=['GET'])
@jwt_required()
def get_progress():
    user_id = get_jwt_identity()
    study_session = StudySession.query.filter_by(user_id=user_id, end_time=None).first()
    if not study_session:
        return jsonify(message="没有进行中的学习"), 404
    progress = StudyProgress.query.filter_by(session_id=study_session.id).all()
    total_time = sum([p.duration for p in progress])
    avg_task_time = total_time / len(progress) if progress else 0
    avg_chapter_time = total_time / len(set([p.chapter_id for p in progress])) if progress else 0
    return jsonify(progress=[p.to_dict() for p in progress], totalTime=total_time, avgTaskTime=avg_task_time, avgChapterTime=avg_chapter_time)

@study_bp.route('/stop', methods=['POST'])
@jwt_required()
def stop_study():
    user_id = get_jwt_identity()
    study_session = StudySession.query.filter_by(user_id=user_id, end_time=None).first()
    if not study_session:
        return jsonify(success=False, message="没有进行中的学习"), 404
    study_session.end_time = datetime.utcnow()
    db.session.commit()
    # 停止学习线程
    # ...
    return jsonify(success=True)

@socketio.on('connect')
def handle_connect():
    emit('message', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    emit('message', {'data': 'Disconnected'})

@socketio.on('log')
def handle_log(data):
    user_id = get_jwt_identity()
    study_session = StudySession.query.filter_by(user_id=user_id, end_time=None).first()
    if study_session:
        emit('log', {'data': data}, room=study_session.id)
