import csv
import re

import pandas as pd
import json

from unidecode import unidecode

import mappings
from mappings.mappers.mappers import Mapper

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


def process_shape():
    xl_file = pd.ExcelFile('raw_mappings/forma.xlsx')

    df = xl_file.parse('Sheet1', names=['source_value', 'target_value'])

    mappings = {}

    for index, row in df.iterrows():
        source_value = Mapper.filter_source_value(row['source_value'])
        target_value = row['target_value']

        mappings[source_value] = target_value

    with open('output.json', 'w') as outfile:
        json.dump(mappings, outfile, indent=2)


def process_periods():

    xl_file = pd.ExcelFile('raw_mappings/MAPHSA_Periods.xlsx')
    df = xl_file.parse('Sheet2', skiprows=lambda x: x in [0])

    mappings = {}
    tar_vals: set = set([])

    for index, row in df.iterrows():
        source_value = Mapper.filter_source_value(row['Original'])
        target_value = row['Concept (Thesaurus)'].replace("_", " ")
        tar_vals.add(target_value)

        mappings[source_value] = target_value

    with open('site_cult_aff.cult_aff.json', 'w') as outfile:
        json.dump(dict(sorted(mappings.items())), outfile, indent=2)

    with open("Cultural Affiliation.csv", 'w') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerows(zip(sorted(tar_vals)))