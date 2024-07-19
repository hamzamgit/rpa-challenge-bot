import inspect
import re
from dataclasses import dataclass, fields
from typing import Iterable, Dict, Any
from datetime import datetime


@dataclass
class BaseItem:
    title:          str
    description:    str
    image_path:     str
    search_phrase:  str
    publish_date:   datetime
    created_at:     datetime = datetime.now()

    def add_value(self, name, value):
        if hasattr(self, name):
            setattr(self, name, value)
        raise AttributeError(f"{name:} not specified")

    def get_headers(self):
        return list(self.load_items().keys())

    def load_items(self) -> Dict[str, Any]:
        """
        Get all fields and properties of the dataclass along with their values.

        Returns:
            dict: A dictionary with attribute names as keys and their corresponding values.
        """

        # Get all dataclass fields
        dataclass_fields = {f.name: getattr(self, f.name) for f in fields(self)}

        # Get all properties
        properties = {
            name: getattr(self, name)
            for name, value in inspect.getmembers(self.__class__, lambda v: isinstance(v, property))
        }

        # Combine both
        return {**dataclass_fields, **properties}
