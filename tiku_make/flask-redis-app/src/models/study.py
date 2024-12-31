from datetime import datetime
from src.extensions import db

class StudySession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.now)
    end_time = db.Column(db.DateTime)
    courses = db.Column(db.PickleType)

class StudyProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('study_session.id'), nullable=False)
    course_id = db.Column(db.String(80), nullable=False)
    chapter_id = db.Column(db.String(80), nullable=False)
    task_id = db.Column(db.String(80), nullable=False)
    duration = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'chapter_id': self.chapter_id,
            'task_id': self.task_id,
            'duration': self.duration,
            'timestamp': self.timestamp
        }
