import os
import json
import time
from urllib.parse import urlparse, urlencode
from playwright.sync_api import sync_playwright, Page
from bs4 import BeautifulSoup
from colorama import Fore, Style
from loguru import logger


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
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)

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

    def create_context(self):
        """Create a new browser context"""
        return self.browser.new_context(
            user_agent=self.headers["User-Agent"],
            viewport={"width": 1280, "height": 800},
            bypass_csp=True,
            extra_http_headers=self.headers
        )

    def scrape_question(self, question):
        """Thread-safe scraping with detailed error logging"""
        from threading import get_ident
        import traceback
        from datetime import datetime
        
        logger.info(f"Starting scrape for question: {question}")

        try:
            # Create completely new browser instance per thread
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.headers["User-Agent"],
                    viewport={"width": 1280, "height": 800}
                )
                
                params = {'query': question, 'page': 1, 'pageSize': 10}
                url = f"https://easylearn.baidu.com/edu-page/tiangong/bgklist?{urlencode(params)}"
                logger.debug(f"Scraping URL: {url}")
                
                try:
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
                            logger.error(f"Error processing question element: {str(e)}")
                            logger.trace(f"Element error details: {traceback.format_exc()}")
                    if q:
                        logger.debug(f"Element HTML: {q.inner_html()[:200]}...")
                    
                    logger.info(f"Completed scrape for question: {question}, found {len(results)} results")
                    
                    return results
                    
                except Exception as e:
                    logger.error(f"Page error during scraping: {str(e)}")
                    logger.trace(f"Page error details: {traceback.format_exc()}")
                    if 'page' in locals():
                        logger.debug(f"Page content snippet: {page.content()[:500]}...")
                    return []
                finally:
                    try:
                        page.close()
                        context.close()
                        browser.close()
                    except:
                        pass
        except Exception as e:
            logger.error(f"Browser error during scraping: {str(e)}")
            logger.trace(f"Browser error details: {traceback.format_exc()}")
            return []

    def __del__(self):
        """Clean up resources when object is destroyed"""
        try:
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
