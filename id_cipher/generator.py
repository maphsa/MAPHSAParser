import uuid


def generate_entity_uuid5(source_data, source_meta: dict) -> uuid:

    namespace = source_meta['namespace']
    source_string = source_data[source_meta['id_field']]
    return uuid.uuid5(namespace, source_string)