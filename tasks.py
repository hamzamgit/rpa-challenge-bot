from bots.aljazeera_bot.bot import AlJazeeraScraper
from configs import get_work_items, setup_logger, logger
from robocorp.tasks import task, get_output_dir

from constants import DEFAULT_OUTPUT_DIRECTORY


def pre_configs():

    """Pre Execution Configs here"""

    # configure logger
    output_dir = get_output_dir() if get_output_dir() else DEFAULT_OUTPUT_DIRECTORY
    setup_logger(output_dir)
    # Load Config from Work items
    return get_work_items()


@task
def run_news_scraper_bot():
    config = pre_configs()
    logger.info("Task Started")
    # x = AljazeeraModel(title='title', search_phrase='de', description='descr 10 USD', image_path='path', publish_date=datetime.datetime.now())

    scraper = AlJazeeraScraper(config=config)
    scraper.main()
    logger.info("Task Completed")


run_news_scraper_bot()
