import re
from dataclasses import dataclass
from typing import Iterable
from datetime import datetime


@dataclass
class Item:
    title: str
    description: str
    image_path: str
    publish_date: datetime
    article_url: int = ''
    scrap_date: str = datetime.now()

    def add_value(self,name, value):
        if hasattr(self, name):
            setattr(self, name, value)
        raise AttributeError(f"{name:} not specified")

    def load_items(self):
        return {item: getattr(self, item) for item in dir(self)}

    def __dir__(self) -> Iterable[str]:
        dirs = super(Item, self).__dir__()
        return [attr for attr in dirs if '__' not in attr]

    def count_search_phrases(self, search_phrase):
        search_phrases = re.findall(search_phrase, f"{self.title} {self.description}", re.IGNORECASE)
        return len(search_phrases)

    @property
    def contains_money(self):
        money_patterns = [
            r"\$\d+(\.\d{1,2})?",
            r"\d+\s+dollars?",
            r"\d+\s+USD"
        ]
        for pattern in money_patterns:
            if re.search(pattern, f"{self.title} {self.description}"):
                return True
        return False