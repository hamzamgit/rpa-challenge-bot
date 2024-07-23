class XpathSelectors:

    # XPath for the button to accept cookies on the site
    cookie_button_xpath = '//button[@id="onetrust-accept-btn-handler"]'
    # XPath for the search icon/button in the site header
    search_icon_xpath = '//div[@class="site-header__search-trigger"]/button'
    # XPath for the search input field in the search bar
    search_input_xpath = '//input[@class="search-bar__input"]'
    # XPath for the search submit button in the search bar
    search_submit_xpath = '//div[@class="search-bar__button"]/button'
    # XPath for the container holding search result articles
    search_results_xpath = '//div[@class="search-result__list"]/article'
    # XPath for the element containing the sort by options for search results
    sort_by_xpath = '//div[@class="search-summary"]'
    # XPath for the select dropdown to choose sort options
    sort_by_select_xpath = '//select[@id="search-sort-option"]'
    # XPath for the button to load more search results
    click_next_button_xpath = '//button[@class="show-more-button grid-full-width"]'
    # XPath for the loading animation element indicating search results are loading
    loading_animation_xpath = '//div[@class="loading-animation"]'

    # Article Xpaths #

    # XPath for the title of an individual article in the search results
    article_title_xpath = './div//h3[@class="gc__title"]'
    # XPath for the description/body of an individual article in the search results
    article_description_xpath = './div//div[@class="gc__body-wrap"]'
    # XPath for the publication date of an individual article in the search results
    article_date_xpath = './div//span[@class="screen-reader-text"]'
    # XPath for the image of an individual article in the search results
    article_image_xpath = './div[@class="gc__image-wrap"]//img'
