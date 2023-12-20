
import json

from mappings.mappers.mappers import Mapper, PreviousResearchActivitiesMapper, CulturalAffiliationMapper, \
    ComponentTypeMapper, FeatureTypeMapper, ArtefactCategoryMapper, EnvironmentAssessmentParamMapper, \
    HydrologyTypeMapper
from exceptions import MAPHSAParserException

import pandas as pd


class MapperManager:

    active_mappers = {}
    missing_values: pd.DataFrame = pd.DataFrame(columns=["value", "filtered_value", "source", "target", "count"])

    specialized_mappers = {
        'arch_ass.prev_res_act': PreviousResearchActivitiesMapper,
        'site_cult_aff.cult_aff': CulturalAffiliationMapper,
        'built_comp.comp_type': ComponentTypeMapper,
        'her_feature.feat_type': FeatureTypeMapper,
        'her_find.art_cat_concept_list_id': ArtefactCategoryMapper,
        'env_assessment.topo_type': EnvironmentAssessmentParamMapper,
        'env_assessment.lcov_type': EnvironmentAssessmentParamMapper,
        'env_assessment.soil_class': EnvironmentAssessmentParamMapper,
        'env_assessment.l_use_type': EnvironmentAssessmentParamMapper,
        'hydro_info.hydro_type': HydrologyTypeMapper,
    }

    @classmethod
    def get_mapper(cls, table_name: str, field_name: str):

        try:
            mapper_key = f"{table_name}.{field_name}"

            mapper_class = cls.specialized_mappers[mapper_key] if mapper_key in cls.specialized_mappers.keys()\
                else Mapper

            if mapper_key not in cls.active_mappers.keys():
                mapping_file_url = f"mappings/mappers/{table_name}.{field_name}.json"
                mappings = json.load(open(mapping_file_url, 'r'))
                cls.active_mappers[mapper_key] = mapper_class(mappings, f"{table_name}.{field_name}")

            mapper = cls.active_mappers[mapper_key]

        except Exception:
            raise MAPHSAParserException(f"Unable to get mapper file for {table_name}.{field_name}")

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
