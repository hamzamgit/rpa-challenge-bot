import re
import time
import os
from dataclasses import dataclass

import requests
from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files

from spiders.aljazeera_spider import AlJazeeraScraper

SEARCH_PHRASE = "iran"


class Locators:
    continue_btn = '//button[@class="css-1fzhd9j"]'
    search_icon = '//button[@data-element="search-button"]'
    search_input = '//input[@data-element="search-form-input"]'
    search_submit = '//button[@data-element="search-submit-button"]'
    # date_dropdown = '//button[@data-testid="search-date-dropdown-a"]'
    see_all_btn = '//p[text()="Topics"]//ancestor::ps-toggler//button[@class="button see-all-button"]'
    topics = '//ul[@data-name="Topics"]//input[@class="checkbox-input-element"]'
    sort_btn = '//select[@class="select-input"]'
    newest_option = '//select[@class="select-input"]//option[text()="Newest"]'
    date_specific = '//button[@value="Specific Dates"]'
    input_start_date = '//input[@id="startDate"]'
    input_end_date = '//input[@id="endDate"]'
    section_btn = '//label[text()="Section"]'
    section_check = '//input[@value="Blogs|nyt://section/7dc9a77b-5567-500d-a633-12f9d14786aa"]'
    search_result = '//div[@class="promo-content"]'
    title = '//h3[@class="promo-title"]'
    description = '//p[@class="promo-description"]'
    date = '//p[@class="promo-timestamp"]'
    image = '//img[@class="image"]'


locate = Locators()


@dataclass
class MyDataClass:
    date: str
    title: str
    desc: str
    image: str
    row: int
    result: bool


class LaTimes:
    def __init__(self):
        self.browser_lib = Selenium()
        self.work_item_lib = WorkItems()
        self.excel_lib = Files()

    def open_browser(self, url):
        self.browser_lib.open_available_browser(url, maximized=True)
        time.sleep(3)

    def input_phrase_data(self):
        self.browser_lib.find_element(locate.search_icon).click()
        self.browser_lib.input_text_when_element_is_visible(locate.search_input, SEARCH_PHRASE)
        self.browser_lib.wait_and_click_button(locate.search_submit)
        time.sleep(3)
        if not self.browser_lib.find_elements(locate.search_result):
            print("Result Not Found!")
            raise BaseException("Result Not Found")

    def sort_by_latest(self):
        self.browser_lib.click_element_when_visible(locate.sort_btn)
        self.browser_lib.click_element_when_visible(locate.newest_option)

    def select_topic(self, topic):
        self.browser_lib.click_element_when_visible(locate.see_all_btn)
        for element in self.browser_lib.find_elements(locate.topics):
            if topic in element.accessible_name:
                time.sleep(2)
                element.click()
                print(element.accessible_name)

    def excel_create(self, data_class: MyDataClass):
        self.excel_lib.set_cell_value(data_class.row, 1, data_class.date)
        self.excel_lib.set_cell_value(data_class.row, 2, data_class.title)
        self.excel_lib.set_cell_value(data_class.row, 3, data_class.desc)
        self.excel_lib.set_cell_value(data_class.row, 4, data_class.image)
        self.excel_lib.set_cell_value(data_class.row, 5, data_class.result)

    def getting_results(self):
        self.excel_lib.create_workbook()
        self.excel_lib.set_cell_value(1, 1, 'Date')
        self.excel_lib.set_cell_value(1, 2, 'Title')
        self.excel_lib.set_cell_value(1, 3, 'Description')
        self.excel_lib.set_cell_value(1, 4, 'Image Path')
        self.excel_lib.set_cell_value(1, 5, 'Price Status')
        self.excel_lib.set_styles("A1:D1", bold=True, font_name="Arial", size=12)
        os.makedirs('./download_data/images', exist_ok=True)
        self.browser_lib.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        pages = self.browser_lib.find_element('//div[@class="search-results-module-page-counts"]').text.split('')[2]
        for _ in range(int(pages)):
            try:
                self.browser_lib.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                row_index = 2
                for i in range(len(self.browser_lib.find_elements(locate.search_result))):
                    time.sleep(3)
                    date_locator = f"({locate.search_result})[{i + 1}]{locate.date}"
                    title_locator = f"({locate.search_result})[{i + 1}]{locate.title}"
                    disc_locator = f"({locate.search_result})[{i + 1}]{locate.description}"
                    img_locator = f"({locate.search_result})[{i + 1}]{locate.image}"
                    date = self.browser_lib.get_text(date_locator)
                    title = self.browser_lib.get_text(title_locator)
                    result = re.search("\$(\w+)", title)
                    result = True if result else False
                    try:
                        disc = self.browser_lib.get_text(disc_locator)
                        result = re.search("\$(\w+)", disc)
                        result = True if result else False
                    except:
                        disc = ""
                    try:
                        image_url = self.browser_lib.get_element_attribute(img_locator, 'src')
                        response = requests.get(image_url)
                        image_path = os.path.join('/home/workspace/RPA/nytime_robot/download_data/images',
                                                  f"image{i}.png")
                        with open(image_path, 'wb') as file:
                            file.write(response.content)
                    except:
                        image_path = "Not available"

                    self.excel_create(MyDataClass(date, title, disc, image_path, row_index, result))
                    row_index += 1
                    self.excel_lib.auto_size_columns("A", "D")
                self.excel_lib.save_workbook("./download_data/ny_time.xlsx")
                self.browser_lib.click_element_when_visible('//div[@class="search-results-module-next-page"]')
            except Exception as e:
                print(str(e))

    def main(self):
        self.open_browser("https://www.latimes.com/")
        time.sleep(3)
        self.input_phrase_data()
        self.select_topic(topic='Lifestyle')
        self.sort_by_latest()
        self.getting_results()


if __name__ == "__main__":
    os.makedirs('./output/images', exist_ok=True)

    scraper = AlJazeeraScraper()
    scraper.main()
    # ny_time = LaTimes()
    # ny_time.main()
