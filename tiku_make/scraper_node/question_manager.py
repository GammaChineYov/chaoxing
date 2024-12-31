import redis
import json
import time
from urllib.parse import urlparse

class QuestionManager:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0, redis_password='question_scraper'):
        parsed_url = urlparse(redis_host) 
        redis_host = parsed_url.hostname  # Use hostname instead of full URL
        self.redis_client = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True
        )

    def send_question(self, question):
        # Check if the answer already exists
        answer = self.redis_client.get(question)
        if answer:
            return json.loads(answer)
        # If no answer exists, send the question
        self.redis_client.rpush('questions', question)
        return None

    def wait_for_answer(self, question, timeout=30):
        start_time = time.time()
        while time.time() - start_time < timeout:
            answer = self.redis_client.get("question_" + question)
            if answer:
                return json.loads(answer)
            time.sleep(1)
        return None

if __name__ == "__main__":
    manager = QuestionManager()
    question = "】交通事故中，如果遇到肇事车辆逃逸，作为目击者要尽可能记清逃逸车辆的（ ）、颜色、车型等特征，为警察提供线索。"
    answer = manager.send_question(question)
    if not answer:
        answer = manager.wait_for_answer(question)
    if answer:
        print(answer)
    else:
        print("Failed to get an answer within the timeout period.")