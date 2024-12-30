import requests

class FlaskClient:
    def __init__(self, flask_host='http://localhost:5000', token='mysecrettoken'):
        self.flask_host = flask_host
        self.headers = {
            'Authorization': f'Bearer {token}'
        }

    def get_data(self, key):
        response = requests.get(f"{self.flask_host}/redis/data?key={key}", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def set_data(self, key, value):
        data = {'key': key, 'value': value}
        response = requests.post(f"{self.flask_host}/redis/data", json=data, headers=self.headers)
        return response.status_code == 201

    def delete_data(self, key):
        response = requests.delete(f"{self.flask_host}/redis/data?key={key}", headers=self.headers)
        return response.status_code == 200

    def get_keys(self, pattern='question_*'):
        response = requests.get(f"{self.flask_host}/redis/data", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def lpop(self, key):
        response = requests.post(f"{self.flask_host}/redis/lpop", json={'key': key}, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('value')
        return None

    def get_unique_question(self):
        response = requests.post(f"{self.flask_host}/redis/get_unique_question", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def clean_up_no_answer_entries(self):
        response = requests.post(f"{self.flask_host}/redis/clean_up_no_answer_entries", headers=self.headers)
        return response.status_code == 200