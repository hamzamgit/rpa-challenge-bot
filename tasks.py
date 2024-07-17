import os
from bots.aljazeera_bot.bot import AlJazeeraScraper
from configs import get_work_items, logger
from robocorp.tasks import task, get_output_dir


def pre_configs():

    """Pre Execution Configs here"""

    # Create empty directory for images.
    os.makedirs(f'{get_output_dir()}/images', exist_ok=True)
    # Load Config from Work items

    return get_work_items()


@task
def run_news_scraper_bot():
    logger.info("Task Started")
    config = pre_configs()
    scraper = AlJazeeraScraper(config=config)
    scraper.main()
    logger.info("Task Completed")

run_news_scraper_bot()