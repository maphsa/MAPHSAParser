import json
import re
from io import StringIO
import pathlib

import geojson
import pandas as pd
from pandas import Series
from shapely import Point
from tqdm import tqdm
from shapely.geometry import shape

import id_cipher
from database_interface import DatabaseInterface
from exceptions import MAPHSAParserException
from mappings import MapperManager


def create_input_dataframes(input_file: pathlib.Path) -> pd.DataFrame:
    with open(input_file, 'r') as f:
        contents = f.read()

    file_data = pd.read_csv(StringIO(contents))

    return file_data


def clean_input_dataframe(input_dataframe: pd.DataFrame) -> pd.DataFrame:
    return input_dataframe


def parse_icanh_her_maphsa(icanh_site_series: Series, source_meta: dict):

    icanh_id = icanh_site_series[source_meta['id_field']]
    uuid = id_cipher.generate_entity_uuid5(icanh_site_series, source_meta)

    source_id = DatabaseInterface.insert_entity('her_source', {
        'data_origin_name': source_meta['name'],
        'location': f"Line {icanh_site_series['ICANH_ID'].split('_')[-1]}"
    })

    her_maphsa_id = DatabaseInterface.insert_entity('her_maphsa', {
        'uuid': uuid,
        'description': f"Imported ICANH data.",
        'source_id': source_id
    })

    # Create these methods for ICANH

    parse_her_geom(icanh_site_series, source_meta, her_maphsa_id)
    '''
    parse_her_loc_sum(sicg_site_series, source_meta, her_maphsa_id)
    parse_her_admin_div(sicg_site_series, source_meta, her_maphsa_id)

    parse_arch_ass(sicg_site_series, source_meta, her_maphsa_id)
    # Parsing two branches simultaneously
    parse_built_comp_her_feature(sicg_site_series, source_meta, her_maphsa_id)

    parse_her_find(sicg_site_series, source_meta, her_maphsa_id)

    parse_env_assessment(sicg_site_series, source_meta, her_maphsa_id)
    parse_her_cond_ass(sicg_site_series, source_meta, her_maphsa_id)
    '''


def map_icanh_value(data_series, source_column_name, target_arches_collection_name, target_table_name,
                    target_field_name, fallback_value=None):
    concept_id_mappings = DatabaseInterface.get_concept_id_mappings()
    loc_cert_id_mappings = concept_id_mappings[target_arches_collection_name]
    loc_cert_string = data_series[source_column_name]
    if not pd.isna(loc_cert_string):
        loc_cert_mapper = MapperManager.get_mapper('icanh', target_table_name, target_field_name)
        loc_cert_name = loc_cert_mapper.get_field_mapping(loc_cert_string)
        return loc_cert_id_mappings[loc_cert_name]
    elif fallback_value is not None:
        return loc_cert_id_mappings[fallback_value]
    else:
        raise ValueError(f"Missing source and fallback values for mapping {source_column_name}"
                         f" into {target_arches_collection_name} at icanh.{target_table_name}.{target_field_name}")


def parse_her_geom(icanh_site_series: Series, source_meta: dict, her_maphsa_id: int):

    # Parse lat, long, polygon
    if not pd.isna(icanh_site_series['GeoJSON Lines']):
        (lat, long, polygon) = process_geom(icanh_site_series['GeoJSON Lines'])
    else:
        (lat, long, polygon) = (None, None, None)

    # Location Certainty
    if lat is None and long is None:
        loc_cert_id = DatabaseInterface.get_concept_id_mappings()['Site Location Certainty']['Negligible']
    else:
        loc_cert_id = map_icanh_value(icanh_site_series, "Site Location Certainty", 'Site Location Certainty',
                                      'her_geom', 'loc_cert', fallback_value='Unknown')

    if polygon is None:
        geom_ext_cert_id = DatabaseInterface.get_concept_id_mappings()['Geometry Extent Certainty']['Negligible']
    else:
        geom_ext_cert_id = map_icanh_value(icanh_site_series, "Site Location Certainty", 'Site Location Certainty',
                                           'her_geom', 'loc_cert', fallback_value='Unknown')

    # System ref ID
    sys_ref_id = DatabaseInterface.get_concept_id_mappings()['Spatial Coordinates Reference System Datum']['WGS84']

    # Grid
    grid_id = DatabaseInterface.get_placeholder_entity_id('grid')

    her_geom_id = DatabaseInterface.insert_entity('her_geom', {
        'loc_cert': loc_cert_id,
        'geom_ext_cert': geom_ext_cert_id,
        'sys_ref': sys_ref_id,
        'lat': 0 if lat is None else lat,
        'long': 0 if long is None else long,
        'her_maphsa_id': her_maphsa_id,
        'grid_id': grid_id,  # TODO this is still a placeholder
        "her_polygon": polygon if polygon is not None else None,
        'wkb_geometry': Point(long, lat).wkt if lat is not None and long is not None else None
    })

def get_polygon_feature(polygon_data: dict) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": polygon_data
            }
        ]
    }


# Return Lat, Long, Polygon if present
def process_geom(geojson_data_string):

    geojson_data = geojson.loads(geojson_data_string)
    if geojson_data['type'] == 'Point':
        (long, lat) = geojson_data['coordinates']
        return lat, long, None

    elif geojson_data['type'] == 'Polygon':
        if len(geojson_data['coordinates']) > 1:
            raise ValueError("Unknown polygon data format")
        points = geojson_data['coordinates'][0]
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        centroid = (sum(x) / len(points), sum(y) / len(points))
        return centroid[1], centroid[0], shape(geojson_data).wkt

    raise ValueError("Unknown geojson data format")


def parse_input_dataframe(input_dataframe: pd.DataFrame, source_meta: dict, insert_data: bool):
    pd.options.mode.chained_assignment = None

    for site_index in tqdm(input_dataframe.index):
        try:
            DatabaseInterface.start_transaction()
            parse_icanh_her_maphsa(input_dataframe.loc[site_index], source_meta)
            if insert_data:
                DatabaseInterface.commit_transaction()
            else:
                DatabaseInterface.abort_transaction()

        except MAPHSAParserException as mpe:
            DatabaseInterface.abort_transaction()
            print(mpe)


def process_input(input_files, source_meta: dict, load_supp_geodata: bool, insert_data: bool):
    data_frame_batch = {in_file.stem: create_input_dataframes(in_file) for in_file in input_files}

    if not DatabaseInterface.verify_origin(source_meta):
        DatabaseInterface.add_origin(source_meta)

    for (input_resource, input_data) in data_frame_batch.items():
        input_data = clean_input_dataframe(input_data)
        parse_input_dataframe(input_data, source_meta, insert_data)