from io import StringIO
import pathlib

import geojson
import pandas as pd
from pandas import Series
from shapely import Point
from tqdm import tqdm
from shapely.geometry import shape

import id_cipher
import mappings
from database_interface import DatabaseInterface
from exceptions import MAPHSAParserException, MAPHSAMissingMappingException
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

    parse_her_geom(icanh_site_series, source_meta, her_maphsa_id)

    parse_her_loc_sum(icanh_site_series, source_meta, her_maphsa_id)

    parse_her_admin_div(icanh_site_series, source_meta, her_maphsa_id)

    parse_arch_ass(icanh_site_series, source_meta, her_maphsa_id)

    parse_her_feature(icanh_site_series, source_meta, her_maphsa_id)

    parse_her_find(icanh_site_series, source_meta, her_maphsa_id)

    parse_env_assessment(icanh_site_series, source_meta, her_maphsa_id)


def map_icanh_value(source_value, target_arches_collection_name, target_table_name,
                    target_field_name, fallback_value=None):
    concept_id_mappings = DatabaseInterface.get_concept_id_mappings()
    target_concept_id_mappings = concept_id_mappings[target_arches_collection_name]
    if not pd.isna(source_value):
        mapper = MapperManager.get_mapper('icanh', target_table_name, target_field_name)
        name = mapper.get_field_mapping(source_value)
        return target_concept_id_mappings[name]
    elif fallback_value is not None:
        return target_concept_id_mappings[fallback_value]
    else:
        raise ValueError(f"Missing source and fallback values for mapping {source_value}"
                         f" into {target_arches_collection_name} at icanh.{target_table_name}.{target_field_name}")


def map_polymorphic_field(source_value, target_arches_collection_name, target_table_name, target_field_name,
                          fallback_value=None) -> list:
    if pd.isna(source_value):
        if fallback_value is None:
            raise ValueError(f"Missing fallback value for source value mapping {source_value}"
                             f" into {target_table_name}.{target_field_name}"
                             f" using {target_arches_collection_name} collection")
        source_values = [fallback_value]
    else:
        source_values = polymorphic_field_to_list(source_value)

    mapped_values = set()
    # Land cover had and empty value
    for source_value in [v for v in source_values if v != '']:
        mapped_value = map_icanh_value(source_value, target_arches_collection_name, target_table_name,
                                       target_field_name)
        mapped_values.add(mapped_value)

    return list(mapped_values)


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

    her_morph_id = next(iter(mapped_her_morph_values))  # TODO disambiguate or reduce somehow

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

    # Heritage Location Measurement

    # Dimension

    if not pd.isna(icanh_site_series['Measurement Value']): # TODO some measurements have no value, inquire

        if str(icanh_site_series['Measurement Value']).count('.') > 1: #TODO Ask about odd hectare value, ignoring second point in the string
            icanh_site_series['Measurement Value'] = '.'.join(icanh_site_series['Measurement Value'].split('.')[:-1])

        if pd.isna(icanh_site_series['Measurement Unit']):
            print(f"Missing measurement unit for {icanh_site_series['ICANH_ID']}, falling back to m2") #TODO ask about this, line 27
            icanh_site_series['Measurement Unit'] = 'square meters'

        mapped_her_dimen_values = map_polymorphic_field(icanh_site_series['Dimension'], 'Dimension', 'her_loc_meas',
                                                        'her_dimen', 'unknown')
        her_dimen_id = mapped_her_dimen_values[0]  # TODO Find out why some dimensions cells have two values but are using m2. We're keeping only the area value
                                                   # TODO Also find out why some elevations are thousands of meters high

        her_meas_unit_id = map_icanh_value(icanh_site_series['Measurement Unit'],
                                         'Measurement Unit',
                                         'her_loc_meas', 'her_meas_unit')

        her_meas_type_id = map_icanh_value(icanh_site_series['Measurement Type'], 'Measurement Type', 'her_loc_meas',
                                        'her_meas_type')

        her_loc_meas_id = DatabaseInterface.insert_entity('her_loc_meas', {
            'her_dimen': her_dimen_id,
            'her_meas_unit': her_meas_unit_id,
            'her_meas_type': her_meas_type_id,
            'her_meas_value': icanh_site_series['Measurement Value'],
            'arch_ass_id': arch_ass_id
        })

        return arch_ass_id


def parse_her_feature(icanh_site_series: Series, source_meta: dict, her_maphsa_id: int):
    if not pd.isna(icanh_site_series['Feature Type']):

        feat_type_source = icanh_site_series['Feature Type']
        feat_count_source = icanh_site_series['Feature Count'] if not pd.isna(icanh_site_series['Feature Count']) else 1

        feat_type_values = map_polymorphic_field(feat_type_source, "Feature Type", "her_feature", "feat_type")

        for feat_type_value in feat_type_values:

            her_feature_id = DatabaseInterface.insert_entity('her_feature', {
                'her_maphsa_id': her_maphsa_id,
                'feat_type': feat_type_value,
                'feat_count': feat_count_source
            })

        return her_feature_id

    else:
        return


def parse_her_find(icanh_site_series: Series, source_meta: dict, her_maphsa_id: int):
    art_cat_values = []
    if not pd.isna(icanh_site_series['Artefact Category']):

        art_cat_values = map_polymorphic_field(icanh_site_series['Artefact Category'], "Artefact Category", 'her_find', 'art_cat_concept_list_id')

    art_cat_concept_list_id = DatabaseInterface.create_concept_list('Artefact Category', art_cat_values)

    her_find_id = DatabaseInterface.insert_entity('her_find', {
        'her_maphsa_id': her_maphsa_id,
        'art_cat_concept_list_id': art_cat_concept_list_id
    })

    return her_find_id


def parse_env_assessment(icanh_site_series: Series, source_meta: dict, her_maphsa_id: int) -> int:
    topo_type_values = lcov_type_values = bedr_geo_values = soil_class_values = l_use_type_values = []

    # Topography
    if not pd.isna(icanh_site_series['Topography']):
        topo_type_values = map_polymorphic_field(icanh_site_series['Topography'], 'Topography', 'env_assessment', 'topo_type')
    # Land Cover
    if not pd.isna(icanh_site_series['Land Cover']):
        lcov_type_values = map_polymorphic_field(icanh_site_series['Land Cover'], 'Land Cover', 'env_assessment', 'lcov_type')
    if not pd.isna(icanh_site_series['Land Cover.1']):
        lcov_type_values = lcov_type_values + map_polymorphic_field(icanh_site_series['Land Cover.1'], 'Land Cover', 'env_assessment', 'lcov_type')

    # Bedrock Geology TODO Empty value?

    # Soil Classification TODO Wrong values that do not fit our thesaurus

    # Land Use
    if not pd.isna(icanh_site_series['Land Use']):
        lcov_type_values = map_polymorphic_field(icanh_site_series['Land Use'], 'Land Use', 'env_assessment', 'l_use_type')

    env_assessment_id = DatabaseInterface.insert_entity('env_assessment', {
        'her_maphsa_id': her_maphsa_id,
        'topo_type': DatabaseInterface.create_concept_list('Topography', topo_type_values),
        'lcov_type': DatabaseInterface.create_concept_list('Land Cover', lcov_type_values),
        'bedr_geo': DatabaseInterface.create_concept_list('Bedrock Geology', bedr_geo_values),
        'soil_class': DatabaseInterface.create_concept_list('Soil Classification', soil_class_values),
        'l_use_type': DatabaseInterface.create_concept_list('Land Use', l_use_type_values),
    })

    # Hydrology Information
    # Hydrology Type # TODO names are not of hydrological subjects, but indications
    if not pd.isna(icanh_site_series['Hydrology Type']):
        hydro_type_source_values = polymorphic_field_to_list(icanh_site_series['Hydrology Type'])

        for hydro_type_source_value in hydro_type_source_values:

            hydro_type_id = map_icanh_value(hydro_type_source_value, 'Hydrology Type', 'hydro_info', 'hydro_type')
            DatabaseInterface.insert_entity('hydro_info', {
                'env_assessment_id': env_assessment_id,
                'hydro_name': hydro_type_source_value,
                'hydro_type': DatabaseInterface.create_concept_list('Hydrology Type', [hydro_type_id])
            })


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
            print("MAPHSAParserException occurred")
            print(mpe)


def process_input(input_files, source_meta: dict, load_supp_geodata: bool, insert_data: bool):
    data_frame_batch = {in_file.stem: create_input_dataframes(in_file) for in_file in input_files}

    if not DatabaseInterface.verify_origin(source_meta):
        DatabaseInterface.add_origin(source_meta)

    for (input_resource, input_data) in data_frame_batch.items():
        input_data = clean_input_dataframe(input_data)
        parse_input_dataframe(input_data, source_meta, insert_data)
