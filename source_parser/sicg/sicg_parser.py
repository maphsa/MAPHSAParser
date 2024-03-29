import json
from io import StringIO
import re
import pathlib
import os.path

import geojson
import numpy as np
import pandas
import pandas as pd
import psycopg2.errors
from pandas import Series
from tqdm import tqdm
from geojson import Point
from shapely.geometry import shape

import database_interface
from database_interface import DatabaseInterface
import source_parser
from exceptions.exceptions import MAPHSAParserException, MAPHSAMissingMappingException
from mappings import MapperManager
from source_parser.sicg import sicg_settings
from source_parser.sicg.sicg_settings import NAME_NEGATIVES
import id_cipher
import mappings

PRONAPA_REGEX = r'[A-Z]{1,}-[A-Z]{1,}-[0-9]{1,}'
CONSTRUCTION_CODE_REGEX = r'[aA-zZ]+-*[0-9]+-*[aA-zZ]+-*[aA-zZ]+-*[0-9]+'


def create_input_dataframes(input_file: pathlib.Path) -> pd.DataFrame:
    with open(input_file, 'r') as f:
        contents = f.read()

    file_data = pd.read_csv(StringIO(contents), keep_default_na=False)

    return file_data


def set_column_to_float(dataframe: pandas.DataFrame, column_name: str):
    if dataframe[column_name].dtypes != 'float64':
        return dataframe[column_name].apply(lambda x: float(x.split()[0].replace(',', '.')))
    else:
        return dataframe[column_name]


def clean_input_dataframe(input_dataframe: pd.DataFrame) -> pd.DataFrame:
    input_dataframe['X'] = input_dataframe['X'] + 2 #TODO This is sloppy, column value gets displaced over time

    input_dataframe = input_dataframe.replace('', np.NAN)
    input_dataframe = input_dataframe.replace('NA', np.NAN)
    input_dataframe = input_dataframe.dropna(axis=1, how='all')

    ''' #TODO remove debug limiter
    artifact_columns = []
    for col in input_dataframe.columns:
        if input_dataframe[col].count() < sicg_settings.MIN_COLUMN_VALUE:
            artifact_columns.append(col)

    input_dataframe = input_dataframe.drop(artifact_columns, axis=1)
    '''
    # TODO Some oddity happening here with input csv and panda datatypes, keep an eye
    input_dataframe['Latitude'] = set_column_to_float(input_dataframe, 'Latitude')
    input_dataframe['Longitude'] = set_column_to_float(input_dataframe, 'Longitude')

    return input_dataframe


def parse_input_dataframe(input_dataframe: pd.DataFrame, source_meta: dict, insert_data: bool):
    pd.options.mode.chained_assignment = None

    for site_index in tqdm(input_dataframe.index):
        try:
            DatabaseInterface.start_transaction()
            parse_sicg_her_maphsa(input_dataframe.loc[site_index], source_meta)
            if insert_data:
                DatabaseInterface.commit_transaction()
            else:
                DatabaseInterface.abort_transaction()

        except MAPHSAParserException as mpe:
            DatabaseInterface.abort_transaction()
            print(mpe)


def parse_sicg_her_maphsa(sicg_site_series: Series, source_meta: dict):

    sicg_id = sicg_site_series['SICG_ID']
    uuid = id_cipher.generate_entity_uuid5(sicg_site_series,
                                           source_parser.source_meta[source_parser.ExistingSources.sicg.value])

    information_resource_id = DatabaseInterface.get_information_resource_id(source_meta)

    source_id = DatabaseInterface.insert_entity('her_source', {
        'data_origin_name': source_meta['name'],
        'location': f"Line {sicg_site_series['X']}"
    })

    her_maphsa_id = DatabaseInterface.insert_entity('her_maphsa', {
        'uuid': uuid,
        'description': f"Legacy SICG data.",
        'source_id': source_id,
        'information_resource_id': information_resource_id
    })

    parse_her_geom(sicg_site_series, source_meta, her_maphsa_id)
    parse_her_loc_sum(sicg_site_series, source_meta, her_maphsa_id)


    parse_arch_ass(sicg_site_series, source_meta, her_maphsa_id)
    # Parsing two branches simultaneously
    parse_built_comp_her_feature(sicg_site_series, source_meta, her_maphsa_id)

    parse_her_find(sicg_site_series, source_meta, her_maphsa_id)

    parse_env_assessment(sicg_site_series, source_meta, her_maphsa_id)
    parse_her_cond_ass(sicg_site_series, source_meta, her_maphsa_id)
    parse_her_admin_div(sicg_site_series, source_meta, her_maphsa_id)


def process_geom(_lat, _long, _polygon):
    lat = long = None
    if not pd.isna(_lat) and not pd.isna(_long):
        lat = _lat
        long = _long

    polygon_points = []
    if not pd.isna(_polygon):
        for point_string in _polygon.split(","):
            point_coords = re.findall("([0-9]+) ([0-9]+)", point_string)[0]
            polygon_points.append((float(point_coords[0])*-0.0001, float(point_coords[1])*-0.000001))

    return lat, long, polygon_points


def parse_her_geom(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int):
    concept_id_mappings = DatabaseInterface.get_concept_id_mappings()
    geom_ext_cert_definite_concept_id = concept_id_mappings['Geometry Extent Certainty']['Negligible']
    loc_cert_definite_concept_id = concept_id_mappings['Site Location Certainty']['Definite']
    loc_cert_negligible_concept_id = concept_id_mappings['Site Location Certainty']['Negligible']
    sys_ref_id = concept_id_mappings['Spatial Coordinates Reference System Datum']['WGS84']

    grid_id = DatabaseInterface.get_placeholder_entity_id('grid')

    obs_geo = sicg_site_series['obsGeo'] if not pd.isna(sicg_site_series['obsGeo']) else None
    if obs_geo and re.match('Georreferenciamento dentro dos limites municipais', obs_geo):
        loc_cert_concept_id = loc_cert_negligible_concept_id
    else:
        loc_cert_concept_id = loc_cert_definite_concept_id

    try:
        (lat, long, polygon) = process_geom(sicg_site_series['Latitude'], sicg_site_series['Longitude'], sicg_site_series['perimetro'])

    except IndexError as ie:
        print(f"Unable to parse perimeter for {sicg_site_series['X']}")
        lat = long = None
        polygon = []

    her_geom_id = DatabaseInterface.insert_entity('her_geom', {
        'loc_cert': loc_cert_concept_id,
        'geom_ext_cert': geom_ext_cert_definite_concept_id,
        'sys_ref': sys_ref_id,
        'lat': 0 if lat is None else lat,
        'long': 0 if long is None else long,
        'her_maphsa_id': her_maphsa_id,
        'grid_id': grid_id,
        "her_polygon": None,
        'wkb_geometry': None
    })

    # TODO Parse the polygons?
    '''
    if len(polygon) > 3:
        polygon_string = ",POLYGON(("
        for p in polygon:
            polygon_string = polygon_string + f"{p[0]} {p[1]}, "

        polygon_string = polygon_string + f"{polygon[0][0]} {polygon[0][1]}))"
    '''

    if lat and long:
        DatabaseInterface.run_script('update_her_geom', target_data={
            'lat': lat,
            'long': long,
            'her_geom_id': her_geom_id
        })

    if 'supp_geom' in sicg_site_series and not pd.isna(sicg_site_series['supp_geom']):
        polygon_geom = geojson.loads(sicg_site_series['supp_geom'])
        DatabaseInterface.run_script('update_her_polygon', target_data={
            'her_geom_id': her_geom_id,
            'polygon_string': shape(polygon_geom).wkt
        })


def parse_her_loc_sum(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int):
    gen_descr = sicg_site_series['Nome.popular']
    her_maphsa_id = her_maphsa_id

    her_loc_sum_id = DatabaseInterface.insert_entity('her_loc_sum', {
        'gen_descr': gen_descr,
        'her_maphsa_id': her_maphsa_id
    })

    parse_her_loc_name(sicg_site_series, source_meta, her_loc_sum_id)
    parse_her_loc_type(sicg_site_series, source_meta, her_loc_sum_id)


def get_her_admin_div_id(admin_div_name, admin_div_type):
    results = DatabaseInterface.run_script('select_her_admin_div',
                                           {'admin_div_name': admin_div_name, 'admin_div_type': admin_div_type},
                                           True)

    return results[0][0] if results else None


def parse_her_admin_div(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int):
    country_admin_type_id = DatabaseInterface.get_concept_id_mapping('Administrative Division Type', 'Country')
    municipality_admin_type_id = DatabaseInterface.get_concept_id_mapping('Administrative Division Type',
                                                                          'Municipality')
    state_admin_type_id = DatabaseInterface.get_concept_id_mapping('Administrative Division Type',
                                                                   'State')

    brazil_country_id = get_her_admin_div_id('Brazil', 'Country')
    DatabaseInterface.insert_entity('her_maphsa_admin_div', {
        'her_admin_div_id': brazil_country_id,
        'her_maphsa_id': her_maphsa_id
    })

    state_id = get_her_admin_div_id(sicg_site_series['UF'], 'State')
    if not pd.isna(sicg_site_series['UF']) and state_id is None:
        state_value = sicg_site_series['UF']

        DatabaseInterface.insert_entity('her_admin_div', {
            'admin_div_name': state_value,
            'admin_type': state_admin_type_id,
            'her_maphsa_id': her_maphsa_id
        })
    elif not pd.isna(sicg_site_series['UF']):
        DatabaseInterface.insert_entity('her_maphsa_admin_div', {
            'her_admin_div_id': state_id,
            'her_maphsa_id': her_maphsa_id
        })

    municipality_id = get_her_admin_div_id(sicg_site_series['Município'], 'Municipality')
    if not pd.isna(sicg_site_series['Município']) and municipality_id is None:
        municipality_value = sicg_site_series['Município']

        DatabaseInterface.insert_entity('her_admin_div', {
            'admin_div_name': municipality_value,
            'admin_type': municipality_admin_type_id,
            'her_maphsa_id': her_maphsa_id
        })

    elif not pd.isna(sicg_site_series['Município']):
        DatabaseInterface.insert_entity('her_maphsa_admin_div', {
            'her_admin_div_id': municipality_id,
            'her_maphsa_id': her_maphsa_id
        })

    return


def parse_her_loc_name(sicg_site_series: Series, source_meta: dict, her_loc_sum_id: int):
    sicg_id = None
    if not pd.isna(sicg_site_series['SICG_ID']):
        sicg_id = sicg_site_series['SICG_ID']

    cnsa_id = None
    if not pd.isna(sicg_site_series['Códigos.vinculados']):
        cnsa_id = sicg_site_series['Códigos.vinculados']

    pronapa_id = None
    name_candidates = []

    if not pd.isna(sicg_site_series['Nome']):
        pronapa_id, name_candidates = parse_name_field(sicg_site_series['Nome'], pronapa_id, name_candidates)

    if not pd.isna(sicg_site_series['Nome.popular']):
        pronapa_id, name_candidates = parse_name_field(sicg_site_series['Nome.popular'], pronapa_id, name_candidates)

    '''
    print(f"ROW {sicg_site_series['X']}")

    print(f"Nome field: {sicg_site_series['Nome']}")
    print(f"Nome.popular field: {sicg_site_series['Nome.popular']}")
    print(f"______Parse results______")

    if len(name_candidates) > 0:
        print(f"Primary name: {name_candidates[0]}")

    if len(name_candidates) > 1:
        print(f"Alternative names:")
        for n in name_candidates[1:]:
            print(n)

    if cnsa_id:
        print(f"CNSA ID: {cnsa_id}")

    if sicg_id:
        print(f"SICG ID: {sicg_id}")

    if pronapa_id:
        print(f"PRONAPA ID: {pronapa_id}")

    print("##########################################################################")
    '''

    if sicg_id:
        sicg_concept_id = DatabaseInterface.get_concept_id_mapping('Heritage Location Name Type', 'SICG ID')
        DatabaseInterface.insert_entity(target_table='her_loc_name', target_data={
            'her_loc_name': sicg_id,
            'her_loc_sum_id': her_loc_sum_id,
            'her_loc_name_type': sicg_concept_id
        })

    if cnsa_id:
        cnsa_concept_id = DatabaseInterface.get_concept_id_mapping('Heritage Location Name Type', 'CNSA ID')
        DatabaseInterface.insert_entity(target_table='her_loc_name', target_data={
            'her_loc_name': cnsa_id,
            'her_loc_sum_id': her_loc_sum_id,
            'her_loc_name_type': cnsa_concept_id
        })

    if pronapa_id:
        pronapa_concept_id = DatabaseInterface.get_concept_id_mapping('Heritage Location Name Type', 'PRONAPA ID')
        DatabaseInterface.insert_entity(target_table='her_loc_name', target_data={
            'her_loc_name': pronapa_id,
            'her_loc_sum_id': her_loc_sum_id,
            'her_loc_name_type': pronapa_concept_id
        })

    if len(name_candidates) > 0:
        primary_name_concept_id = DatabaseInterface.get_concept_id_mapping('Heritage Location Name Type',
                                                                           'Primary Name')
        DatabaseInterface.insert_entity(target_table='her_loc_name', target_data={
            'her_loc_name': name_candidates[0],
            'her_loc_sum_id': her_loc_sum_id,
            'her_loc_name_type': primary_name_concept_id
        })

    for nc in name_candidates[1:]:
        alternate_name_concept_id = DatabaseInterface.get_concept_id_mapping('Heritage Location Name Type',
                                                                             'Alternate Name')
        DatabaseInterface.insert_entity(target_table='her_loc_name', target_data={
            'her_loc_name': nc,
            'her_loc_sum_id': her_loc_sum_id,
            'her_loc_name_type': alternate_name_concept_id
        })

    return


# SilentGhost's solution from
# https://stackoverflow.com/questions/1265665/how-can-i-check-if-a-string-represents-an-int-without-using-try-except
def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def parse_name_field(name_field, pronapa_id, name_candidates):
    name_field = name_field.strip()

    partial_name_string = name_field

    match = re.search(CONSTRUCTION_CODE_REGEX, partial_name_string)
    if match:
        partial_name_string = partial_name_string.replace(match.group(), "")

    match = re.search(PRONAPA_REGEX, partial_name_string)
    if match and pronapa_id is None:
        pronapa_id = match.group()

    if name_field not in NAME_NEGATIVES and not check_int(name_field):
        name_candidates.append(name_field)

    return pronapa_id, name_candidates


def parse_her_loc_type(sicg_site_series: Series, source_meta: dict, her_loc_sum_id: int):
    her_loc_type = DatabaseInterface.get_concept_id_mapping('Heritage Location Type', 'Archaeological Site')
    her_loc_type_cert = DatabaseInterface.get_concept_id_mapping('Heritage Location Type Certainty', 'Definite')

    her_loc_type_id = DatabaseInterface.insert_entity('her_loc_type', {
        'her_loc_type': her_loc_type,
        'her_loc_type_cert': her_loc_type_cert,
        'her_loc_sum_id': her_loc_sum_id
    })

    return her_loc_type_id


def parse_arch_ass(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:
    # Previous Research Activities
    pra_ids = []

    if not pd.isna(sicg_site_series['atividadesDesenvolvidasLocal1']):
        pra_mapper = mappings.MapperManager.get_mapper('sicg', 'arch_ass', 'prev_res_act')
        prev_res_act_mapping_ids = DatabaseInterface.get_concept_id_mappings()['Previous Research Activities']
        previous_research_activities = \
            [pra.strip() for pra in pra_mapper.split_source_value(sicg_site_series['atividadesDesenvolvidasLocal1'])]

        for pra in previous_research_activities:
            maphsa_name = pra_mapper.get_field_mapping(pra)
            maphsa_id = prev_res_act_mapping_ids[maphsa_name]
            pra_ids.append(maphsa_id)

    prev_res_act_id = DatabaseInterface.create_concept_list('Previous Research Activities', pra_ids)

    # Shape
    shape_mapping_ids = DatabaseInterface.get_concept_id_mappings()['Shape']
    her_shape_id = DatabaseInterface.get_concept_id_mapping('Shape', 'Not Informed')
    if not pd.isna(sicg_site_series['forma']):
        shape_mapper = mappings.MapperManager.get_mapper('sicg', 'arch_ass', 'her_shape')
        her_shape_name = shape_mapper.get_field_mapping(sicg_site_series['forma'])
        her_shape_id = shape_mapping_ids[her_shape_name]

    # Overall Morphology
    her_morph_id = DatabaseInterface.get_concept_id_mappings()['Overall Morphology']['Unknown']

    # Heritage Location Orientation
    her_loc_orient_id = DatabaseInterface.get_concept_id_mappings()['Heritage Location Orientation']['Not Informed']

    # Overall Certainty
    overall_arch_cert_id = DatabaseInterface.get_concept_id_mappings()['Overall Archaeological Certainty']['Definite']

    arch_ass_id = DatabaseInterface.insert_entity('arch_ass', {
        'her_maphsa_id': her_maphsa_id,
        'prev_res_act': prev_res_act_id,
        'her_morph': her_morph_id,
        'her_shape': her_shape_id,
        'her_loc_orient': her_loc_orient_id,
        'o_arch_cert': overall_arch_cert_id
    })

    # Cultural affiliation

    confirmed_ca_certainty_id = DatabaseInterface.get_concept_id_mappings()['Cultural Affiliation Certainty'][
        'Confirmed']
    ca_mapping_ids = DatabaseInterface.get_concept_id_mappings()['Cultural Affiliation']
    ca_mapper = mappings.MapperManager.get_mapper('sicg', 'site_cult_aff', 'cult_aff')
    ca_names: set = set()

    def is_valid_ca_value(source_value: str) -> bool:
        return not pd.isna(source_value) and source_value not in ('.', '?', '-')

    def find_word_in_text(search_text, target_word):
        try:
            search_function = re.compile(r'\b({0})\b'.format(target_word), flags=re.IGNORECASE).findall
            return search_function(search_text)
        except Exception as e:
            print("find_word_in_text exception")
            print(e)

    if is_valid_ca_value(sicg_site_series['tradicoesArtefatosCeramicos']):
        try:
            ca_names = ca_names.union(ca_mapper.get_field_mappings(sicg_site_series['tradicoesArtefatosCeramicos']))
        except MAPHSAMissingMappingException as mme:
            MapperManager.add_missing_value(sicg_site_series['tradicoesArtefatosCeramicos'], mme.missing_value,
                                            f"{source_meta['name']}:{sicg_site_series['X']}:tradicoesArtefatosCeramicos",
                                            'site_cult_aff.cult_aff')
            ca_names.add('Other')

    if is_valid_ca_value(sicg_site_series['fasesArtefatosCeramicos']):
        try:
            ca_names = ca_names.union(ca_mapper.get_field_mappings(sicg_site_series['fasesArtefatosCeramicos']))
        except MAPHSAMissingMappingException as mme:
            MapperManager.add_missing_value(sicg_site_series['fasesArtefatosCeramicos'], mme.missing_value,
                                            f"{source_meta['name']}:{sicg_site_series['X']}:fasesArtefatosCeramicos",
                                            'site_cult_aff.cult_aff')
            ca_names.add('Other')

    if is_valid_ca_value(sicg_site_series['tradicoesArtefatosLiticos']):
        try:
            ca_names = ca_names.union(ca_mapper.get_field_mappings(sicg_site_series['tradicoesArtefatosLiticos']))
        except MAPHSAMissingMappingException as mme:
            MapperManager.add_missing_value(sicg_site_series['tradicoesArtefatosLiticos'], mme.missing_value,
                                            f"{source_meta['name']}:{sicg_site_series['X']}:tradicoesArtefatosLiticos",
                                            'site_cult_aff.cult_aff')
            ca_names.add('Other')

    # Check the description field sicg_site_series['Síntese.histórica']
    if str(sicg_site_series['X']) in ca_mapper.description_ca_values.keys():
        source_value, target_value = ca_mapper.description_ca_values[str(sicg_site_series['X'])].split('_')
        if source_value in sicg_site_series['Síntese.histórica'] and target_value not in ca_names:
            ca_names.add(target_value)

    if len(ca_names) == 0:
        ca_names.add('Not Informed')

    ca_ids = []
    for ca_name in ca_names:
        ca_id = DatabaseInterface.get_concept_id_mappings()['Cultural Affiliation'][ca_name]
        ca_ids.append(ca_id)

    for ca_id in ca_ids:

        site_cult_aff_id = DatabaseInterface.insert_entity('site_cult_aff', {
            'arch_ass_id': arch_ass_id,
            'cult_aff': ca_id,
            'cult_aff_certainty': confirmed_ca_certainty_id

        })

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

    # Function

    if not pd.isna(sicg_site_series['tipo']):
        hlfc_id = DatabaseInterface.get_concept_id_mappings()['Heritage Location Function Certainty']['Definite']
        function_mapper = mappings.MapperManager.get_mapper('sicg', 'her_loc_funct', 'her_loc_funct')
        function_ids = DatabaseInterface.get_concept_id_mappings()['Heritage Location Function']

        her_loc_funct_name = function_mapper.get_field_mapping(sicg_site_series['tipo'])

        if her_loc_funct_name != 'Not Informed':
            her_loc_funct_id = function_ids[her_loc_funct_name]

            her_loc_funct_id = DatabaseInterface.insert_entity('her_loc_funct', {
                'her_loc_funct': her_loc_funct_id,
                'her_loc_fun_cert': hlfc_id,
                'arch_ass_id': arch_ass_id
            })

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


def parse_built_comp_her_feature(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int) -> (int, int):
    # If estruturas field can't be mapped to either a Feature or Built Component, report it as a missing mapping

    built_comp_id = her_feature_id = None
    # Skip if no source value
    if not pd.isna(sicg_site_series['estruturas']):

        try:
            built_comp_id = parse_built_comp(sicg_site_series, source_meta, her_maphsa_id)
        except MAPHSAMissingMappingException as mme:
            source_value = mme.missing_value
            built_comp_id = None

        try:
            her_feature_id = parse_her_feature(sicg_site_series, source_meta, her_maphsa_id)
        except MAPHSAMissingMappingException as mme:
            source_value = mme.missing_value
            her_feature_id = None

        if not built_comp_id and not her_feature_id and not pd.isna(sicg_site_series['estruturas']):
            MapperManager.add_missing_value(sicg_site_series['estruturas'], source_value,
                                            f"{source_meta['name']}:{sicg_site_series['X']}:estruturas",
                                            'built_comp.comp_type/her_feature.feat_type')

    return built_comp_id, her_maphsa_id


def parse_built_comp(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int):
    estruturas_value = sicg_site_series['estruturas']

    comp_type_concept_names = mappings.MapperManager.get_mapper('sicg', 'built_comp', 'comp_type')
    comp_type_concept_ids = DatabaseInterface.get_concept_id_mappings()['Component Type']

    comp_type_concept_names = comp_type_concept_names.get_field_mapping(estruturas_value, True)

    built_comp_ids = []
    for comp_type_concept_name in comp_type_concept_names:
        comp_type = comp_type_concept_ids[comp_type_concept_name]

        built_comp_id = DatabaseInterface.insert_entity('built_comp', {
            'her_maphsa_id': her_maphsa_id,
            'comp_type': comp_type,
            'comp_mat': 'NULL',
            'comp_const_tech': 'NULL'
        })

        built_comp_ids.append(built_comp_id)

    return built_comp_ids


def parse_her_feature(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int):
    estruturas_value = sicg_site_series['estruturas']

    feat_type_concept_names = mappings.MapperManager.get_mapper('sicg', 'her_feature', 'feat_type')
    feat_type_concept_ids = DatabaseInterface.get_concept_id_mappings()['Feature Type']

    feat_type_concept_names = feat_type_concept_names.get_field_mapping(estruturas_value, True)

    her_feature_ids = []
    for feat_type_concept_name in feat_type_concept_names:
        feat_type = feat_type_concept_ids[feat_type_concept_name]

        her_feature_id = DatabaseInterface.insert_entity('her_feature', {
            'her_maphsa_id': her_maphsa_id,
            'feat_type': feat_type,
            'feat_count': 1
        })

        her_feature_ids.append(her_feature_id)

    return her_feature_ids


def parse_her_find(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:
    artefact_category_ids = []

    if not pd.isna(sicg_site_series['artefatos']):

        artefatos_value = sicg_site_series['artefatos']

        art_cat_concept_names = mappings.MapperManager.get_mapper('sicg', 'her_find', 'art_cat_concept_list_id')
        art_cat_concept_ids = DatabaseInterface.get_concept_id_mappings()['Artefact Category']

        try:
            art_cat_concept_name = art_cat_concept_names.get_field_mapping(artefatos_value)
        except MAPHSAMissingMappingException as mme:
            MapperManager.add_missing_value(artefatos_value, mme.missing_value,
                                            f"{source_meta['name']}:{sicg_site_series['X']}:artefatos",
                                            'her_find.art_cat_concept_list_id')
            return None

        art_cat_id = art_cat_concept_ids[art_cat_concept_name]

        artefact_category_ids.append(art_cat_id)

    if len(artefact_category_ids) > 0:
        art_cat_concept_list_id = DatabaseInterface.create_concept_list('Artefact Category', artefact_category_ids)

        her_find_id = DatabaseInterface.insert_entity('her_find', {
            'her_maphsa_id': her_maphsa_id,
            'art_cat_concept_list_id': art_cat_concept_list_id
        })

        return her_find_id


def parse_env_assessment_param(source_series, source_field_name, target_collection_name, fallback_concept_name,
                               source_meta_name, target_table, target_field, concept_list=False):
    source_value = source_series[source_field_name] if not pd.isna(source_series[source_field_name]) else None
    concept_names = mappings.MapperManager.get_mapper('sicg', target_table, target_field)
    concept_ids = DatabaseInterface.get_concept_id_mappings()[target_collection_name]
    fallback_concept_id = DatabaseInterface.get_concept_id_mappings()[target_collection_name][fallback_concept_name]

    target_concept_ids = []

    if source_value is not None:

        try:
            target_concept_name = concept_names.get_field_mapping(source_value)
            target_concept_id = concept_ids[target_concept_name]
            target_concept_ids.append(target_concept_id)

        except MAPHSAMissingMappingException as mme:
            MapperManager.add_missing_value(source_value, mme.missing_value,
                                            f"{source_meta_name}:{source_series['X']}:{source_field_name}",
                                            f"{target_table}.{target_field}")

            target_concept_id = fallback_concept_id

    if concept_list:
        target_concept_list_id = DatabaseInterface.create_concept_list(target_collection_name, target_concept_ids)
        return target_concept_list_id
    elif target_concept_id:
        return target_concept_id
    else:
        return None


def parse_env_assessment(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:

    topo_type = lcov_type = soil_class = l_use_type = bedr_geo = None

    # Topography
    topo_type = parse_env_assessment_param(sicg_site_series, 'tipoRelevo',
                                               'Topography', 'Unknown',
                                                   source_meta['name'], 'env_assessment', 'topo_type', True)
    # Land Cover
    lcov_type = parse_env_assessment_param(sicg_site_series, 'vegetacaoAtual',
                                               'Land Cover', 'Unknown',
                                               source_meta['name'], 'env_assessment', 'lcov_type', True)
    # Soil Classification
    soil_class = parse_env_assessment_param(sicg_site_series, 'tipoSolo',
                                                'Soil Classification', 'Not Specified',
                                                source_meta['name'], 'env_assessment', 'soil_class', True)
    # Land Use
    l_use_type = parse_env_assessment_param(sicg_site_series,
                                                'atividadesDesenvolvidasLocal', 'Land Use',
                                                'Unknown', source_meta['name'],
                                                'env_assessment', 'l_use_type', True)
    
    # TODO Empty value?

    bedr_geo = DatabaseInterface.create_concept_list('Bedrock Geology', [])
    env_assessment_id = DatabaseInterface.insert_entity('env_assessment', {
        'her_maphsa_id': her_maphsa_id,
        'topo_type': topo_type,
        'lcov_type': lcov_type,
        'bedr_geo': bedr_geo,
        'soil_class': soil_class,
        'l_use_type': l_use_type
    })

    # Hydrology Information

    hyd_inf_sources = []

    if not pd.isna(sicg_site_series['bacia']) and sicg_site_series['bacia'] not in [his[0] for his in hyd_inf_sources]:
        hyd_inf_sources.append((sicg_site_series['bacia'], 'bacia'))

    if not pd.isna(sicg_site_series['rio']) and sicg_site_series['rio'] not in [his[0] for his in hyd_inf_sources]:
        hyd_inf_sources.append((sicg_site_series['rio'], 'rio'))

    if not pd.isna(sicg_site_series['aguaProxima']) and sicg_site_series['aguaProxima'] not in [his[0] for his in hyd_inf_sources]:
        hyd_inf_sources.append((sicg_site_series['aguaProxima'], 'aguaProxima'))

    hydro_info = []
    for (hyd_name, hd_label) in hyd_inf_sources:
        hydro_id = parse_env_assessment_param(sicg_site_series, hd_label, 'Hydrology Type',
                                              'Not Defined', source_meta['name'], 'hydro_info', 'hydro_type')

        hydro_concept_list_id = DatabaseInterface.create_concept_list('Hydrology Type', [hydro_id])

        hydro_info.append((hyd_name, hydro_concept_list_id))

    for (hydro_name, hydro_type) in hydro_info:
        DatabaseInterface.insert_entity('hydro_info', {
            'env_assessment_id': env_assessment_id,
            'hydro_name': hydro_name,
            'hydro_type': hydro_type
        })


def parse_her_cond_ass(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:

    # Condition Assessment

    concept_id_mappings = DatabaseInterface.get_concept_id_mappings()

    recc_type_mapper = mappings.MapperManager.get_mapper('sicg', 'her_cond_ass', 'recc_type')
    recc_type_source_ids = concept_id_mappings['Recommendation Type']

    missing_recc_type_id = recc_type_source_ids['Not Defined']
    other_recc_type_id = recc_type_source_ids['Other']

    if not pd.isna(sicg_site_series['medidasPreservação']):
        try:
            recc_type_value = recc_type_mapper.get_field_mapping(sicg_site_series['medidasPreservação'])
            recc_type_ids = [recc_type_source_ids[recc_type_value]]
        except MAPHSAMissingMappingException as mme:
            recc_type_ids = [other_recc_type_id]
            MapperManager.add_missing_value(
                f"{sicg_site_series['medidasPreservação']}", mme.missing_value,
                f"{source_meta['name']}:{sicg_site_series['X']}:medidasPreservação",
                'her_cond_ass.recc_type')

    else:
        recc_type_ids = [missing_recc_type_id]

    recc_type_list_id = DatabaseInterface.create_concept_list('Recommendation Type', recc_type_ids)

    her_cond_ass_id = DatabaseInterface.insert_entity('her_cond_ass', {
        'her_maphsa_id': her_maphsa_id,
        'recc_type': recc_type_list_id
    })

    # Disturbance Event

    dist_cause_mapper = mappings.MapperManager.get_mapper('sicg', 'disturbance_event', 'dist_cause')
    dist_cause_source_ids = concept_id_mappings['Disturbance Cause']

    try:
        dist_cause_value = dist_cause_mapper.get_field_mapping(sicg_site_series['fatoresDegradacao'])

    except MAPHSAMissingMappingException as mme:
        dist_cause_value = 'Other'
        MapperManager.add_missing_value(
            f"{sicg_site_series['fatoresDegradacao']}", mme.missing_value,
            f"{source_meta['name']}:{sicg_site_series['X']}:fatoresDegradacao",
            'disturbance_event.dist_cause')

    except AttributeError as ae:
        if pd.isna(ae.obj):
            dist_cause_value = 'Not Defined'
        else:
            raise ae

    dist_cause_id = dist_cause_source_ids[dist_cause_value]

    dist_effect_source_ids = concept_id_mappings['Disturbance Effect']
    missing_dist_effect_type_id = dist_effect_source_ids['Not Visible/Known']

    dist_effect_list_id = DatabaseInterface.create_concept_list('Disturbance Effect', [missing_dist_effect_type_id])

    # Overall Damage Extent Estado.de.Conservação, Estado.de.Preservação, Entorno.do.bem

    over_dam_ext_mapper = mappings.MapperManager.get_mapper('sicg', 'disturbance_event', 'over_dam_ext')
    over_dam_ext_ids = concept_id_mappings['Overall Damage Extent']

    estado_de_conservacao = sicg_site_series['Estado.de.Conservação'] if not pd.isna(sicg_site_series['Estado.de.Conservação']) else None
    #TODO integrate these two
    estado_de_preservacao = sicg_site_series['Estado.de.Preservação'] if not pd.isna(sicg_site_series['Estado.de.Preservação']) else None
    entorno_do_bem = sicg_site_series['Entorno.do.bem'] if not pd.isna(sicg_site_series['Entorno.do.bem']) else None

    if estado_de_conservacao is not None:
        over_dam_ext_value = over_dam_ext_mapper.get_field_mapping(estado_de_conservacao)
    else:
        over_dam_ext_value = 'Unknown'

    try:
        over_dam_ext_id = over_dam_ext_ids[over_dam_ext_value]
    except KeyError as ke:
        print(ke)

    disturbance_event_id = DatabaseInterface.insert_entity('disturbance_event', {
        'her_cond_ass_id': her_cond_ass_id,
        'dist_cause': dist_cause_id,
        'dist_effect': dist_effect_list_id,
        'dist_from': 'NULL',
        'over_dam_ext': over_dam_ext_id,
    })


def verify_data_origin(source_meta: dict):
    return DatabaseInterface.verify_origin(source_meta)


def add_data_origin(source_meta: dict):
    DatabaseInterface.add_origin(source_meta)


def adjust_sicg_code(source_code):
    m = re.search(r'([A-Z]+)([0-9]+)([A-Z]{2})([A-Z]{2})([0-9]+)', source_code)
    return f"{m[1]}-{m[2]}-{m[3]}-{m[4]}-{m[5]}"


def load_supplementary_geodata(input_file: pathlib.Path, source_meta: dict, input_data_frame: pd.DataFrame):
    geodata_file_url = f"{os.path.dirname(input_file)}/{input_file.stem}{source_meta['polygon_suffix']}"
    if os.path.isfile(geodata_file_url):
        with open(geodata_file_url) as supplementary_geodata:
            supplementary_geodata = geojson.load(supplementary_geodata)
    else:
        raise IOError(f"Missing supplementary geodata {geodata_file_url}")

    input_data_frame['supp_geom'] = ""
    print("Loading supplementary geometry...")
    for site in tqdm(supplementary_geodata['features']):
        adjusted_code = adjust_sicg_code(site['properties']['co_iphan'])
        matches = input_data_frame['SICG_ID'].str.match(adjusted_code)
        if matches.sum() == 1:
            input_data_frame.loc[matches, 'supp_geom'] = geojson.dumps(site['geometry'])

    return input_data_frame


def process_input(input_files, source_meta: dict, load_supp_geodata: bool, insert_data: bool):
    data_frame_batch = {in_file.name: create_input_dataframes(in_file) for in_file in input_files}

    if load_supp_geodata:
        data_frame_batch = {in_file.name: load_supplementary_geodata(in_file, source_meta, data_frame_batch[in_file.name]) for in_file in input_files}

    for (input_resource, input_data) in data_frame_batch.items():
        source_meta['input_url'] = input_resource
        if not verify_data_origin(source_meta):
            add_data_origin(source_meta)

        input_data = clean_input_dataframe(input_data)
        parse_input_dataframe(input_data, source_meta, insert_data)

    MapperManager.print_missing_values()
