import re
from unidecode import unidecode

from exceptions import MAPHSAMissingMappingException


class Mapper:
    source_name: str
    field_mappings: dict = None

    def __init__(self, _mappings: dict, _source_name: str = "Unnamed"):
        self.load_mappings(_mappings)
        self.source_name = _source_name

    def load_mappings(self, _mappings: dict):
        self.field_mappings = _mappings

    def filter_source_value(self, source_value: str) -> str:
        source_value = unidecode(source_value)
        source_value = source_value.lower().strip()
        source_value = re.sub(r'[.,()¿?]', '', source_value)
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


class MultiValueMapper(Mapper):

    def get_field_mappings(self, source_value: str):
        raise NotImplemented("Abstract method")


class PreviousResearchActivitiesMapper(Mapper):

    @classmethod
    def split_source_value(cls, source_value: str) -> list:
        source_value = re.sub(r'[()\[\]]', '', source_value)
        source_value_items = source_value.split('&')

        if len(source_value_items) == 1:
            if '_' in source_value or ', ' in source_value:
                source_value_items = source_value.split(',')
                source_value_items = [svi.replace('_', ' ').strip() for svi in source_value_items]
                source_value_items = filter(None, source_value_items)

        return source_value_items


class CulturalAffiliationMapper(MultiValueMapper):
    def get_field_mappings(self, source_value: str) -> set:

        mapped_values: set = set()
        filtered_source_value = self.filter_source_value(source_value)

        for va_value in self.field_mappings.keys():
            pattern = r"\b" + va_value + r"\b"
            match = re.search(pattern, filtered_source_value)
            if match is not None:
                mapped_values.add(self.get_field_mapping(va_value))

        if len(mapped_values) == 0:
            message = f"Unable to find mapping in {self.source_name} for value {source_value}"
            raise MAPHSAMissingMappingException(message, source_value, filtered_source_value)

        return mapped_values


# TODO maybe generalize regex usage
class ComponentTypeMapper(Mapper):

    def filter_source_value(self, source_value: str) -> str:

        _source_value = super().filter_source_value(source_value)
        _source_value = re.sub(r'[()\[\]/]', '', _source_value)

        return _source_value


class FeatureTypeMapper(Mapper):

    def filter_source_value(self, source_value: str) -> str:

        _source_value = super().filter_source_value(source_value)
        _source_value = re.sub(r'[()\[\]/]', '', _source_value)

        return _source_value


class ArtefactCategoryMapper(Mapper):

    def filter_source_value(self, source_value: str) -> str:

        _source_value = super().filter_source_value(source_value)
        _source_value = re.sub(r'[()\[\]/]', '', _source_value)

        return _source_value


class EnvironmentAssessmentParamMapper(Mapper):

    @staticmethod
    def filter_mapping_key(_key: str):
        key = _key.lower()
        # key = re.sub(r'[()\[\]/]', '', key)
        key = re.sub(r'[.,()¿?]', '', key)
        key = unidecode(key)
        return key

    def load_mappings(self, _mappings: dict):
        self.field_mappings = {self.filter_mapping_key(k): v.title() for k, v in _mappings.items()}


class HydrologyTypeMapper(EnvironmentAssessmentParamMapper):

    substring_mappings = {
        'baia': 'Bay',
        'corrego': 'Stream',
        'rio': 'River',
        'lagoa': 'Lake',
        'laguna': 'Lake',
        'riacho': 'Stream',

    }

    def get_field_mapping(self, _source_value: str) -> str:
        source_value = self.filter_source_value(_source_value)

        field_mapping = self.field_mappings[source_value] if source_value in self.field_mappings.keys() else None

        if field_mapping is None:
            for substring, value in self.substring_mappings.items():
                if substring in source_value:
                    field_mapping = value

        if field_mapping is None:
            self.report_missing_value(_source_value, source_value)
        else:
            return field_mapping
