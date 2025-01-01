from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
import subprocess
import os
import time
from datetime import datetime
from src.extensions import redis_client

scraper_manage_bp = Blueprint('scraper_manage', __name__)

# 全局字典，存储爬虫名称和路径
SCRAPER_SCRIPTS = {
    'question_scraper': '/workspaces/chaoxing/tiku_make/scraper_node/question_scraper.py'
}

# 全局字典，存储可用的redis调度器队列名称
REDIS_QUEUES = {
    'questions': 'question_'
}

@scraper_manage_bp.route('/admin/scraper_manage', methods=['GET'])
@login_required
def scraper_manage():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    scraper_names = list(SCRAPER_SCRIPTS.keys())
    redis_queues = list(REDIS_QUEUES.keys())
    return render_template('admin/scraper_manage.html', scraper_names=scraper_names, redis_queues=redis_queues)

@scraper_manage_bp.route('/admin/scraper_manage/start', methods=['POST'])
@login_required
def start_scraper():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    data = request.json
    scraper_name = data.get('scraper_name')
    scraper_path = SCRAPER_SCRIPTS.get(scraper_name)
    if not scraper_path:
        return jsonify({"message": "爬虫脚本不存在"}), 404
    # 启动爬虫进程
    log_file = f"logs/{scraper_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
    command = f"python3 {scraper_path} > {log_file} 2>&1 &"
    subprocess.Popen(command, shell=True)
    return jsonify({"message": f"{scraper_name} 启动成功"}), 200

@scraper_manage_bp.route('/admin/scraper_manage/stop', methods=['POST'])
@login_required
def stop_scraper():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    data = request.json
    scraper_name = data.get('scraper_name')
    scraper_path = SCRAPER_SCRIPTS.get(scraper_name)
    if not scraper_path:
        return jsonify({"message": "爬虫脚本不存在"}), 404
    # 停止爬虫进程
    command = f"pkill -f {scraper_path}"
    subprocess.Popen(command, shell=True)
    return jsonify({"message": f"{scraper_name} 停止成功"}), 200

@scraper_manage_bp.route('/admin/scraper_manage/restart', methods=['POST'])
@login_required
def restart_scraper():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    data = request.json
    scraper_name = data.get('scraper_name')
    scraper_path = SCRAPER_SCRIPTS.get(scraper_name)
    if not scraper_path:
        return jsonify({"message": "爬虫脚本不存在"}), 404
    # 重启爬虫进程
    stop_command = f"pkill -f {scraper_path}"
    subprocess.Popen(stop_command, shell=True)
    time.sleep(1)
    log_file = f"logs/{scraper_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"
    start_command = f"python3 {scraper_path} > {log_file} 2>&1 &"
    subprocess.Popen(start_command, shell=True)
    return jsonify({"message": f"{scraper_name} 重启成功"}), 200

@scraper_manage_bp.route('/admin/scraper_manage/logs', methods=['GET'])
@login_required
def view_logs():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    scraper_name = request.args.get('scraper_name')
    log_file = f"logs/{scraper_name}.log"
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.read()
        return jsonify({"logs": logs}), 200
    return jsonify({"message": "日志文件不存在"}), 404

@scraper_manage_bp.route('/admin/scraper_manage/add', methods=['POST'])
@login_required
def add_scraper():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    data = request.json
    scraper_name = data.get('scraper_name')
    scraper_params = data.get('scraper_params')
    # 添加爬虫进程
    # ...添加爬虫进程的代码...
    return jsonify({"message": f"{scraper_name} 添加成功"}), 200

@scraper_manage_bp.route('/admin/scraper_manage/refresh', methods=['POST'])
@login_required
def refresh_scraper():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    # 刷新爬虫进程列表
    # ...刷新爬虫进程列表的代码...
    return jsonify({"message": "刷新成功"}), 200

@scraper_manage_bp.route('/admin/scraper_manage/clear', methods=['POST'])
@login_required
def clear_scraper():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    data = request.json
    scraper_names = data.get('scraper_names')
    # 清除爬虫进程
    for scraper_name in scraper_names:
        scraper_path = SCRAPER_SCRIPTS.get(scraper_name)
        if scraper_path:
            command = f"pkill -f {scraper_path}"
            subprocess.Popen(command, shell=True)
    return jsonify({"message": "清除成功"}), 200

@scraper_manage_bp.route('/admin/scraper_manage/test', methods=['POST'])
@login_required
def test_scraper():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    data = request.json
    task = data.get('task')
    queue = data.get('queue')
    queue_prefix = REDIS_QUEUES.get(queue)
    if not queue_prefix:
        return jsonify({"message": "无效的队列名称"}), 400
    # 发送测试任务
    redis_client.lpush(queue, task)
    return jsonify({"message": "测试任务发送成功"}), 200

@scraper_manage_bp.route('/admin/scraper_manage/delete_test_result', methods=['POST'])
@login_required
def delete_test_result():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    data = request.json
    task = data.get('task')
    queue = data.get('queue')
    queue_prefix = REDIS_QUEUES.get(queue)
    if not queue_prefix:
        return jsonify({"message": "无效的队列名称"}), 400
    # 删除测试结果
    redis_client.delete(f"{queue_prefix}{task}")
    return jsonify({"message": "测试结果删除成功"}), 200

@scraper_manage_bp.route('/admin/scraper_manage/update_test_result', methods=['POST'])
@login_required
def update_test_result():
    if not current_user.is_admin:
        return jsonify({"message": "无权限访问"}), 403
    data = request.json
    task = data.get('task')
    queue = data.get('queue')
    queue_prefix = REDIS_QUEUES.get(queue)
    if not queue_prefix:
        return jsonify({"message": "无效的队列名称"}), 400
    # 更新测试结果
    result = redis_client.get(f"{queue_prefix}{task}")
    return jsonify({"task": task, "result": result}), 200
