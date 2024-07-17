import os
from dataclasses import dataclass
from typing import cast

from RPA.Robocorp.WorkItems import WorkItems
from robocorp.workitems import JSONType

from constants import SEARCH_PHRASE, MONTH


@dataclass
class WorkItemInputs:
    search_phrase: str
    month: int

    def __str__(self):
        return f"{self.search_phrase}, {self.month} "


def get_work_items() -> WorkItemInputs:

    def load_work_items() -> JSONType:
        if not os.getenv('ENVIRONMENT') == 'PROD':
            return cast(JSONType, {})

        work_items = WorkItems()
        work_items.get_input_work_item()
        return work_items.get_work_item_payload()

    workitems = load_work_items()
    return WorkItemInputs(
        search_phrase=workitems.get(SEARCH_PHRASE, os.getenv(SEARCH_PHRASE)),
        month=workitems.get(MONTH, os.getenv(MONTH))
    )
