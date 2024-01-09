import uuid
from enum import Enum

from source_parser.sicg import sicg_parser
from source_parser.icanh import icanh_parser


class ExistingSources(Enum):
    sicg = 'sicg'
    icanh = 'icanh'

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
        'source_description': 'Parsed SICG legacy data',
        'polygon_suffix': '_polygons.geojson'
    },
    ExistingSources.icanh.value: {
        'name': ExistingSources.icanh.value,
        'version': 1.0,
        'date': '8.1.2024',
        'id_field': 'ICANH_ID',
        'namespace': uuid.UUID('ca1a1d87-fa84-4926-8cc0-acc370916d81'),
        'parser': icanh_parser,
        'source_description': 'Delivered ICANH data',
        'polygon_suffix': '_polygons.geojson'
    }
}

post_process_commands = ['createExtentPointsView.sql']

from source_parser import source_parser
