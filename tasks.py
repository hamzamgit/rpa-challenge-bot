import os
from bots.aljazeera_bot import AlJazeeraScraper
from constants import CONFIG_KEYS
from configs import load_work_item_config
from robocorp.tasks import task


def pre_configs():

    """Pre Execution Configs here"""

    os.makedirs('./output/', exist_ok=True)
    os.makedirs('./output/images', exist_ok=True)

    # Load Config from Work items

    if os.getenv('ENVIRONEMENT') == 'PROD':
        pass
    return {
      key: os.getenv(key) for key in CONFIG_KEYS
    }


@task
def extract_news():
    config = pre_configs()
    scraper = AlJazeeraScraper(config=config)
    scraper.main()
