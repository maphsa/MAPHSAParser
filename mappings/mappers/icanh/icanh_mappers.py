import re

from unidecode import unidecode

from exceptions import MAPHSAMissingMappingException


class ICANHMapper:
    source_name: str
    field_mappings: dict = None

    def __init__(self, _mappings: dict, _source_name: str = "Unnamed"):
        self.load_mappings(_mappings)
        self.source_name = _source_name

    def load_mappings(self, _mappings: dict):
        self.field_mappings = _mappings

    def filter_source_value(self, source_value: str) -> str:
        # source_value = unidecode(source_value)
        # source_value = source_value.lower().strip()
        # source_value = re.sub(r'[.,()¿?]', '', source_value)
        return source_value

    def get_field_mapping(self, _source_value: str) -> str:

        source_value = self.filter_source_value(_source_value)

        if source_value not in self.field_mappings.keys():
            self.report_missing_value(_source_value, source_value)

        return self.field_mappings[source_value] if source_value in self.field_mappings.keys() else None

    def report_missing_value(self, _source_value, source_value):
        message = f"Unable to find mapping in {self.source_name} for value {_source_value} as {source_value}"
        raise MAPHSAMissingMappingException(message, _source_value, source_value)

    @classmethod
    def split_source_value(cls, source_value: str) -> list:
        raise NotImplemented("Abstract method")
