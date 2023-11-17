import csv

import pandas as pd
import json
from pprint import pprint

from mappings.mappers.mappers import Mapper


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


process_periods()
