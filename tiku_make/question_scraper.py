import os
import json
import time
from urllib.parse import urlparse, urlencode
from playwright.sync_api import sync_playwright, Page

from bs4 import BeautifulSoup
from colorama import Fore, Style 

class ScrapeSession:
    """Handles browser session and core scraping logic"""
    def __init__(self):
        self.profile_dir = '/tmp/profile'
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)
        
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
        self._setup_browser_prefs()

    def _setup_browser_prefs(self):
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': '/tmp/downloads',
            'profile.managed_default_content_settings.images': 2,
            'profile.default_content_setting_values.headers': json.dumps(self.headers)
        }
        filepath = os.path.join(self.profile_dir, 'Preferences')
        with open(filepath, 'w') as f:
            json.dump(prefs, f)

    def __init__(self):
        self.profile_dir = '/tmp/profile'
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)
        
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
        self._setup_browser_prefs()
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)

    def create_context(self):
        """Create a new browser context"""
        return self.browser.new_context(
            user_agent=self.headers["User-Agent"],
            viewport={"width": 1280, "height": 800},
            bypass_csp=True,
            extra_http_headers=self.headers
        )

    def scrape_question(self, question, context=None):
        """Core scraping logic for a single question"""
        params = {'query': question, 'page': 1, 'pageSize': 10}
        url = f"https://easylearn.baidu.com/edu-page/tiangong/bgklist?{urlencode(params)}"
        
        if context is None:
            context = self.create_context()
            close_context = True
        else:
            close_context = False

        try:
            if self.browser.is_connected():
                page = context.new_page()
                page.goto(url)
                page.wait_for_load_state('domcontentloaded')
                
                page.wait_for_selector('.bgk-list-item, .nocontnet-wrap', timeout=10000)

                if page.query_selector('.nocontnet-wrap'):
                    page.close()
                    return []

                questions = page.query_selector_all('.bgk-list-item')
                
                results = []
                if not questions:
                    return []
                for q in questions:
                    try:
                        question_text = q.query_selector('[id^="tigan"]').inner_text()
                        answer_text = q.query_selector('[id^="answer"]')
                        answer_text = answer_text.inner_text() if answer_text else ""
                        results.append({
                            'question': question_text,
                            'answer': answer_text
                        })
                    except Exception as e:
                        import traceback
                        error_msg = f"Error processing question at line {traceback.extract_tb(e.__traceback__)[-1].lineno}: {str(e)}"
                        print(error_msg)
                        print(f"Full traceback:\n{''.join(traceback.format_tb(e.__traceback__))}")
                return results
            else:
                raise Exception("Browser is not connected")
        except Exception as e:
            import traceback
            error_msg = f"Error during scraping at line {traceback.extract_tb(e.__traceback__)[-1].lineno}: {str(e)}"
            print(error_msg)
            print(f"Full traceback:\n{''.join(traceback.format_tb(e.__traceback__))}")
            return []
        finally:
            try:
                if close_context and context:
                    context.close()
            except Exception as e:
                print(f"Error closing context: {str(e)}")

    def __del__(self):
        """Clean up resources when object is destroyed"""
        try:
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")


class FlaskScraper:
    """Handles Flask integration and scraping task management"""
    def __init__(self, flask_host='http://localhost:5000'):
        from flask_client import FlaskClient
        self.scrape_session = ScrapeSession()
        self.flask_client = FlaskClient(flask_host)

    def clean_up_no_answer_entries(self):
        """Clean up entries with no answers"""
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
        """Main processing loop for Flask integration"""
        print(Fore.GREEN + "Started processing questions..." + Style.RESET_ALL)
        while True:
            try:
                response = self.flask_client.get_unique_question()
                question = response.get('question')
                if question:
                    print(Fore.GREEN + f"INFO: Processing question: {question}" + Style.RESET_ALL)
                    answers = self.scrape_session.scrape_question(question)
                    self.flask_client.set_data("question_" + question, json.dumps(answers))
                else:
                    time.sleep(1)
            except KeyboardInterrupt:
                break


if __name__ == "__main__":
    scraper = FlaskScraper()
    scraper.clean_up_no_answer_entries()
    scraper.process_questions()
