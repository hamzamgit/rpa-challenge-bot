import os
from datetime import datetime, timedelta

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from RPA.Archive import Archive
from robocorp.tasks import get_output_dir
from selenium.common import NoSuchElementException, ElementNotVisibleException, TimeoutException, WebDriverException

from constants import IMAGES_FOLDER_NAME, SHEET_NAME, EXCEL_FILE_PREFIX, DEFAULT_OUTPUT_DIRECTORY, WAIT_TIMEOUT
from core.exceptions import ScraperStopException
from configs import logger as log


class StorageMixin:
    # Class variables shared among all instances

    # List to store scraped data items
    scraped_data = []

    # Name of the bot (can be set by subclasses or instances)
    bot_name = ""

    # Timestamp to create unique folder and file names
    start_time = datetime.now()

    def __init__(self):

        # Files utility for handling Excel operations
        self.excel = Files()

        # HTTP utility for downloading images
        self.http = HTTP()

        # configure file paths
        self._initialize_paths()

    def _initialize_paths(self):

        # Directory to store downloaded images, with a unique timestamp
        output_dir = get_output_dir() if get_output_dir() else DEFAULT_OUTPUT_DIRECTORY
        self.images_folder = f'{output_dir}/{IMAGES_FOLDER_NAME}-{self.start_time.isoformat()}'

        # Create the image folder if it doesn't exist
        os.makedirs(self.images_folder, exist_ok=True)

        # Directory to store archived images.
        self.archive_path = f'{output_dir}/{IMAGES_FOLDER_NAME}-{self.start_time.isoformat()}.zip'

        # Path to save the Excel file, with a unique timestamp
        self.excel_path = f'{output_dir}/{EXCEL_FILE_PREFIX}-{self.start_time.isoformat()}.xlsx'

    def download_image(self, url):

        # Construct local path for the image
        image_file = os.path.join(self.images_folder, os.path.basename(url))

        # Download the image
        self.http.download(url, image_file)

        # Return the local path of the downloaded image
        return image_file

    def archive_image(self):
        # Method to archive the images folder into a zip file

        # Don't archive if no images found
        if not os.listdir(self.images_folder):
            return

        # Initialize Archive utility
        lib = Archive()

        # Archive the images folder
        lib.archive_folder_with_zip(self.images_folder, self.archive_path)

    def convert_to_excel(self):
        """Convert the collected data to an Excel file."""

        if not self.scraped_data:
            log.warning("No data available to compile in Excel File.")  # Log a warning if no data is available
            # If no data is scraped, return early
            return

        self.excel.create_workbook(fmt='xlsx', path=self.excel_path, sheet_name=SHEET_NAME)

        # Get attribute names of the first data item as headers
        headers = self.scraped_data[0].get_headers()

        # Append headers to the Excel sheet
        self.excel.append_rows_to_worksheet(headers, SHEET_NAME)

        for article in self.scraped_data:
            # Prepare a row for each article
            row = list(article.load_items().values())

            # Append the row to the Excel sheet
            self.excel.append_rows_to_worksheet([row], SHEET_NAME)

        # Save the Excel workbook
        self.excel.save_workbook()
        log.info(f"Excel file generated at {self.excel_path}")

    def store_item(self, item):
        # Method to store a scraped item in the class variable list
        self.scraped_data.append(item)  # Add the item to the scraped_data list

    def share_stats(self):
        scraped_content = len(self.scraped_data)
        log.info(f"Total scraped content: {scraped_content}")

    def close_browser(self):

        # Log scraped items
        self.share_stats()

        # archive images folder
        self.archive_image()

        # Compile Excel file for the scraped items.
        self.convert_to_excel()  # Convert scraped data to Excel and save it


class BaseScraper(StorageMixin):

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

        except (NoSuchElementException,
                ElementNotVisibleException,
                TimeoutException,
                WebDriverException) as e:
            log.error(f"Failed with Exception {e}", exc_info=e)

        finally:
            self.close_browser()

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
        except ValueError:
            raise ValueError(f"month:{month} should be an Integer/Float rather a string value")

    @property
    def stop_date(self):
        return datetime.now() - timedelta(days=30 * self.month)

    def parse(self):
        """Method to be implemented by subclasses for parsing logic."""
        raise NotImplementedError("Subclasses must implement this method")
        # This method is meant to be overridden by subclasses to implement specific parsing logic.

    def open_browser(self, link: str):
        """Open the browser with specified options and link."""

        # Opens a browser instance with the provided link using the `open_available_browser` method.
        self.browser.open_available_browser(link)

    def close_browser(self):
        """Close the browser and convert collected data to Excel."""

        log.warning("Closing scraper")

        # Closes all browser instances,
        self.browser.close_all_browsers()
        # calls the supe class's `close_browser` method to trigger all inherited methods.
        super().close_browser()

    def load_workitems(self, config):
        """Load work items for processing."""

        self.set_search_phrase(config.search_phrase)

        self.set_month(config.month)

    def element_is_visible(self, xpath: str, max_retries: int = 5) -> bool:
        """
        Checks if an element identified by XPath is visible on the page.

        Args:
            xpath (str): The XPath expression to locate the element.
            max_retries (int, optional): Maximum number of retries to wait for the element to be visible. Default is 5.

        Returns:
            bool: True if the element is visible, False otherwise.

        Raises:
            NoSuchElementException: If the element is not found after max_retries attempts.

        Example:
            element_is_visible("//div[@id='example']")
            True

            element_is_visible("//div[@id='invalid']")
            Exception NoSuchElementException

        This method recursively attempts to find and check the visibility of an element
        identified by XPath. It retries up to max_retries times. If the element is found
        and visible, it returns True; otherwise, it returns False. If the element is not
        found after all retries, it raises a NoSuchElementException.
        """

        def recursive_wait(tries: int) -> bool:
            # Base case: If no retries left, raise exception
            if tries == 0:
                # No more tries, Exit as Xpath is invalid.
                raise NoSuchElementException(f"Element not found for xpath='{xpath}'")

            try:
                log.debug(f"Finding element {xpath}")
                # Wait until element is visible
                self.browser.wait_until_element_is_visible(xpath, timeout=WAIT_TIMEOUT)

                # Check if element is visible
                return self.browser.is_element_visible(xpath)

            except (NoSuchElementException, AssertionError) as e:
                tries -= 1
                log.error(f"Error finding element with xpath='{xpath}': {e}")
                log.error(f"Tries left for xpath='{xpath}': {tries}")
                return recursive_wait(tries)  # Retry recursively

        return recursive_wait(max_retries)  # Start recursive wait with max_retries

