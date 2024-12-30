from flask_sqlalchemy import SQLAlchemy
from src.redis_client import RedisClient

redis_client = RedisClient(password='question_scraper')
db = SQLAlchemy()
