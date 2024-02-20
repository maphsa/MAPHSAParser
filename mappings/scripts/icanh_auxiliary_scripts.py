import csv
import numpy as np
import pandas as pd


def parse_cell_value(_value: str):
    if _value == '' or pd.isna(_value):
        return _value
    cell_set = set(eval(_value))
    if len(cell_set) == 1:
        return cell_set.pop()
    elif len(cell_set) > 1:
        return list(cell_set)


def filter_incanh_sites(file_csv: str):

    # If this gets too complex, drop and switch to pandas
    out_rows = []

    df = pd.read_csv(file_csv, sep=',', quotechar='"')

    df = df.map(parse_cell_value)

    df.insert(0, 'ICANH_ID', '')
    df['ICANH_ID'] = df['Site Name'] + '_' + (np.arange(df.shape[0]) + 2).astype(str)

    output_file_url = file_csv.replace('.csv', '_filtered.csv')
    df.to_csv(output_file_url, sep=',', index=False)


filter_incanh_sites('../../sources/icanh_sites.csv')