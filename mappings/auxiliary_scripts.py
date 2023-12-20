import re

import pandas as pd
import json

from unidecode import unidecode

import mappings

DISABLED_ROUTINGS = [
    {
        'source_sheet': 'env_assessment.topo_type',
        'source_value_column': 'value',
        'target_value_column': 'Columna1',
        'db_table_name': 'env_assessment',
        'db_field_name': 'topo_type'
    },
    {
        'source_sheet': 'env_assessment.lcov_type',
        'source_value_column': 'value',
        'target_value_column': 'Columna1',
        'db_table_name': 'env_assessment',
        'db_field_name': 'lcov_type'
    },
    {
        'source_sheet': 'env_assessment.soil_class',
        'source_value_column': 'value',
        'target_value_column': 'Columna1',
        'db_table_name': 'env_assessment',
        'db_field_name': 'soil_class'
    },
    {
        'source_sheet': 'env_assessment.l_use_type',
        'source_value_column': 'value',
        'target_value_column': 'Columna1',
        'db_table_name': 'env_assessment',
        'db_field_name': 'l_use_type'
    },
    {
        'source_sheet': 'hydro_info.hydro_type',
        'source_value_column': 'value',
        'target_value_column': 'Columna1',
        'db_table_name': 'hydro_info',
        'db_field_name': 'hydro_type'
    },
    {
        'source_sheet': 'hydro_info.hydro_basin',
        'source_value_column': 'value',
        'target_value_column': 'Columna1',
        'db_table_name': 'hydro_info',
        'db_field_name': 'hydro_type'
    }
]

SOURCE = {
    'url': 'mappings/auxiliary/Heidgen_Mappings.xlsx',
    'routings': [
        {
            'source_sheet': 'her_find.art_cat_concept_list_i',
            'source_value_column': 'value',
            'target_value_column': 'Columna1',
            'db_table_name': 'her_find',
            'db_field_name': 'art_cat_concept_list_id',
            'processing_method': 'filter_keys'
        }
    ]
}


def filter_keys(_mappings: dict) -> dict:
    new_mappings = {}
    for k, v in _mappings.items():
        k = unidecode(k)
        k = k.lower().strip()
        k = re.sub(r'[.,()¿?]', '', k)
        k = re.sub(r'[()\[\]/]', '', k)

        if pd.isna(v):
            v = "Undefined Object"

        new_mappings[k] = v

    return new_mappings


def get_additional_mappings():

    for r in SOURCE['routings']:
        df = pd.read_excel(SOURCE['url'], sheet_name=r['source_sheet'])

        table_name, field_name = r['db_table_name'], r['db_field_name']
        mapping_file_url = f"mappings/mappers/{table_name}.{field_name}.json"
        original_mappings = json.load(open(mapping_file_url, 'r'))
        original_mapper = mappings.MapperManager.get_mapper(table_name, field_name)

        new_mappings_list = df[[r['source_value_column'], r['target_value_column']]].to_numpy()
        new_mappings = {nm[0]: nm[1] for nm in new_mappings_list}

        if 'processing_method' in r.keys():
            processing_method = eval(r['processing_method'])
            new_mappings = processing_method(new_mappings)

        out_mappings = original_mappings | new_mappings

        with open(mapping_file_url, 'w') as outfile:
            json.dump(out_mappings, outfile)


get_additional_mappings()