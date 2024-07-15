import re

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from SeleniumLibrary.errors import ElementNotFound
from selenium.common import NoSuchElementException
from RPA.Robocorp.WorkItems import WorkItems


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
        self.excel = Files()
        self.excel.create_workbook()
        self.work_items = WorkItems()

    def main(self):
        start_url = self.get_start_url()
        self.open_browser(start_url)
        self.parse()

    ###############
    #   BROWSER   #
    ###############
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
        self.browser.close_all_browsers()

    def load_workitems(self):
        self.work_items.get_work_item_payload()

    ###############
    #  SCRAPING   #
    ###############
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

    def _count_search_phrases(self, title, description):
        if not self.search_phrase:
            raise NotImplemented('Search phrase not found or defined.')
        search_phrases = re.findall(self.search_phrase, f"{title} {description}", re.IGNORECASE)
        return len(search_phrases)

    def _contains_money(self, title, description):
        money_patterns = [
            r"\$\d+(\.\d{1,2})?",
            r"\d+\s+dollars?",
            r"\d+\s+USD"
        ]
        for pattern in money_patterns:
            if re.search(pattern, f"{title} {description}"):
                return True
        return False

    ###############
    # DATA STORE  #
    ###############

    def convert_to_excel(self):
        pass
    # def sort_by_latest(self):
    #     self.browser.click_element_when_visible(locate.sort_btn)
    #     self.browser.click_element_when_visible(locate.newest_option)
    #
    # def select_topic(self, topic):
    #     self.browser.click_element_when_visible(locate.see_all_btn)
    #     for element in self.browser.find_elements(locate.topics):
    #         if topic in element.accessible_name:
    #             time.sleep(2)
    #             element.click()
    #             print(element.accessible_name)
    #
    # def excel_create(self, data_class: MyDataClass):
    #     self.excel.set_cell_value(data_class.row, 1, data_class.date)
    #     self.excel.set_cell_value(data_class.row, 2, data_class.title)
    #     self.excel.set_cell_value(data_class.row, 3, data_class.desc)
    #     self.excel.set_cell_value(data_class.row, 4, data_class.image)
    #     self.excel.set_cell_value(data_class.row, 5, data_class.result)
    #
    # def getting_results(self):
    #     self.excel.create_workbook()
    #     self.excel.set_cell_value(1, 1, 'Date')
    #     self.excel.set_cell_value(1, 2, 'Title')
    #     self.excel.set_cell_value(1, 3, 'Description')
    #     self.excel.set_cell_value(1, 4, 'Image Path')
    #     self.excel.set_cell_value(1, 5, 'Price Status')
    #     self.excel.set_styles("A1:D1", bold=True, font_name="Arial", size=12)
    #     os.makedirs('./download_data/images', exist_ok=True)
    #     self.browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     pages = self.browser.find_element('//div[@class="search-results-module-page-counts"]').text.split('')[2]
    #     for _ in range(int(pages)):
    #         try:
    #             self.browser.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #             row_index = 2
    #             for i in range(len(self.browser.find_elements(locate.search_result))):
    #                 time.sleep(3)
    #                 date_locator = f"({locate.search_result})[{i + 1}]{locate.date}"
    #                 title_locator = f"({locate.search_result})[{i + 1}]{locate.title}"
    #                 disc_locator = f"({locate.search_result})[{i + 1}]{locate.description}"
    #                 img_locator = f"({locate.search_result})[{i + 1}]{locate.image}"
    #                 time.sleep(3)
    #                 date = self.browser.get_text(date_locator)
    #                 title = self.browser.get_text(title_locator)
    #                 result = re.search("\$(\w+)", title)
    #                 result = True if result else False
    #                 try:
    #                     disc = self.browser.get_text(disc_locator)
    #                     result = re.search("\$(\w+)", disc)
    #                     result = True if result else False
    #                 except:
    #                     disc = ""
    #                 try:
    #                     image_url = self.browser.get_element_attribute(img_locator, 'src')
    #                     response = requests.get(image_url)
    #                     image_path = os.path.join('/home/workspace/RPA/nytime_robot/download_data/images',
    #                                               f"image{i}.png")
    #                     with open(image_path, 'wb') as file:
    #                         file.write(response.content)
    #                 except:
    #                     image_path = "Not available"
    #
    #                 self.excel_create(MyDataClass(date, title, disc, image_path, row_index, result))
    #                 row_index += 1
    #                 self.excel.auto_size_columns("A", "D")
    #             self.excel.save_workbook("./download_data/ny_time.xlsx")
    #             self.browser.click_element_when_visible('//div[@class="search-results-module-next-page"]')
    #         except Exception as e:
    #             print(str(e))

    data = []

    def store(self, item):
        self.data.append(item)

    # @log_decorator
    # def my_generator(n):
    #     for i in range(n):
    #         yield i
    #
    # # Using the decorated generator
    # gen = my_generator(5)
    # for value in gen:
    #     print(value)
