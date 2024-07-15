import os
from spiders.aljazeera_spider import AlJazeeraScraper


if __name__ == "__main__":
    os.makedirs('./output/images', exist_ok=True)

    scraper = AlJazeeraScraper()
    scraper.main()
