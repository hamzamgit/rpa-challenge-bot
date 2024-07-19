from bots.aljazeera_bot.constants import (
    ALJAZEERA_DATE_SEPARATORS,
    ALJAZEERA_SCRAPE_URL,
    ITEMS_PER_PAGE,
    SORT_BY_ARTICLES
)
from bots.aljazeera_bot.model import AljazeeraModel
from bots.aljazeera_bot.utils import parse_date_string
from core.base import BaseScraper
from bots.aljazeera_bot import XpathSelectors
from configs.loggers import logger as log

from RPA.Browser.Selenium import By

from core.exceptions import ScraperStopException


class AlJazeeraScraper(BaseScraper, XpathSelectors):
    # Class to scrape Al Jazeera website, inheriting from BaseScraper and XpathSelectors

    domain = start_url = ALJAZEERA_SCRAPE_URL  # Set domain and start URL
    page = -1  # Initialize page counter
    items_per_page = ITEMS_PER_PAGE  # Set number of items per page
    bot_name = 'AljazeeraNews'  # Set bot name
    close_spider = False  # Flag to indicate when to stop scraping

    def parse(self):
        """Parse the website to extract article data."""

        # Accept cookies if prompted
        self.accept_cookies()

        # Enter search phrase in search bar
        self.input_search_phrase()

        # Wait for search results to load on next page
        self.wait_for_search_items_to_load()

        # Sort search results by latest articles
        self.sort_by_latest()

        # Start parsing articles
        self.parse_articles()

    def parse_articles(self):
        """Recursively parse the pages until a stop condition is met."""
        # Stop parsing if no more articles are found and it's not the first page
        if self.page != -1 and not self.browser.is_element_visible(self.search_results_xpath):
            raise ScraperStopException("No more articles.")

        # Get articles from the current page
        articles = self.select_articles_from_page()

        # Extract information from each article
        for item in self.extract_articles(articles):
            # Continue to the next page if the spider should not be closed
            if not self.close_spider:
                self.store_item(item)  # Store the extracted item

        self.click_next_item()  # Click the next button to load more articles
        self.browser.wait_until_element_is_not_visible(self.loading_animation_xpath, timeout=10)
        self.parse_articles()  # Recursively parse the next page of articles

    def accept_cookies(self):
        # Click the accept cookies button if visible
        if self.element_is_visible(self.cookie_button_xpath):
            self.browser.click_button_when_visible(self.cookie_button_xpath)
            log.debug("Cookie Accept button clicked")
        log.debug("No Cookies Banner found to Click")

    def wait_for_search_items_to_load(self):
        # Wait until search items are visible, with up to 10 retries
        self.element_is_visible(self.sort_by_xpath, max_retries=10)

    def input_search_phrase(self):
        # Enter the search phrase in the search input
        self.element_is_visible(self.search_icon_xpath)
        self.browser.find_element(self.search_icon_xpath).click()
        self.element_is_visible(self.search_input_xpath)
        self.browser.input_text_when_element_is_visible(self.search_input_xpath, self.search_phrase)
        self.browser.click_button_when_visible(self.search_submit_xpath)

    def sort_by_latest(self):
        # Sort search results by date
        self.element_is_visible(self.sort_by_xpath, max_retries=5)
        self.browser.select_from_list_by_value(self.sort_by_select_xpath, SORT_BY_ARTICLES)
        log.debug("Sort by latest")

    def click_next_item(self):
        # Scroll to the bottom of the page and click the next button if visible
        self.browser.execute_javascript("window.scrollTo(0, document.body.scrollHeight);")
        if self.element_is_visible(self.click_next_button_xpath):
            self.browser.click_element_when_clickable(self.click_next_button_xpath)
            log.debug("Next button clicked")
            self.browser.wait_until_element_is_not_visible(self.loading_animation_xpath, timeout=5)
            return True
        raise ScraperStopException("No further elements to be scraped")

    def select_articles_from_page(self):
        """
        Selects and returns a slice of articles from the current search results page.

        Returns:
            list: A list of article elements from the current page.

        Optimizations:
            - Added comments to clarify each step in the function.
            - Removed unnecessary comments that merely restated the code.
        """
        # Ensure search results are visible on the page
        self.element_is_visible(self.search_results_xpath, max_retries=5)

        # Find all article elements on the current page
        results = self.browser.find_elements(self.search_results_xpath)

        # Increment page counter for pagination tracking
        self.page += 1
        log.debug(f"Current page={self.page}")

        # Calculate indices to slice the results based on pagination
        start_index = self.page * self.items_per_page
        end_index = start_index + self.items_per_page

        # Return a slice of the results based on the current page
        return results[start_index:end_index]

    def extract_articles(self, articles):
        """
        Extracts information from each article element and yields an AljazeeraModel item.

        Args:
            articles (list): List of article elements to extract information from.

        Yields:
            AljazeeraModel: An instance of AljazeeraModel containing extracted article information.

        Optimizations:
            - Added comments to clarify each step in the function.
            - Removed unnecessary comments that merely restated the code.
        """
        for article in articles:
            # Extract article description
            description = article.find_element(By.XPATH, self.article_description_xpath).text

            # Skip articles without publish date in the description
            if ALJAZEERA_DATE_SEPARATORS not in description:
                log.error(f"Article does not contain Publish Date description: {description}")
                continue

            # Extract and parse publish date from the description
            publish_date_str = self.get_publish_date(description)
            publish_date = parse_date_string(publish_date_str)

            # Check if the article's publish date is beyond the stop date
            log.debug(f"Check Stop date {self.stop_date} >= {publish_date}: {self.stop_date >= publish_date}")
            if self.stop_date >= publish_date:
                log.info("Content found till required date")
                self.close_spider = True
                return

            # Extract article title
            title = article.find_element(By.XPATH, self.article_title_xpath).text

            # Extract and process article image URL
            image_src = article.find_element(By.XPATH, self.article_image_xpath).get_attribute('src')
            image_path = self.get_image_path(image_src)

            # Log the extraction details
            log.info(f"Article extracted: {title}, {publish_date}, {image_path}")

            # Create and yield an instance of Model
            item = AljazeeraModel(
                title=title,
                description=description,
                image_path=image_path,
                publish_date=publish_date,
                search_phrase=self.search_phrase
            )
            yield item  # Yield the extracted article item

    def get_publish_date(self, text) -> str:
        # extract publish date from Description.
        return text.split(ALJAZEERA_DATE_SEPARATORS)[0]

    def get_image_path(self, image_url) -> str:
        # Add domain to the relative image src
        if 'http' not in image_url:
            image_url = self.domain + image_url  # Ensure the image URL is complete

        # Download the article image
        return self.download_image(image_url)
