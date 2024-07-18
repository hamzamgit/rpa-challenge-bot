class ScraperStopException(Exception):
    """Custom exception to stop the scraper when a specific condition is met."""
    def __init__(self, message="Scraper stop condition met"):
        self.message = message
        super().__init__(self.message)
