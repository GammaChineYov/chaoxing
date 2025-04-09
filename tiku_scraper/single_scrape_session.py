import os
import json
from urllib.parse import urlparse, urlencode
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from loguru import logger

class SingleScrapeSession:
    """Single-threaded synchronous version for standalone use"""
    def __init__(self):
        self.profile_dir = '/tmp/single_profile'
        if not os.path.exists(self.profile_dir):
            os.makedirs(self.profile_dir)
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 EdgA/131.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        self._setup_browser_prefs()
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)

    def _setup_browser_prefs(self):
        prefs = {
            'profile.default_content_settings.popups': 0,
            'download.default_directory': '/tmp/downloads',
            'profile.managed_default_content_settings.images': 2,
        }
        filepath = os.path.join(self.profile_dir, 'Preferences')
        with open(filepath, 'w') as f:
            json.dump(prefs, f)

    def scrape_question(self, question):
        """Synchronous question scraping"""
        try:
            context = self.browser.new_context(
                user_agent=self.headers["User-Agent"],
                viewport={"width": 1280, "height": 800}
            )
            
            params = {'query': question, 'page': 1, 'pageSize': 10}
            url = f"https://easylearn.baidu.com/edu-page/tiangong/bgklist?{urlencode(params)}"
            
            page = context.new_page()
            page.goto(url)
            page.wait_for_load_state('domcontentloaded')
            
            page.wait_for_selector('.bgk-list-item, .nocontnet-wrap', timeout=10000)

            if page.query_selector('.nocontnet-wrap'):
                return []

            questions = page.query_selector_all('.bgk-list-item')
            
            results = []
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
                    logger.error(f"Error processing question: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return []
        finally:
            if 'page' in locals():
                page.close()
            if 'context' in locals():
                context.close()

    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'browser') and self.browser:
            self.browser.close()
        if hasattr(self, 'playwright') and self.playwright:
            self.playwright.stop()

if __name__ == '__main__':
    # Test the single-threaded version
    scraper = SingleScrapeSession()
    question = "计算机的主机由CPU和( )组成。"
    results = scraper.scrape_question(question)
    print(f"Results for '{question}':")
    for i, result in enumerate(results, 1):
        print(f"{i}. Q: {result['question']}")
        print(f"   A: {result['answer']}")
