import re
from models import BaseItem


class AljazeeraModel(BaseItem):

    @property
    def count_search_phrases(self) -> int:
        search_phrases = re.findall(self.search_phrase, f"{self.title} {self.description}", re.IGNORECASE)
        return len(search_phrases)

    @property
    def contains_money(self) -> bool:
        money_pattern = re.compile(
            r"\$\d+(\.\d{1,2})?|"
            r"\d+\s+dollars?|"
            r"\d+\s+USD"
        )
        return bool(money_pattern.search(f"{self.title} {self.description}"))

