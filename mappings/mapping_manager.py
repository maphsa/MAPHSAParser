
import json

from mappings.mappers.icanh.icanh_mappers import ICANHMapper
from mappings.mappers.sicg.sicg_mappers import SICGMapper, SICGPreviousResearchActivitiesMapper, SICGCulturalAffiliationMapper, \
    SICGComponentTypeMapper, SICGFeatureTypeMapper, SICGArtefactCategoryMapper, SICGEnvironmentAssessmentParamMapper, \
    SICGHydrologyTypeMapper
from exceptions import MAPHSAParserException

import pandas as pd

from source_parser import ExistingSources


class MapperManager:

    active_mappers = {}
    missing_values: pd.DataFrame = pd.DataFrame(columns=["value", "filtered_value", "source", "target", "count"])

    default_mappers = {
        ExistingSources.sicg.value: SICGMapper,
        ExistingSources.icanh.value: ICANHMapper,
    }

    sicg_specialized_mappers = {
        'arch_ass.prev_res_act': SICGPreviousResearchActivitiesMapper,
        'site_cult_aff.cult_aff': SICGCulturalAffiliationMapper,
        'built_comp.comp_type': SICGComponentTypeMapper,
        'her_feature.feat_type': SICGFeatureTypeMapper,
        'her_find.art_cat_concept_list_id': SICGArtefactCategoryMapper,
        'env_assessment.topo_type': SICGEnvironmentAssessmentParamMapper,
        'env_assessment.lcov_type': SICGEnvironmentAssessmentParamMapper,
        'env_assessment.soil_class': SICGEnvironmentAssessmentParamMapper,
        'env_assessment.l_use_type': SICGEnvironmentAssessmentParamMapper,
        'hydro_info.hydro_type': SICGHydrologyTypeMapper,
    }

    icanh_specialized_mapper_source = {
        'her_geom.loc_cert': 'Site Location Certainty',
        'her_loc_name.her_loc_name_type': 'Heritage Location Name Type',
        'her_loc_type.her_loc_type': 'Heritage Location Type',
        'her_admin_div.admin_type': 'Administrative Division Type',
        'arch_ass.her_morph': 'Overall Morphology',
        'arch_ass.her_shape': 'Shape',
        'site_cult_aff.cult_aff': 'Cultural Affiliation',
        'her_loc_funct.her_loc_funct': 'Heritage Location Function',
        'her_loc_funct.her_loc_fun_cert': 'Heritage Location Function Certainty',
        'her_loc_meas.her_dimen': 'Dimension',
        'her_loc_meas.her_meas_unit': 'Measurement Unit',
        'her_loc_meas.her_meas_type': 'Measurement Type',
    }

    specialized_mapper_indexes = {
        ExistingSources.sicg.value: sicg_specialized_mappers,

    }

    @classmethod
    def get_mapper(cls, source_name: str, table_name: str, field_name: str):

        try:
            mapper_key = f"{table_name}.{field_name}"

            # If the mapper has not been loaded, load it
            if mapper_key not in cls.active_mappers.keys():

                if source_name == ExistingSources.icanh.value:
                    mapper_class = ICANHMapper
                else:
                    specialized_mapper_index = cls.specialized_mapper_indexes[source_name]
                    mapper_class = specialized_mapper_index[mapper_key] \
                        if mapper_key in specialized_mapper_index.keys() else SICGMapper

                if source_name == ExistingSources.icanh.value:
                    mapping_file_url = f"mappings/mappers/{source_name}/master_mapper.json"
                    mapping_subindex = cls.icanh_specialized_mapper_source[f"{table_name}.{field_name}"]
                    master_mappings = json.load(open(mapping_file_url, 'r'))
                    mappings = master_mappings[mapping_subindex]

                else:
                    mapping_file_url = f"mappings/mappers/{source_name}/{table_name}.{field_name}.json"
                    mappings = json.load(open(mapping_file_url, 'r'))

                cls.active_mappers[mapper_key] = mapper_class(mappings, f"{table_name}.{field_name}")

            mapper = cls.active_mappers[mapper_key]

        except Exception:
            raise MAPHSAParserException(f"Unable to get mapper file for {source_name} {table_name}.{field_name}")

        return mapper

    @classmethod
    def add_missing_value(cls, value: str, filtered_value: str, source: str, target: str) -> object:
        if cls.missing_values[(cls.missing_values['value'].values == value) &
                              (cls.missing_values['target'].values == target)].count().value == 0:
            cls.missing_values.loc[-1] = [value, filtered_value, source, target, 1]
            cls.missing_values.index = cls.missing_values.index + 1
        else:
            cls.missing_values.loc[(cls.missing_values['value'].values == value) &
                                   (cls.missing_values['target'].values == target), 'count'] += 1

    @classmethod
    def print_missing_values(cls):
        cls.missing_values.to_csv('missing_values.csv', sep=',', encoding='utf-8', index=False)
