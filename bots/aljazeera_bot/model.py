import re
from models import BaseItem


class AljazeeraModel(BaseItem):

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
