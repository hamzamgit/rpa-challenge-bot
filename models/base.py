from dataclasses import dataclass
from typing import Iterable
from datetime import datetime


@dataclass
class Item:
    title: str
    description: str
    image_path: str
    publish_date: str
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
