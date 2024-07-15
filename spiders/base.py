import os
import re

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from SeleniumLibrary.errors import ElementNotFound
from selenium.common import NoSuchElementException
from RPA.Robocorp.WorkItems import WorkItems
from selenium.webdriver.common.by import By

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
        """Initialize the BaseScraper with necessary components."""
        self.browser = Selenium()
        self.work_item_lib = WorkItems()
        self.http = HTTP()
        self.excel = Files()
        self.excel.create_workbook()
        self.work_items = WorkItems()
        self.data = []

    def main(self):
        """Main method to start the scraping process."""
        start_url = self.get_start_url()
        self.open_browser(start_url)
        try:
            self.parse()
        except Exception as e:
            logger.error(f"Error during parsing: {e}")
        finally:
            self.close_browser()

    ##############################
    #  BROWSER                   #
    ##############################
    def get_start_url(self):
        """Return the starting URL for scraping."""
        return self.start_url

    def parse(self):
        """Method to be implemented by subclasses for parsing logic."""
        raise NotImplementedError("Subclasses must implement this method")

    def open_browser(self, link):
        """Open the browser with specified options and link."""
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
                        "profile.default_content_setting_values.notifications": 2  # Disable notifications
                    }
                }
            }
        }
        self.browser.open_available_browser(link, options=options)

    def close_browser(self):
        """Close the browser and convert collected data to Excel."""
        logger.warning("Closing scraper")
        self.browser.close_all_browsers()
        self.convert_to_excel()

    def load_workitems(self):
        """Load work items for processing."""
        self.work_items.get_work_item_payload()

    ##############################
    #  SCRAPING                  #
    ##############################
    def wait_for_element_and_get_result(self, xpath, max_retries=5):
        """Wait for an element to be visible and return its result.

        Args:
            xpath (str): The XPath of the element.
            max_retries (int): Maximum number of retries for waiting.

        Returns:
            list: List of elements found.

        Raises:
            NoSuchElementException: If the element is not found after retries.
        """
        tries = max_retries
        while tries > 0:
            try:
                if self.browser.find_element(xpath):
                    return self.browser.find_elements(xpath)
                self.browser.wait_until_element_is_visible(xpath)
            except (AssertionError, NoSuchElementException) as e:
                logger.error(f"Error finding element with xpath='{xpath}': {e}")
            tries -= 1
        raise NoSuchElementException(f"Element not found for xpath='{xpath}'")

    ##############################
    #  ARTICLE STORE             #
    ##############################
    def download_image(self, url):
        """Download image from a URL.

        Args:
            url (str): The URL of the image.

        Returns:
            str: Path to the downloaded image file.
        """
        image_file = os.path.join("output/images", os.path.basename(url))
        self.http.download(url, image_file)
        return image_file

    def convert_to_excel(self):
        """Convert the collected data to an Excel file."""
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
                article.contains_money
            ]
            self.excel.append_rows_to_worksheet([row], "News")
        self.excel.close_workbook()

    def store(self, item):
        """Store an item in the data list.

        Args:
            item (dict): The item to store.
        """
        self.data.append(item)
