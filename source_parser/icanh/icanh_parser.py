import json
import re
from io import StringIO
import pathlib

import geojson
import numpy as np
import pandas as pd
from pandas import Series
from shapely import Point
from tqdm import tqdm
from shapely.geometry import shape

import id_cipher
from database_interface import DatabaseInterface
from exceptions import MAPHSAParserException
from mappings import MapperManager


def polymorphic_field_to_list(source_field) -> list:
    if '[' in source_field and ']' in source_field:
        return eval(source_field)
    else:
        return [source_field]


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

    parse_her_loc_sum(icanh_site_series, source_meta, her_maphsa_id)

    parse_her_admin_div(icanh_site_series, source_meta, her_maphsa_id)

    parse_arch_ass(icanh_site_series, source_meta, her_maphsa_id)
    # Parsing two branches simultaneously
    '''
    parse_built_comp_her_feature(icanh_site_series, source_meta, her_maphsa_id)

    parse_her_find(icanh_site_series, source_meta, her_maphsa_id)

    parse_env_assessment(icanh_site_series, source_meta, her_maphsa_id)
    parse_her_cond_ass(icanh_site_series, source_meta, her_maphsa_id)
    '''


def map_icanh_value(source_value, target_arches_collection_name, target_table_name,
                    target_field_name, fallback_value=None):
    concept_id_mappings = DatabaseInterface.get_concept_id_mappings()
    loc_cert_id_mappings = concept_id_mappings[target_arches_collection_name]
    if not pd.isna(source_value):
        loc_cert_mapper = MapperManager.get_mapper('icanh', target_table_name, target_field_name)
        loc_cert_name = loc_cert_mapper.get_field_mapping(source_value)
        return loc_cert_id_mappings[loc_cert_name]
    elif fallback_value is not None:
        return loc_cert_id_mappings[fallback_value]
    else:
        raise ValueError(f"Missing source and fallback values for mapping {source_value}"
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
        loc_cert_id = map_icanh_value(icanh_site_series["Site Location Certainty"], 'Site Location Certainty',
                                      'her_geom', 'loc_cert', fallback_value='Unknown')

    if polygon is None:
        geom_ext_cert_id = DatabaseInterface.get_concept_id_mappings()['Geometry Extent Certainty']['Negligible']
    else:
        geom_ext_cert_id = map_icanh_value(icanh_site_series["Site Location Certainty"], 'Site Location Certainty',
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


def parse_her_loc_sum(icanh_site_series: Series, source_meta: dict, her_maphsa_id: int):
    gen_descr = icanh_site_series['Site Name']

    her_loc_sum_id = DatabaseInterface.insert_entity('her_loc_sum', {
        'gen_descr': gen_descr,
        'her_maphsa_id': her_maphsa_id
    })

    parse_her_loc_name(icanh_site_series, source_meta, her_loc_sum_id)
    parse_her_loc_type(icanh_site_series, source_meta, her_loc_sum_id)


def parse_her_loc_name(icanh_site_series: Series, source_meta: dict, her_loc_sum_id: int):
    her_loc_name = icanh_site_series['Site Name']
    her_loc_name_type = map_icanh_value(icanh_site_series["Heritage Location Name Type"],
                                        'Heritage Location Name Type',
                                        'her_loc_name', 'her_loc_name_type')

    DatabaseInterface.insert_entity(target_table='her_loc_name', target_data={
        'her_loc_name': her_loc_name,
        'her_loc_sum_id': her_loc_sum_id,
        'her_loc_name_type': her_loc_name_type
    })

    return


def parse_her_loc_type(icanh_site_series: Series, source_meta: dict, her_loc_sum_id: int):
    her_loc_type_cert = DatabaseInterface.get_concept_id_mapping('Heritage Location Type Certainty', 'Definite')

    her_loc_type_list = polymorphic_field_to_list(icanh_site_series['Heritage Location Type'])

    for her_loc_type_value in her_loc_type_list:
        her_loc_type = map_icanh_value(her_loc_type_value, 'Heritage Location Type',
                                       'her_loc_type', 'her_loc_type')

        her_loc_type_id = DatabaseInterface.insert_entity('her_loc_type', {
            'her_loc_type': her_loc_type,
            'her_loc_type_cert': her_loc_type_cert,
            'her_loc_sum_id': her_loc_sum_id
        })

    return


def parse_her_admin_div(icanh_site_series: Series, source_meta: dict, her_maphsa_id: int):
    country_admin_type_id = DatabaseInterface.get_concept_id_mapping('Administrative Division Type', 'Country')
    state_admin_type_id = DatabaseInterface.get_concept_id_mapping('Administrative Division Type',
                                                                   'Municipality')

    DatabaseInterface.insert_entity('her_admin_div', {
        'admin_div_name': 'Colombia',
        'admin_type': country_admin_type_id,
        'her_maphsa_id': her_maphsa_id
    })

    admin_div_name = icanh_site_series['Administrative Division Name']
    admin_type_value = icanh_site_series['Administrative Division Type']
    if not pd.isna(admin_div_name) and pd.isna(admin_type_value):
        admin_type = map_icanh_value(admin_type_value, 'Administrative Division Type',
                                       'her_admin_div', 'admin_type')

        DatabaseInterface.insert_entity('her_admin_div', {
            'admin_div_name': admin_div_name,
            'admin_type': admin_type,
            'her_maphsa_id': her_maphsa_id
        })

    return


def parse_arch_ass(icanh_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:
    # Previous Research Activities
    # TODO Only a few rows present, no mappings
    prev_res_act_id = DatabaseInterface.create_concept_list('Previous Research Activities', [])

    # Shape
    if pd.isna(icanh_site_series['Shape']):
        her_shape_values = ['not informed']
    else:
        her_shape_values = polymorphic_field_to_list(icanh_site_series['Shape'])

    mapped_her_shape_values = set()
    for her_shape_value in her_shape_values:
        mapped_her_shape = map_icanh_value(her_shape_value, 'Shape',
                                    'arch_ass', 'her_shape')
        mapped_her_shape_values.add(mapped_her_shape)

    her_shape_id = next(iter(mapped_her_shape_values))  # TODO disambiguate or reduce somehow

    # Overall Morphology

    her_morph_values: set = set()

    if not pd.isna(icanh_site_series['Overall Morphology']):
        her_morph_values.update(polymorphic_field_to_list(icanh_site_series['Overall Morphology']))

    if not pd.isna(icanh_site_series['Overall Morphology.1']):
        her_morph_values.update(polymorphic_field_to_list(icanh_site_series['Overall Morphology.1']))

    if len(her_morph_values) == 0:
        her_morph_values.add('not informed')

    mapped_her_morph_values = set()
    for her_morph_value in her_morph_values:
        mapped_her_morph = map_icanh_value(her_morph_value, 'Overall Morphology',
                                        'arch_ass', 'her_morph')
        mapped_her_morph_values.add(mapped_her_morph)

    try:
        her_morph_id = next(iter(mapped_her_morph_values))  # TODO disambiguate or reduce somehow
    except KeyError as ke:
        print(ke)

    # Heritage Location Orientation
    her_loc_orient_id = DatabaseInterface.get_concept_id_mappings()['Heritage Location Orientation']['Not Informed']

    # Overall Archaeological Certainty
    overall_arch_cert_id = DatabaseInterface.get_concept_id_mappings()['Overall Archaeological Certainty']['Definite']

    arch_ass_id = DatabaseInterface.insert_entity('arch_ass', {
        'her_maphsa_id': her_maphsa_id,
        'prev_res_act': prev_res_act_id,
        'her_morph': her_morph_id,
        'her_shape': her_shape_id,
        'her_loc_orient': her_loc_orient_id,  # TODO
        'o_arch_cert': overall_arch_cert_id
    })

    # Cultural affiliation

    confirmed_ca_certainty_id = DatabaseInterface.get_concept_id_mappings()['Cultural Affiliation Certainty'][
        'Confirmed']

    ca_values: set = set()

    if not pd.isna(icanh_site_series['Cultural Affiliation']):
        ca_values.update(polymorphic_field_to_list(icanh_site_series['Cultural Affiliation']))

    if not pd.isna(icanh_site_series['Cultural Affiliation.1']):
        ca_values.update(polymorphic_field_to_list(icanh_site_series['Cultural Affiliation.1']))

    if len(ca_values) == 0:
        ca_values.add('not informed')

    ca_ids = set()
    # Patch odd value # TODO Ask about this
    if "puerto caldas   granada" in ca_values:
        ca_values.remove("puerto caldas   granada")
        ca_values.add("puerto caldas")
        ca_values.add("granada")

    for ca_value in ca_values:
        ca_id = map_icanh_value(ca_value, 'Cultural Affiliation', 'site_cult_aff', 'cult_aff')
        ca_ids.add(ca_id)

    for ca_id in ca_ids:

        site_cult_aff_id = DatabaseInterface.insert_entity('site_cult_aff', {
            'arch_ass_id': arch_ass_id,
            'cult_aff': ca_id,
            'cult_aff_certainty': confirmed_ca_certainty_id

        })

    '''
    # Period

    dated_ca_names = [ca_name for ca_name in ca_names if ca_name not in ('Other', 'Not Informed')]

    dates = []
    if len(dated_ca_names) > 0:
        date_mapper = mappings.MapperManager.get_mapper('sicg', 'sites_timespace', 'from_to_date')
        for ca_name in dated_ca_names:
            try:
                date_string = date_mapper.get_field_mapping(ca_name)
                if date_string != '':
                    dates += [int(d) for d in date_string.split(',')]
            except MAPHSAMissingMappingException as e:
                # TODO ignore undated cultural affiliation values?
                continue

    if len(dates) > 0:
        dates.sort()

        from_year = dates[-1]
        to_year = dates[0]

        pc_id = DatabaseInterface.get_concept_id_mappings()['Period Certainty']['Unconfirmed']

        sites_timespace_id = DatabaseInterface.insert_entity('sites_timespace', {
            'arch_ass_id': arch_ass_id,
            'period_cert': pc_id,
            'from_year': from_year,
            'to_year': to_year,

        })
    '''
    # Function

    if not pd.isna(icanh_site_series['Heritage Location Function']):
        her_loc_funct_values = polymorphic_field_to_list(icanh_site_series['Heritage Location Function'])

        her_loc_funct_mapped_ids = set()
        for her_loc_funct_value in her_loc_funct_values:
            her_loc_funct_mapped_ids.add(map_icanh_value(her_loc_funct_value, 'Heritage Location Function',
                                                         'her_loc_funct', 'her_loc_funct')
                                         )

        hlfc_mapped_id = map_icanh_value(icanh_site_series['Heritage Location Function Certainty'],
                                         'Heritage Location Function Certainty',
                                         'her_loc_funct', 'her_loc_fun_cert')

        for her_loc_funct_mapped_id in her_loc_funct_mapped_ids:

            her_loc_funct_id = DatabaseInterface.insert_entity('her_loc_funct', {
                'her_loc_funct': her_loc_funct_mapped_id,
                'her_loc_fun_cert': hlfc_mapped_id,
                'arch_ass_id': arch_ass_id
            })
    '''
    # Heritage Location Measurement

    def insert_measurement(source_value: float, dimension: str, measurement_unit: str, her_meas_type: int):

        source_value = float(source_value)

        if not pd.isna(source_value) and source_value != 0:
            her_dimen = DatabaseInterface.get_concept_id_mappings()['Dimension'][dimension]
            her_meas_unit = DatabaseInterface.get_concept_id_mappings()['Measurement Unit'][measurement_unit]
            her_meas_value = source_value

            her_loc_meas_id = DatabaseInterface.insert_entity('her_loc_meas', {
                'her_dimen': her_dimen,
                'her_meas_unit': her_meas_unit,
                'her_meas_type': her_meas_type,
                'her_meas_value': her_meas_value,
                'arch_ass_id': arch_ass_id
            })

        return arch_ass_id

    # TODO Refactor as Mapper with json file?
    match sicg_site_series['medicao']:

        case 'instrumento':
            measurement_type = DatabaseInterface.get_concept_id_mappings()['Measurement Type']['Handheld GPS']
        case 'estimada':
            measurement_type = DatabaseInterface.get_concept_id_mappings()['Measurement Type']['Estimated/Paced']
        case 'passo':
            measurement_type = DatabaseInterface.get_concept_id_mappings()['Measurement Type']['Estimated/Paced']
        case 'mapa':
            measurement_type = DatabaseInterface.get_concept_id_mappings()['Measurement Type']['Maps']
        case _:
            measurement_type = DatabaseInterface.get_concept_id_mappings()['Measurement Type'][
                'Unknown-Recorded From Legacy Data']

    for source_measurement_field in [
        ('comprimento', 'Length', 'Meters (m)'),
        ('largura', 'Breadth/Width', 'Meters (m)'),
        ('area', 'Area', 'Square Meters (m2)')
    ]:
        try:
            insert_measurement(
                sicg_site_series[source_measurement_field[0]],
                source_measurement_field[1],
                source_measurement_field[2],
                measurement_type)

        except ValueError as ve:
            missing_value = f"{sicg_site_series[source_measurement_field[0]]}:{source_measurement_field[1]}:{source_measurement_field[2]}"
            MapperManager.add_missing_value(missing_value, missing_value,
                                            f"{source_meta['name']}:{sicg_site_series['X']}:{source_measurement_field}",
                                            'her_loc_meas.her_meas_value')
            continue
    '''


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
