import os
import json
import time
from urllib.parse import urlparse, urlencode
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup
from colorama import Fore, Style
from tiku_make.scraper_node.flask_client import FlaskClient


class QuestionScraper:
    def __init__(self, flask_host='http://localhost:5000', force_flush=False):
        self.force_flush = force_flush
        self.flask_client = FlaskClient(flask_host)
        self.profile_dir = '/tmp/profile'
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)
        self.prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': '/tmp/downloads',
            'profile.managed_default_content_settings.images': 2  # Disable images for faster loading
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 EdgA/131.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "Sec-CH-UA-Platform": "\"Android\"",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
        }
        self.prefs['profile.default_content_setting_values.headers'] = json.dumps(self.headers)
        filepath = os.path.join(self.profile_dir, 'Preferences')
        with open(filepath, 'w') as f:
            json.dump(self.prefs, f)

    def scrape_questions_and_answers(self, question, context):
        params = {
            'query': question,
            'page': 1,
            'pageSize': 10
        }
        url = f"https://easylearn.baidu.com/edu-page/tiangong/bgklist?{urlencode(params)}"
        page: Page = context.new_page()
        page.goto(url)
        page.wait_for_load_state('domcontentloaded')
        # 等待 <div data-v-8da6d952="" class="nocontnet-wrap"> 或者 .bgk-list-item 的元素出现
        page.wait_for_selector('.bgk-list-item, .nocontnet-wrap')
        if page.query_selector('.nocontnet-wrap'):
            # 调试，写入./tiku_make/no_data.html
            print(Fore.YELLOW + f"No questions found for: {question}" + Style.RESET_ALL)
            # with open("./tiku_make/no_data.html", "w") as f:
            #     f.write(page.inner_html("html"))
            page.close()
            return []
        questions = page.query_selector_all('.bgk-list-item')
        if not questions:
            return []
        results = []
        for i, question in enumerate(questions):
            try:
                # question_title = question.query_selector('.item-title').inner_text()
                question_text = question.query_selector('[id^="tigan"]').inner_text()
                answer_text = question.query_selector('[id^="answer"]')
                if not answer_text:
                    answer_text = ""
                else:
                    answer_text = answer_text.inner_text()
                results.append({
                    'question': question_text,
                    'answer': answer_text
                })
            except Exception as e:
                print(Fore.RED + f"An error occurred[{i}]: {e}" + Style.RESET_ALL + "\n")
                print(question.inner_html())
                
        page.close()
        return results
    
    def clean_up_no_answer_entries(self):
        keys = self.flask_client.get_keys()
        if keys:
            for key in keys:
                if not key.startswith("question_"):
                    continue
                data = self.flask_client.get_data(key)["value"]
                data = json.loads(data)
                if not data or not any([d.get('answer') for d in data]):
                    print(Fore.YELLOW + f"Deleting key: {key}" + Style.RESET_ALL)
                    self.flask_client.delete_data(key)
    
    def process_questions(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context_config = {
                "user_agent": self.headers["User-Agent"],
                "locale": "en-US",
                "viewport": {"width": 1280, "height": 800},
                "bypass_csp": True,
                "extra_http_headers": self.headers
            }
            context = browser.new_context(**context_config)
            print(Fore.GREEN + "Started processing questions..." + Style.RESET_ALL)
            while True:
                try:
                    response = self.flask_client.get_unique_question()
                    question = response.get('question')
                    if question:
                        print(Fore.GREEN + f"INFO: Processing question: {question}" + Style.RESET_ALL)
                        context = browser.new_context(**context_config)
                        questions_and_answers = self.scrape_questions_and_answers(question, context)
                        context.close()
                        answers = json.dumps(questions_and_answers, ensure_ascii=False)
                        print(Fore.GREEN + f"INFO: Got answers for question: {question}" + Style.RESET_ALL)
                        print(answers)
                        self.flask_client.set_data("question_" + question, answers)
                    else:
                        time.sleep(1)
                except KeyboardInterrupt:
                    break
            browser.close()

if __name__ == "__main__":
    scraper = QuestionScraper()
    scraper.clean_up_no_answer_entries()
    scraper.process_questions()
