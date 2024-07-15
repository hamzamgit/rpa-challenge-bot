import os
import re

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from SeleniumLibrary.errors import ElementNotFound
from selenium.common import NoSuchElementException
from RPA.Robocorp.WorkItems import WorkItems

import logging

logger = logging.getLogger(__name__)


def store_articles(func):
    def wrapper(*args, **kwargs):
        print(f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Ending {func.__name__}")
        return result

    return wrapper


class BaseScraper:
    def __init__(self):
        self.browser = Selenium()
        self.work_item_lib = WorkItems()
        self.http = HTTP()
        self.excel = Files()
        self.excel.create_workbook()
        self.work_items = WorkItems()

    def main(self):
        start_url = self.get_start_url()
        self.open_browser(start_url)
        try:
            self.parse()
        except Exception as e:
            logger.error(e)
        finally:
            self.close_browser()

    ##############################
    #  BROWSER                   #
    ##############################
    def get_start_url(self):
        return self.start_url

    def parse(self):
        raise NotImplemented()

    def open_browser(self, link):
        options = {
            "arguments": [
                "--disable-gpu",
                "--disable-extensions",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-animations",
                "--disable-images"
            ],
            "capabilities": {
                "goog:chromeOptions": {
                    "prefs": {
                        "profile.managed_default_content_settings.images": 2,  # Disable images
                        "profile.default_content_setting_values.notifications": 2,  # Disable notifications
                    }
                }
            }
        }
        self.browser.open_available_browser(link, options=options)

    def close_browser(self):
        logger.warning("CLOSING SCRAPER")
        self.browser.close_all_browsers()
        self.convert_to_excel()

    def load_workitems(self):
        self.work_items.get_work_item_payload()

    ##############################
    #  SCRAPING                  #
    ##############################
    def wait_for_element_and_get_result(self, xpath, max_retries=5):
        tries = max_retries
        while tries >= 0:
            try:
                if self.browser.find_element(xpath):
                    return self.browser.find_elements(xpath)
                self.browser.wait_until_element_is_visible(x)
                tries = tries - 1
            except (AssertionError, ElementNotFound) as e:
                pass
        raise NoSuchElementException(f"Element not found for xpath='{xpath}'")

    ##############################
    #  ARTICLE STORE             #
    ##############################

    def download_image(self, url):
        image_file = os.path.join("output/images", os.path.basename(url))
        self.http.download(url, image_file)
        return image_file

    def convert_to_excel(self):
        self.excel.create_workbook()

        headers = ["Title", "Date", "Description", "Image File", "Search Phrase Count", "Contains Money"]

        self.excel.append_rows_to_worksheet([headers], "News")

        for article in self.data:
            row = [
                article["title"],
                article["date"].strftime("%Y-%m-%d"),
                article["description"],
                article["image_path"],
                article.count_search_phrases(self.search_phrase),
                article.count_search_phrases(self.search_phrase),
                article.contains_money
            ]
            self.excel.append_rows_to_worksheet([row], "News")
        self.excel.close_workbook()

    data = []

    def store(self, item):
        self.data.append(item)
