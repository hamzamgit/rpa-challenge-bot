import logging

from bots.aljazeera_bot.constants import ALJAZEERA_DATE_SEPARATORS, ALJAZEERA_SCRAPE_URL
from bots.aljazeera_bot import AljazeeraModel
from bots import BaseScraper
from bots.aljazeera_bot import XpathSelectors

from dateutil.parser import parse as date_parser, ParserError
from selenium.webdriver.common.by import By


log = logging.getLogger(__name__)


class AlJazeeraScraper(BaseScraper, XpathSelectors):
    start_url = ALJAZEERA_SCRAPE_URL
    search_url = '{site_url}search/{search}'
    domain = ALJAZEERA_SCRAPE_URL

    page = -1
    current_index = 1
    items_per_page = 10

    close_spider = False

    def get_start_url(self):
        """Return the formatted start URL for the search."""
        search_phrase = self.search_phrase
        return self.search_url.format(search=search_phrase, site_url=ALJAZEERA_SCRAPE_URL)

    def parse(self):
        """Parse the website to extract article data."""
        self.accept_cookies()
        self.sort_by_latest()
        while not self.close_spider:
            articles = self.browser_get_articles()
            for item in self.extract_articles(articles):
                self.store(item)
            if self.close_spider:
                break
            self.click_next_item()
            self.browser.wait_until_element_is_not_visible(self.loading_animation_xpath, timeout=10)

    def accept_cookies(self):
        """Accept cookies to proceed with the website scraping."""
        if self.browser.is_element_visible(self.cookie_button_xpath):
            self.browser.wait_and_click_button(self.cookie_button_xpath)
            log.debug("Cookie Accept button clicked")
        log.debug("No Cookies Banner found to Click")

    def input_search_phrase(self):
        """ Search input window  """
        self.browser.wait_and_click_button(self.search_icon_xpath)
        self.browser.find_element(self.search_icon_xpath).click()
        self.browser.input_text_when_element_is_visible(self.search_input_xpath, self.search_phrase)
        self.browser.wait_and_click_button(self.search_submit)

    def browser_get_articles(self):
        """Fetch articles from the current search results page."""
        results = self.wait_for_element_and_get_results(self.search_results_xpath, max_retries=5)

        self.page += 1
        log.debug(f"Current page={self.page}")
        start_index = self.page * self.items_per_page
        end_index = start_index + self.items_per_page
        return results[start_index:end_index]

    def sort_by_latest(self):
        """Sort the search results by the latest articles."""
        self.wait_for_element_and_get_result(self.sort_by_xpath, max_retries=5)
        self.browser.select_from_list_by_value(self.sort_by_select_xpath, 'date')
        log.debug("Sort by latest")

    def click_next_item(self):
        """Click the next button to load more articles."""
        self.browser.execute_javascript("window.scrollTo(0, document.body.scrollHeight);")
        if self.browser.is_element_visible(self.click_next_button_xpath):
            self.browser.click_element_when_clickable(self.click_next_button_xpath)
        log.debug("Next button clicked")

    def extract_articles(self, articles):
        """Extract information from each article element."""
        for article in articles:
            title = article.find_element(By.XPATH, self.article_title_xpath).text
            description = article.find_element(By.XPATH, self.article_description_xpath).text
            if ALJAZEERA_DATE_SEPARATORS not in description:
                continue
            publish_date_str = description.split(ALJAZEERA_DATE_SEPARATORS)[0]
            try:
                publish_date = date_parser(publish_date_str, fuzzy=True)
            except (ValueError, ParserError) as e:
                log.error("Invalid Date", exc_info=e)
                continue

            log.debug(f"Check Stop date {self.stop_date} >= {publish_date}: {self.stop_date >= publish_date}")
            if self.stop_date >= publish_date:
                log.debug("Content found till required date")
                self.close_spider = True
                return

            image_url = article.find_element(By.XPATH, self.article_image_xpath).get_attribute('src')
            if 'http' not in image_url:
                image_url = self.domain + image_url
            image_path = self.download_image(image_url)
            log.debug(f"Article extracted: {title}, {publish_date}, {image_path}")
            item = AljazeeraModel(
                title=title,
                description=description,
                image_path=image_path,
                publish_date=publish_date
            )
            yield item
