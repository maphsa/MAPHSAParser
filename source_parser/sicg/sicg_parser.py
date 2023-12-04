from io import StringIO
import re
import pathlib

import numpy as np
import pandas
import pandas as pd
from pandas import Series
from tqdm import tqdm
from geojson import Point


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
    input_dataframe['X'] = input_dataframe['X'] + 2

    input_dataframe = input_dataframe.replace('', np.NAN)
    input_dataframe = input_dataframe.replace('NA', np.NAN)
    input_dataframe = input_dataframe.dropna(axis=1, how='all')

    artifact_columns = []
    for col in input_dataframe.columns:
        if input_dataframe[col].count() < sicg_settings.MIN_COLUMN_VALUE:
            artifact_columns.append(col)

    input_dataframe = input_dataframe.drop(artifact_columns, axis=1)

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

    source_id = DatabaseInterface.insert_entity('her_source', {
        'data_origin_name': source_meta['name'],
        'location': f"Line {sicg_site_series['X']}"
    })

    her_maphsa_id = DatabaseInterface.insert_entity('her_maphsa', {
        'uuid': uuid,
        'description': f"Legacy SICG data.",
        'source_id': source_id
    })

    parse_her_geom(sicg_site_series, source_meta, her_maphsa_id)
    parse_her_loc_sum(sicg_site_series, source_meta, her_maphsa_id)
    parse_her_admin_div(sicg_site_series, source_meta, her_maphsa_id)

    parse_arch_ass(sicg_site_series, source_meta, her_maphsa_id)
    # Parsing two branches simultaneously
    parse_built_comp_her_feature(sicg_site_series, source_meta, her_maphsa_id)

    parse_her_find(sicg_site_series, source_meta, her_maphsa_id)
    parse_env_assessment(sicg_site_series, source_meta, her_maphsa_id)


def parse_her_geom(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int):
    concept_id_mappings = DatabaseInterface.get_concept_id_mappings()
    geom_ext_cert_definite_concept_id = concept_id_mappings['Geometry Extent Certainty']['Negligible']
    loc_cert_definite_concept_id = concept_id_mappings['Location Certainty']['Definite']
    loc_cert_negligible_concept_id = concept_id_mappings['Location Certainty']['Negligible']
    sys_ref_id = concept_id_mappings['Spatial Coordinates Reference System Datum']['WGS84']

    grid_id = DatabaseInterface.get_placeholder_entity_id('grid')

    obs_geo = sicg_site_series['obsGeo'] if not pd.isna(sicg_site_series['obsGeo']) else None
    if obs_geo and re.match('Georreferenciamento dentro dos limites municipais', obs_geo):
        loc_cert_concept_id = loc_cert_negligible_concept_id
    else:
        loc_cert_concept_id = loc_cert_definite_concept_id

    lat = long = None
    if not pd.isna(sicg_site_series['Latitude']) and not pd.isna(sicg_site_series['Longitude']):
        lat = sicg_site_series['Latitude']
        long = sicg_site_series['Longitude']

    her_geom_id = DatabaseInterface.insert_entity('her_geom', {
        'loc_cert': loc_cert_concept_id,
        'geom_ext_cert': geom_ext_cert_definite_concept_id,
        'sys_ref': sys_ref_id,
        'lat': 0 if lat is None else lat,
        'long': 0 if long is None else long,
        'her_maphsa_id': her_maphsa_id,
        'grid_id': grid_id,
        'wkb_geometry': "NULL"
    })

    if lat and long:
        DatabaseInterface.run_script('update_her_geom', target_data={
            'lat': lat,
            'long': long,
            'her_geom_id': her_geom_id
        })

    # TODO Add polygon from sicg_site_series['perimetro']


def parse_her_loc_sum(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int):
    gen_descr = sicg_site_series['Nome.popular']
    her_maphsa_id = her_maphsa_id

    her_loc_sum_id = DatabaseInterface.insert_entity('her_loc_sum', {
        'gen_descr': gen_descr,
        'her_maphsa_id': her_maphsa_id
    })

    parse_her_loc_name(sicg_site_series, source_meta, her_loc_sum_id)
    parse_her_loc_type(sicg_site_series, source_meta, her_loc_sum_id)


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


def parse_her_admin_div(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int):
    country_admin_type_id = DatabaseInterface.get_concept_id_mapping('Administrative Division Type', 'Country')
    municipality_admin_type_id = DatabaseInterface.get_concept_id_mapping('Administrative Division Type',
                                                                          'Municipality')
    state_admin_type_id = DatabaseInterface.get_concept_id_mapping('Administrative Division Type',
                                                                   'Municipality')

    DatabaseInterface.insert_entity('her_admin_div', {
        'admin_div_name': 'Brazil',
        'admin_type': country_admin_type_id,
        'her_maphsa_id': her_maphsa_id
    })

    if not pd.isna(sicg_site_series['UF']):
        state_value = sicg_site_series['UF']

        DatabaseInterface.insert_entity('her_admin_div', {
            'admin_div_name': state_value,
            'admin_type': state_admin_type_id,
            'her_maphsa_id': her_maphsa_id
        })

    if not pd.isna(sicg_site_series['Município']):
        municipality_value = sicg_site_series['Município']

        DatabaseInterface.insert_entity('her_admin_div', {
            'admin_div_name': municipality_value,
            'admin_type': municipality_admin_type_id,
            'her_maphsa_id': her_maphsa_id
        })

    return


def parse_arch_ass(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:
    # Previous Research Activities
    pra_ids = []

    if not pd.isna(sicg_site_series['atividadesDesenvolvidasLocal1']):
        pra_mapper = mappings.MapperManager.get_mapper('arch_ass', 'prev_res_act')
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
        shape_mapper = mappings.MapperManager.get_mapper('arch_ass', 'her_shape')
        her_shape_name = shape_mapper.get_field_mapping(sicg_site_series['forma'])
        her_shape_id = shape_mapping_ids[her_shape_name]

    # Overall Certainty
    overall_arch_cert_id = DatabaseInterface.get_concept_id_mappings()['Overall Archaeological Certainty']['Definite']
    arch_ass_id = DatabaseInterface.insert_entity('arch_ass', {
        'her_maphsa_id': her_maphsa_id,
        'prev_res_act': prev_res_act_id,
        'her_morph': 1,  # TODO
        'her_shape': her_shape_id,
        'her_loc_orient': 1,  # TODO
        'o_arch_cert': overall_arch_cert_id
    })

    # Cultural affiliation

    unconfirmed_ca_certainty_id = DatabaseInterface.get_concept_id_mappings()['Cultural Affiliation Certainty'][
        'Confirmed']
    ca_mapping_ids = DatabaseInterface.get_concept_id_mappings()['Cultural Affiliation']
    ca_mapper = mappings.MapperManager.get_mapper('site_cult_aff', 'cult_aff')
    ca_names: set = set()

    def is_valid_ca_value(source_value: str) -> bool:
        return not pd.isna(source_value) and source_value not in ('.', '?', '-')

    if is_valid_ca_value(sicg_site_series['tradicoesArtefatosCeramicos']):
        try:
            ca_names = ca_names.union(ca_mapper.get_field_mappings(sicg_site_series['tradicoesArtefatosCeramicos']))
        except MAPHSAMissingMappingException:
            MapperManager.add_missing_value(sicg_site_series['tradicoesArtefatosCeramicos'],
                                            f"{source_meta['name']}:{sicg_site_series['X']}:tradicoesArtefatosCeramicos",
                                            'site_cult_aff.cult_aff')
            ca_names.add('Other')

    if is_valid_ca_value(sicg_site_series['fasesArtefatosCeramicos']):
        try:
            ca_names = ca_names.union(ca_mapper.get_field_mappings(sicg_site_series['fasesArtefatosCeramicos']))
        except MAPHSAMissingMappingException:
            MapperManager.add_missing_value(sicg_site_series['fasesArtefatosCeramicos'],
                                            f"{source_meta['name']}:{sicg_site_series['X']}:fasesArtefatosCeramicos",
                                            'site_cult_aff.cult_aff')
            ca_names.add('Other')

    if is_valid_ca_value(sicg_site_series['tradicoesArtefatosLiticos']):
        try:
            ca_names = ca_names.union(ca_mapper.get_field_mappings(sicg_site_series['tradicoesArtefatosLiticos']))
        except MAPHSAMissingMappingException:
            MapperManager.add_missing_value(sicg_site_series['tradicoesArtefatosLiticos'],
                                            f"{source_meta['name']}:{sicg_site_series['X']}:tradicoesArtefatosLiticos",
                                            'site_cult_aff.cult_aff')
            ca_names.add('Other')

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
            'cult_aff_certainty': unconfirmed_ca_certainty_id

        })

    # Period

    dated_ca_names = [ca_name for ca_name in ca_names if ca_name not in ('Other', 'Not Informed')]

    dates = []
    if len(dated_ca_names) > 0:
        date_mapper = mappings.MapperManager.get_mapper('sites_timespace', 'from_to_date')
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
        function_mapper = mappings.MapperManager.get_mapper('her_loc_funct', 'her_loc_funct')
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
            MapperManager.add_missing_value(f"{sicg_site_series[source_measurement_field[0]]}:{source_measurement_field[1]}:{source_measurement_field[2]}",
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
        except MAPHSAMissingMappingException:
            built_comp_id = None

        try:
            her_feature_id = parse_her_feature(sicg_site_series, source_meta, her_maphsa_id)
        except MAPHSAMissingMappingException:
            her_feature_id = None

        if not built_comp_id and not her_feature_id and not pd.isna(sicg_site_series['estruturas']):
            MapperManager.add_missing_value(sicg_site_series['estruturas'],
                                            f"{source_meta['name']}:{sicg_site_series['X']}:estruturas",
                                            'built_comp.comp_type/her_feature.feat_type')

    return built_comp_id, her_maphsa_id


def parse_built_comp(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:
    estruturas_value = sicg_site_series['estruturas']

    comp_type_concept_names = mappings.MapperManager.get_mapper('built_comp', 'comp_type')
    comp_type_concept_ids = DatabaseInterface.get_concept_id_mappings()['Component Type']

    comp_type_concept_name = comp_type_concept_names.get_field_mapping(estruturas_value)

    comp_type = comp_type_concept_ids[comp_type_concept_name]

    built_comp_id = DatabaseInterface.insert_entity('built_comp', {
        'her_maphsa_id': her_maphsa_id,
        'comp_type': comp_type,
        'comp_mat': 'NULL',
        'comp_const_tech': 'NULL'
    })

    return built_comp_id


def parse_her_feature(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:
    estruturas_value = sicg_site_series['estruturas']

    feat_type_concept_names = mappings.MapperManager.get_mapper('her_feature', 'feat_type')
    feat_type_concept_ids = DatabaseInterface.get_concept_id_mappings()['Feature Type']

    feat_type_concept_name = feat_type_concept_names.get_field_mapping(estruturas_value)

    feat_type = feat_type_concept_ids[feat_type_concept_name]

    her_feature_id = DatabaseInterface.insert_entity('her_feature', {
        'her_maphsa_id': her_maphsa_id,
        'feat_type': feat_type,
        'feat_count': 1
    })

    return her_feature_id


def parse_her_find(sicg_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:
    artefact_category_ids = []

    if not pd.isna(sicg_site_series['artefatos']):

        artefatos_value = sicg_site_series['artefatos']

        art_cat_concept_names = mappings.MapperManager.get_mapper('her_find', 'art_cat_concept_list_id')
        art_cat_concept_ids = DatabaseInterface.get_concept_id_mappings()['Artefact Category']

        try:
            art_cat_concept_name = art_cat_concept_names.get_field_mapping(artefatos_value)
        except MAPHSAMissingMappingException:
            MapperManager.add_missing_value(artefatos_value,
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
    concept_names = mappings.MapperManager.get_mapper(target_table, target_field)
    concept_ids = DatabaseInterface.get_concept_id_mappings()[target_collection_name]
    fallback_concept_id = DatabaseInterface.get_concept_id_mappings()[target_collection_name][fallback_concept_name]

    target_concept_ids = []

    if source_value is not None:
        try:
            target_concept_name = concept_names.get_field_mapping(source_value)
            target_concept_id = concept_ids[target_concept_name]
            target_concept_ids.append(target_concept_id)

        except MAPHSAMissingMappingException:
            MapperManager.add_missing_value(source_value,
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
    recc_type = concept_id_mappings['Recommendation Type']['Not Defined']

    her_cond_ass_id = DatabaseInterface.insert_entity('her_cond_ass', {
        'her_maphsa_id': her_maphsa_id,
        'recc_type': recc_type,
        'cond_assessor': f"{source_meta['name']}:{sicg_site_series['X']}",
    })


def verify_data_origin(source_meta: dict):
    return DatabaseInterface.verify_origin(source_meta)


def add_data_origin(source_meta: dict):
    DatabaseInterface.add_origin(source_meta)


def process_input(input_files, source_meta: dict, insert_data: bool):
    data_frame_batch = {in_file.stem: create_input_dataframes(in_file) for in_file in input_files}

    if not verify_data_origin(source_meta):
        add_data_origin(source_meta)

    for (input_resource, input_data) in data_frame_batch.items():
        input_data = clean_input_dataframe(input_data)
        parse_input_dataframe(input_data, source_meta, insert_data)

    MapperManager.print_missing_values()
