DB_NAME = ''
DB_HOST = ''
DB_USERNAME = ''
DB_PASSWORD = ''

DB_AUTOCOMMIT = True
DB_ISOLATION_LEVEL = 1

DB_SCRIPT_PATH = 'database_interface/scripts'

DB_PURGE_SCRIPT = f"{DB_SCRIPT_PATH}/purgeSchema.sql"
DB_DEPLOYMENT_SCRIPT = f"{DB_SCRIPT_PATH}/buildSchema.sql"
DB_MASTER_ROW_SCRIPT = f"{DB_SCRIPT_PATH}/insertMasterRows.sql"
DB_CONCEPT_LIST_TRIGGER_SCRIPT = f"addEmptyConceptListTrigger.sql"
DB_CONCEPT_LIST_FUNCTION_SCRIPT = f"addEmptyConceptListFunction.sql"

DB_LOAD_EXTENT_SCRIPT = f"{DB_SCRIPT_PATH}/loadExtent.sh.j2"
DB_ADJUST_EXTENT_SCRIPT = f"{DB_SCRIPT_PATH}/adjustExtent.sql.j2"
DB_EXTENT_SHAPEFILE_URL = "database_interface/extent/MAPHSA_areas.shp"
DB_EXTENT_CRS = "4326"

DB_TEMPLATE_URL_PATH = 'database_interface/sql_templates'

SKIP_INSERT_CONCEPT_CONFIRMATION = False

DB_PLACEHOLDER_ID_MAPPINGS = {
    'grid': 'getPlaceholderGridID.sql'
}
