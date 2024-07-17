import os

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from selenium.common import NoSuchElementException
from RPA.Robocorp.WorkItems import WorkItems

import logging


log = logging.getLogger(__name__)


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
        # self.excel.create_workbook()
        self.work_items = WorkItems()
        self.data = []

    def main(self):
        """Main method to start the scraping process."""
        start_url = self.get_start_url()
        self.open_browser(start_url)
        self.parse()
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
        log.warning("Closing scraper")
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
                log.debug("FINDING ELEMENT")
                self.browser.scroll_element_into_view(xpath)
                if result := self.browser.find_element(xpath):
                    log.debug("ELEMENT FOUND AND RETURN")
                    return result
                self.browser.wait_until_element_is_visible(xpath)
            except Exception as e:
                log.error(f"Error finding element with xpath='{xpath}': {e}")
            tries -= 1
            print("TRIES ARE HERE", tries)
        raise NoSuchElementException(f"Element not found for xpath='{xpath}'")

    def wait_for_element_and_get_results(self, xpath, max_retries=5):
        """Wait for an elements to be visible and return its results.

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
                log.debug("FINDING ELEMENT")
                self.browser.wait_until_element_is_visible(xpath)
                self.browser.scroll_element_into_view(xpath)
                if results := self.browser.find_elements(xpath):
                    log.debug("ELEMENT FOUND AND RETURN")
                    return results
            except Exception as e:
                log.error(f"Error finding element with xpath='{xpath}': {e}")
            tries -= 1
        raise NoSuchElementException(f"Element not found for xpath='{xpath}'")

    ##############################
    #  STORE ARTICLE             #
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
        if not self.data:
            return
        self.excel.create_workbook(fmt='xlsx',path='output/Articles.xlsx', sheet_name="News")
        headers = ["Title", "Date", "Description", "Image File", "Search Phrase Count", "Contains Money"]  # generic, Broader ExceptionAvoid, Remove while True use recursion
        self.excel.append_rows_to_worksheet([headers], "News")

        for article in self.data:
            row = [
                article.title,
                article.publish_date.strftime("%Y-%m-%d"),
                article.description,
                article.image_path,
                article.count_search_phrases(self.search_phrase),
                article.contains_money
            ]
            self.excel.append_rows_to_worksheet([row], "News")
        self.excel.save_workbook()

    def store(self, item):
        """Store an item in the data list.

        Args:
            item (dict): The item to store.
        """
        self.data.append(item)