import os
from datetime import datetime, timedelta

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from RPA.Archive import Archive
from robocorp.tasks import get_output_dir
from selenium.common import NoSuchElementException, ElementNotVisibleException, TimeoutException, WebDriverException

from constants import IMAGES_FOLDER_NAME, SHEET_NAME, EXCEL_FILE_PREFIX
from core.exceptions import ScraperStopException
from configs import logger as log


class StorageMixin:
    scraped_data = []
    bot_name = ""

    def __init__(self):
        self.excel = Files()
        self.http = HTTP()
        self.images_folder = f'{get_output_dir()}/{IMAGES_FOLDER_NAME}'
        self.excel_path = f'{get_output_dir()}/{EXCEL_FILE_PREFIX}}.xslx'

    def download_image(self, url):
        image_file = os.path.join(self.images_folder, os.path.basename(url))
        self.http.download(url, image_file)
        return image_file

    def archive_image(self):
        lib = Archive()
        lib.archive_folder_with_zip(self.images_folder, f"{get_output_dir()}/images.zip")

    def convert_to_excel(self):
        """Convert the collected data to an Excel file."""
        if not self.scraped_data:
            return
        self.excel.create_workbook(fmt='xlsx', path=self.excel_path, sheet_name=SHEET_NAME)
        headers = dir(self.scraped_data[0])

        self.excel.append_rows_to_worksheet([headers], SHEET_NAME)

        for article in self.scraped_data:
            row = [
                article.title,
                article.publish_date.strftime("%Y-%m-%d"),
                article.description,
                article.images_folder,
                article.count_search_phrases(self.search_phrase),
                article.contains_money
            ]
            self.excel.append_rows_to_worksheet([row], SHEET_NAME)
        self.excel.save_workbook()

    def store_item(self, item):

        self.scraped_data.append(item)

    def close_browser(self):
        self.convert_to_excel()


class BaseScraper(StorageMixin):

    start_time = datetime.now()

    def __init__(self, config=None):
        """Initialize the BaseScraper with necessary components."""
        self.month = None
        self.search_phrase = None

        self.browser = Selenium()
        self.load_workitems(config)
        super().__init__()

    def main(self):
        """Main method to start the scraping process."""
        start_url = self.get_start_url()

        try:
            self.open_browser(start_url)
            self.parse()
        except ScraperStopException:
            pass
        except (
                NoSuchElementException,
                ElementNotVisibleException,
                TimeoutException,
                WebDriverException,
        ) as e:
            log.error(f"Failed with Exception {e}", exc_info=e)
        finally:
            self.close_browser()

    ##############################
    #  BROWSER CONFIGS           #
    ##############################
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
        except ValueError as e:
            raise ValueError("month should be an Integer/Float rather a string value")

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
        super().close_browser()

    def load_workitems(self, config):
        """Load work items for processing."""
        self.set_search_phrase(config.search_phrase)
        self.set_month(config.month)

    ##############################
    #  SCRAPING                  #
    ##############################

    def element_is_visible(self, xpath, max_retries=5):
        def recursive_wait(tries):
            if tries == 0:
                raise NoSuchElementException(f"Element not found for xpath='{xpath}'")
            try:
                log.debug(f"finding element {xpath}")
                self.browser.wait_until_element_is_visible(xpath)
                return self.browser.is_element_visible(xpath)
            except (NoSuchElementException, AssertionError) as e:
                log.error(f"Error finding element with xpath='{xpath}': {e}")
                log.info(f"tries on xpath:{xpath} tries:{tries - 1}")
                return recursive_wait(tries - 1)

        return recursive_wait(max_retries)
