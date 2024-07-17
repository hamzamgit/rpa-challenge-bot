import os
from bots.aljazeera_news_bot import AlJazeeraScraper
from constants import CONFIG_KEYS


def pre_configs():

    """Pre Execution Configs here"""
    os.makedirs('./output/images', exist_ok=True)

    # Load Config from Work items
    return {
      key: os.getenv(key) for key in CONFIG_KEYS
    }


if __name__ == "__main__":
    config = pre_configs()
    scraper = AlJazeeraScraper(config=config)
    scraper.main()
