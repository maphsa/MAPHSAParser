import uuid
from enum import Enum

from source_parser.sicg import sicg_parser


class ExistingSources(Enum):
    sicg = 'sicg'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


source_meta = {
    ExistingSources.sicg.value: {
        'name': ExistingSources.sicg.value,
        'version': 1.0,
        'date': '21.7.2023',
        'id_field': 'SICG_ID',
        'namespace': uuid.UUID('d08c3d93-3d3e-431d-affe-0d7bb1a839ba'),
        'parser': sicg_parser,
        'source_description': 'Parsed SICG legacy data'
    }
}

post_process_commands = ['createExtentPointsView.sql']

from source_parser import source_parser
