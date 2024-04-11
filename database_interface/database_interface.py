import argparse
import subprocess
import types

import psycopg2
from psycopg2.errors import SyntaxError
from jinja2 import Template
import json
from uuid import UUID
import re

import database_interface
from database_interface import db_settings
from exceptions.exceptions import MAPHSAParseInsertionException


class DatabaseInterface:
    _connection = None
    _origin_id_mappings = None
    _concept_id_mappings = None
    _placeholder_entity_id_mappings = {}

    @classmethod
    def get_connection(cls):

        if cls._connection is None:
            cls.initialize()

        return cls._connection

    @classmethod
    def initialize(cls):
        if cls._connection is None:
            cls._connection = psycopg2.connect(
                database=db_settings.DB_NAME,
                user=db_settings.DB_USERNAME,
                password=db_settings.DB_PASSWORD,
                host=db_settings.DB_HOST,
                port=db_settings.DB_PORT,
            )

            cls._connection.autocommit = db_settings.DB_AUTOCOMMIT
            cls._connection.isolation_level = db_settings.DB_ISOLATION_LEVEL

    @classmethod
    def start_transaction(cls):
        cls.get_connection().autocommit = False
        cls.get_connection().isolation_level = 1

    @classmethod
    def abort_transaction(cls):
        cls.get_connection().rollback()
        cls.get_connection().autocommit = db_settings.DB_AUTOCOMMIT
        cls.get_connection().isolation_level = db_settings.DB_ISOLATION_LEVEL

    @classmethod
    def commit_transaction(cls):
        cls.get_connection().commit()
        cls.get_connection().autocommit = db_settings.DB_AUTOCOMMIT
        cls.get_connection().isolation_level = db_settings.DB_ISOLATION_LEVEL

    @classmethod
    def get_connection_cursor(cls):

        return cls.get_connection().cursor()

    @classmethod
    def add_schema_triggers(cls):
        cls.run_script(db_settings.DB_CONCEPT_LIST_FUNCTION_SCRIPT, {})
        with open(f"{db_settings.DB_SCRIPT_PATH}/conceptListTriggeredTables.json", 'r') as infile:
            concept_list_triggered_tables = json.load(infile)
            for cltt in concept_list_triggered_tables:
                (table_name, column_name, thesaurus_name) = cltt

                cls.run_script(db_settings.DB_CONCEPT_LIST_TRIGGER_SCRIPT, {
                    'table_name': table_name,
                    'column_name': column_name,
                    'thesaurus_name': thesaurus_name
                })

    @classmethod
    def run_post_process_command(cls, ppc):
        curs = cls.get_connection_cursor()
        curs.execute(open(f"{db_settings.DB_SCRIPT_PATH}/{ppc}", 'r').read())
        curs.close()

    @classmethod
    def purge_database(cls):
        curs = cls.get_connection_cursor()
        curs.execute(open(db_settings.DB_PURGE_SCRIPT, 'r').read())
        curs.close()

    @classmethod
    def insert_master_rows(cls):
        curs = cls.get_connection_cursor()
        curs.execute(open(db_settings.DB_MASTER_ROW_SCRIPT, 'r').read())
        curs.close()

    @classmethod
    def build_database(cls):
        curs = cls.get_connection_cursor()
        curs.execute(open(db_settings.DB_DEPLOYMENT_SCRIPT, 'r').read())
        curs.close()

    @classmethod
    def load_extent(cls):
        load_extent_template = open(db_settings.DB_LOAD_EXTENT_SCRIPT, 'r').read()
        j2_template = Template(load_extent_template)
        load_extent_command = j2_template.render({'CRS': db_settings.DB_EXTENT_CRS,
                                                  'shapefile_url': db_settings.DB_EXTENT_SHAPEFILE_URL,
                                                  'schema_name': 'public',
                                                  'table_name': 'extent',
                                                  'db_name': db_settings.DB_NAME,
                                                  'db_url': db_settings.DB_HOST,
                                                  'username': db_settings.DB_USERNAME
                                                  })
        subprocess.run(load_extent_command, text=True, shell=True)

    @classmethod
    def filter_concept_string(cls, cs: str) -> str:
        return cs.replace("'", "''")

    @classmethod
    def concept_is_present(cls, concept_string, thesaurus_name):

        select_concept_template = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/select_concept.j2", 'r').read()
        j2_template = Template(select_concept_template)
        select_concept_query = j2_template.render({'concept_string': concept_string,
                                                   'thesaurus_name': thesaurus_name
                                                   })
        try:
            curs = cls.get_connection_cursor()
            curs.execute(select_concept_query)
        except Exception as e:
            print(f"{type(e)} occurred while selecting concept {concept_string}")
            print(e)

        cardinality = len(curs.fetchall())

        if cardinality > 1:
            raise ValueError(f"{concept_string} is present more than once in thesaurus {thesaurus_name}")

        return cardinality == 1

    @classmethod
    def filter_concepts_to_append(cls, concept_data) -> dict:
        concept_data['concepts'] = {concept_string: description
                                    for concept_string, description in concept_data['concepts'].items()
                                    if not
                                    DatabaseInterface.concept_is_present(cls.filter_concept_string(concept_string),
                                                                         concept_data['thesaurus_title'])}
        print(f"{list(concept_data['concepts'].keys())} "
              f"new concepts found in {concept_data['thesaurus_title']}")
        return concept_data

    @classmethod
    def insert_concepts(cls, concept_data: dict, append: bool = False, confirm: bool = False):

        db_settings.SKIP_INSERT_CONCEPT_CONFIRMATION = confirm | db_settings.SKIP_INSERT_CONCEPT_CONFIRMATION

        if append:
            DatabaseInterface.filter_concepts_to_append(concept_data)

        confirmation_prompt = ''

        thesaurus_name = concept_data['thesaurus_title']
        concept_cardinality = len(concept_data['concepts'])

        if append and concept_cardinality == 0:
            print(f"No new concepts to append to {thesaurus_name}, skipping")
            return

        while not db_settings.SKIP_INSERT_CONCEPT_CONFIRMATION and confirmation_prompt not in ['y', 'n', 'a']:
            verb = "Insert" if not append else "Append"
            confirmation_prompt = input(f"{verb} {concept_cardinality} new concepts to thesaurus "
                                        f"{thesaurus_name}? (y/n/a)\n")

        if confirmation_prompt == 'n':
            return

        if confirmation_prompt == 'a':
            db_settings.SKIP_INSERT_CONCEPT_CONFIRMATION = True

        curs = cls.get_connection_cursor()

        if not append:
            print(f"Inserting thesaurus {thesaurus_name} including {concept_cardinality} concepts")

            insert_thesaurus_template = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/insert_thesaurus.j2", 'r').read()
            j2_template = Template(insert_thesaurus_template)
            insert_query = j2_template.render({'thesaurus_id': 'DEFAULT',
                                               'thesaurus_name': thesaurus_name,
                                               'thesaurus_description': thesaurus_name
                                               })

            try:
                curs.execute(insert_query)
                thesaurus_index = curs.fetchone()[0]
            except Exception as e:
                print(f"{type(e)} occurred while appending to thesaurus {thesaurus_name}")
                print(e)
                raise e

        else:
            print(f"Appending {concept_cardinality} new concepts into thesaurus {thesaurus_name}")
            select_thesaurus_template = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/select_thesaurus.j2", 'r').read()
            j2_template = Template(select_thesaurus_template)
            select_query = j2_template.render({'thesaurus_name': thesaurus_name})

            try:
                curs.execute(select_query)
                thesaurus_index = curs.fetchone()[0]
            except TypeError as te:
                print(f"{te}")
                print(f"Thesaurus {thesaurus_name} missing? Perhaps use non-append concept insertion")
                curs.close()
                raise te
            except Exception as e:
                print(f"{type(e)} occurred while selecting thesaurus {thesaurus_name}")
                print(e)
                raise e

        insert_concept_template = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/insert_concept.j2", 'r').read()

        for (concept_string, concept_description) in concept_data['concepts'].items():
            if append and DatabaseInterface.concept_is_present(concept_string, thesaurus_name):
                continue
            elif append:
                print(f"Appending concept {concept_string} to thesaurus {thesaurus_name}")

            # TODO sloppy hack, this might be a more general problem with all the strings
            concept_string = concept_string.replace("'", "''")
            concept_description = concept_description.replace("'", "''") if concept_description else ""
            j2_template = Template(insert_concept_template)
            insert_query = j2_template.render({'concept_id': 'DEFAULT',
                                               'concept_field': concept_string,
                                               'concept_string': concept_string,
                                               'concept_description': concept_description,
                                               'concept_thesaurus_id': thesaurus_index
                                               })
            try:
                curs.execute(insert_query)
            except Exception as e:
                print(f"{type(e)} occurred while inserting concept {concept_string}")
                print(e)
                raise e

        curs.close()

    @classmethod
    def get_concept_id_mapping(cls, thesaurus_string: str, concept_string: str) -> int:
        concept_id_mappings = cls.get_concept_id_mappings()
        return concept_id_mappings[thesaurus_string][concept_string]

    @classmethod
    def get_concept_id_mappings(cls):

        if cls._concept_id_mappings is None:
            select_sources_string = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/select_concepts.j2", 'r').read()
            select_sources_template = Template(select_sources_string)
            select_query = select_sources_template.render()

            cursor = cls.get_connection_cursor()
            cursor.execute(select_query)
            result = cursor.fetchall()

            concept_id_mappings = {}
            for (concept_id, concept_string, thesaurus_string) in result:
                if thesaurus_string not in concept_id_mappings.keys():
                    concept_id_mappings[thesaurus_string] = {}
                concept_id_mappings[thesaurus_string][concept_string] = concept_id

            cls._concept_id_mappings = concept_id_mappings

        return cls._concept_id_mappings

    @classmethod
    def create_concept_list(cls, concept_list_value: str, concept_ids: list) -> int:

        try:

            insert_concept_list_template = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/insert_concept_list.j2",
                                                'r').read()
            j2_template = Template(insert_concept_list_template)
            insert_query = j2_template.render({'concept_list_value': concept_list_value})

            curs = cls.get_connection_cursor()
            curs.execute(insert_query)
            concept_list_id = curs.fetchone()[0]

            for concept_id in concept_ids:
                insert_cl_to_con_template = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/insert_cl_to_con.j2", 'r').read()
                j2_template = Template(insert_cl_to_con_template)
                insert_query = j2_template.render({'concept_list_id': concept_list_id,
                                                   'concept_id': concept_id})
                curs.execute(insert_query)

            curs.close()
            return concept_list_id

        except Exception as e:
            print(f"Exception while creating concept list {concept_list_value}")
            print(e)

    @classmethod
    def clean_insert_data(cls, target_data: dict) -> dict:
        for (k, v) in target_data.items():
            if type(v) is str:
                target_data[k] = str(v).replace("'", "''")

        return target_data

    @classmethod
    def insert_entity(cls, target_table: str, target_data: dict) -> int:

        target_data = cls.clean_insert_data(target_data)
        insert_template_string = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/insert_{target_table}.j2", 'r').read()
        insert_template = Template(insert_template_string)
        insert_query = insert_template.render(target_data)
        curs = cls.get_connection_cursor()
        try:
            curs.execute(insert_query)
            entity_id = curs.fetchone()[0]
        except psycopg2.errors.Error as e:
            raise (MAPHSAParseInsertionException(f"Error{e.pgcode}: {e.pgerror}", query=insert_query,
                                                 parse_data=target_data))
        curs.close()
        return entity_id

    @classmethod
    def get_information_resource_id(cls, source_meta):

        select_information_resource_string = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/select_information_resource.j2",
                                                  'r').read()
        select_information_resource_template = Template(select_information_resource_string)
        select_query = select_information_resource_template.render({'domain': str(source_meta['namespace'])})

        cursor = cls.get_connection_cursor()
        cursor.execute(select_query)
        result = cursor.fetchall()

        if len(result) == 1:
            return result[0][0]
        else:
            return None

    @classmethod
    def verify_origin(cls, source_meta: dict) -> bool:
        # TODO This is old logic, should be deprecated
        select_data_origins_string = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/select_data_origins.j2", 'r').read()
        select_data_origins_template = Template(select_data_origins_string)
        select_query = select_data_origins_template.render({'name_string': source_meta['name']})

        cursor = cls.get_connection_cursor()
        cursor.execute(select_query)
        result = cursor.fetchall()

        if len(result) == 0:
            return False

        return DatabaseInterface.get_information_resource_id(source_meta) is not None

    @classmethod
    def get_db_origin_id(cls):

        select_query = ("SELECT concept_id FROM concept_table ct WHERE ct.concept_thesaurus_id = "
                        "(SELECT cth.id FROM concept_thesaurus cth WHERE cth.name LIKE 'Information Resource Type') "
                        "AND ct.concept_string LIKE 'Database';")

        cursor = cls.get_connection_cursor()
        cursor.execute(select_query)
        return cursor.fetchall()[0][0]

    @classmethod
    def add_origin(cls, source_meta: dict):

        insert_data_origins_string = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/insert_data_origin.j2", 'r').read()
        insert_data_origins_template = Template(insert_data_origins_string)

        # Using IVI's solution from https://stackoverflow.com/questions/36588126/uuid-is-not-json-serializable
        class SourceMetaEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, UUID):
                    return obj.hex
                if isinstance(obj, types.ModuleType):
                    return re.search("module '([A-z_.]*)'", obj.__str__()).group(1)
                return json.JSONEncoder.default(self, obj)

        insert_query = insert_data_origins_template.render(
            {
                'name_string': source_meta['name'],
                'json_data': json.dumps(source_meta, cls=SourceMetaEncoder)
            }
        )

        cursor = cls.get_connection_cursor()
        cursor.execute(insert_query)

        # TODO this is the new origin architecture
        db_origin_id = DatabaseInterface.get_db_origin_id()
        insert_info_source_string = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/insert_information_source.j2", 'r').read()
        insert_info_source_template = Template(insert_info_source_string)

        insert_query = insert_info_source_template.render(
            {
                'domain': str(source_meta['namespace']),
                'description': source_meta['source_description'],
                'database_type_id': db_origin_id,
                'url': source_meta['input_url']
            }
        )

        cursor = cls.get_connection_cursor()
        cursor.execute(insert_query)

        return

    @classmethod
    def run_script(cls, script_name: str, target_data: dict, fetch_return: bool = False):

        return_value = None

        target_data = cls.clean_insert_data(target_data)
        script_string = open(f"{db_settings.DB_TEMPLATE_URL_PATH}/{script_name}.j2", 'r').read()
        script_template = Template(script_string)
        script_query = script_template.render(target_data)
        curs = cls.get_connection_cursor()
        try:
            curs.execute(script_query)
            if fetch_return:
                return_value = curs.fetchall()

        except psycopg2.errors.DataError as e:
            raise (MAPHSAParseInsertionException(f"Error{e.pgcode}: {e.pgerror}", query=script_query))
        curs.close()

        if return_value:
            return return_value
        else:
            return

    @classmethod
    def process_subcommand(cls, args: argparse.Namespace):

        if args.subcommand[1] == database_interface.BUILD_DATABASE:
            print(f"Rebuilding database {db_settings.DB_NAME} at {db_settings.DB_HOST}:{db_settings.DB_PORT} using "
                  f"{db_settings.DB_DEPLOYMENT_SCRIPT}")
            confirmation_prompt = input("Proceed?(y/n)\n") if args.yes is False else 'y'

            if confirmation_prompt != 'y':
                quit()

            print(f"Purging database...")
            cls.purge_database()
            print(f"Building database...")
            cls.build_database()
            print(f"Adding schema triggers...")
            cls.add_schema_triggers()
            print(f"Loading extent...")
            cls.load_extent()
            print(f"Done")

        elif args.subcommand[1] == database_interface.INSERT_MASTER_ROWS:
            print("Inserting master rows...")
            try:
                cls.insert_master_rows()
            except psycopg2.errors.Error as e:
                print("Error inserting master rows")
                raise(e)
            print("Done")

        else:
            print(f"Unknown database_interface subcommand mode {args.subcommand[1]}")

    @classmethod
    def get_placeholder_entity_id(cls, table_name: str) -> int:
        if table_name not in db_settings.DB_PLACEHOLDER_ID_MAPPINGS.keys():
            raise MAPHSAParseInsertionException(f"Missing placeholder entity query for table {table_name}")

        if table_name not in cls._placeholder_entity_id_mappings.keys():
            curs = cls.get_connection_cursor()
            script_path = f"{db_settings.DB_SCRIPT_PATH}/{db_settings.DB_PLACEHOLDER_ID_MAPPINGS[table_name]}"
            curs.execute(open(script_path, 'r').read())
            cls._placeholder_entity_id_mappings[table_name] = curs.fetchone()[0]
            curs.close()

        return cls._placeholder_entity_id_mappings[table_name]
