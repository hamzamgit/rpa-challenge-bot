from selenium.webdriver.common.by import By

from models.base import Item
from spiders.base import BaseScraper, store_articles
from parsel import Selector

SEARCH_PHRASE = "iran"


class AlJazeeraScraper(BaseScraper):
    start_url = 'https://www.aljazeera.com/'
    search_url = 'https://www.aljazeera.com/search/{search}'

    domain = 'https://www.aljazeera.com/'

    cookie_button_xpath = '//button[@id="onetrust-accept-btn-handler"]'
    search_xpath = '//div[@class="site-header__search-trigger"]'
    search_input_xpath = '//input[@class="search-bar__input"]'
    search_submit = '//div[@class="search-bar__button"]/button'
    search_results_xpath = '//div[@class="search-result__list"]/article'
    sort_by_xpath = '//div[@class="search-summary"]'
    sort_by_select_xpath = '//select[@id="search-sort-option"]'
    click_next_button_xpath = '//button[@class="show-more-button grid-full-width"]'
    loading_animation_xpath = '//div[@class="loading-animation"]'

    # article extraction details
    article_title_xpath = './div//h3[@class="gc__title"]'
    article_description_xpath = './div//div[@class="gc__body-wrap"]'
    article_date_xpath = './div//span[@class="screen-reader-text"]'
    article_image_xpath = './div[@class="gc__image-wrap"]//img'

    article_full_title_xpath = '//div[@class="search-result__list"]/article[index:]//h3[@class="gc__title"]'
    article_full_body_xpath = '//div[@class="search-result__list"]/article[index:]//div[@class="gc__body-wrap"]/text()'
    article_full_date_xpath = '//div[@class="search-result__list"]/article[index:]//div[@class="screen-reader-text"]/text()'
    article_full_image_xpath = '//div[@class="search-result__list"]/article[index:]//div[@class="gc__image-wrap"]/text()'

    items_per_page = 10

    # as no page loaded so far
    page = -1

    current_index = 1
    close_spider = True

    def get_start_url(self):
        search_phrase = 'uk'
        return self.search_url.format(search=search_phrase)

    def parse(self):
        # self.input_search_phrase()
        self.accept_cookies()
        self.sort_by_latest()
        while self.close_spider:
            articles = self.browser_get_articles()
            for item in self.extract_articles(articles):
                self.store(item)
            self.click_next_item()
            self.browser.wait_until_element_is_not_visible(self.loading_animation_xpath)

    def accept_cookies(self):
        self.browser.wait_and_click_button(self.cookie_button_xpath)

    def input_search_phrase(self):
        """ Search input window  """
        self.browser.find_element(self.search_xpath).click()
        self.browser.input_text_when_element_is_visible(self.search_input_xpath, SEARCH_PHRASE)
        self.browser.wait_and_click_button(self.search_submit)

    def browser_get_articles(self):
        results = self.wait_for_element_and_get_result(self.search_results_xpath, max_retries=5)
        self.page = self.page + 1
        return results[self.page * self.items_per_page: (self.page + 1) * self.items_per_page]

    def sort_by_latest(self):
        self.wait_for_element_and_get_result(self.sort_by_xpath, max_retries=5)
        self.browser.select_from_list_by_value(self.sort_by_select_xpath, 'date')

    def click_next_item(self):
        # if self.browser.wait_until_page_contains('Show more'):
        # self.wait_for_element_and_get_result(self.click_next_button_xpath)
        self.browser.execute_javascript("window.scrollTo(0, document.body.scrollHeight);")

        if self.browser.is_element_visible(self.click_next_button_xpath):
            self.browser.click_element_when_clickable(self.click_next_button_xpath)

    # @store_articles
    def extract_articles(self, articles):

        for article in articles:
            title = article.find_element(By.XPATH, self.article_title_xpath).text
            description = article.find_element(By.XPATH, self.article_description_xpath).text

            publish_date = article.find_element(By.XPATH, self.article_date_xpath).text if article.find_elements(By.XPATH, self.article_date_xpath) else None
            image_path = article.find_element(By.XPATH, self.article_image_xpath).get_attribute('src')
            image_path = image_path.split('?')[0]
            if 'http' not in image_path:
                image_path = self.domain + image_path

            print(title, description, publish_date, image_path)
            item = Item(title, description, image_path, publish_date)
            yield item
