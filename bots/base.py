import os
from datetime import datetime, timedelta

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from selenium.common import NoSuchElementException
from RPA.Robocorp.WorkItems import WorkItems
from configs import logger as log
from constants import MONTH, SEARCH_PHRASE


def store_articles(func):
    def wrapper(*args, **kwargs):
        print(f"Starting {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Ending {func.__name__}")
        return result

    return wrapper


class BaseScraper:

    data = []

    def __init__(self, config=None):
        """Initialize the BaseScraper with necessary components."""
        self.browser = Selenium()
        self.http = HTTP()
        self.excel = Files()
        self.work_items = WorkItems()
        # self.config = config
        self.load_workitems(config)

    def main(self):
        """Main method to start the scraping process."""
        start_url = self.get_start_url()
        self.open_browser(start_url)
        self.parse()
        self.close_browser()

    ##############################
    #  CONFIGS                   #
    ##############################
    @property
    def get_start_url(self):
        """Return the starting URL for scraping."""
        if hasattr(self, 'start_url'):
            return self.start_url
        raise ValueError("start_url is not configured")

    def set_search_phrase(self, search_phrase):
        if not search_phrase:
            raise ValueError("search_phrase is not configured")
        self.search_phrase = search_phrase

    def set_month(self, month):
        try:
            self.month = float(month)
        except TypeError as e:
            raise ValueError("month should be an Integer/Float rather string")

    @property
    def stop_date(self):
        return datetime.now() - timedelta(days=30 * self.month)

    def parse(self):
        """Method to be implemented by subclasses for parsing logic."""
        raise NotImplementedError("Subclasses must implement this method")

    def open_browser(self, link):
        """Open the browser with specified options and link."""
        self.browser.open_available_browser(link)

    def close_browser(self):
        """Close the browser and convert collected data to Excel."""
        log.warning("Closing scraper")
        self.browser.close_all_browsers()
        self.convert_to_excel()

    def load_workitems(self, config):
        """Load work items for processing."""
        self.set_search_phrase(config.search_phrase)
        self.set_month(config.month)

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
        self.excel.create_workbook(fmt='xlsx', path='output/Articles.xlsx', sheet_name="News")
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

