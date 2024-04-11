import argparse

import arches_interface
import database_interface


def validate_arguments(args: argparse.Namespace):
    try:
        assert len(args.subcommand > 1)
    except AssertionError:
        raise IOError(f"Missing arches interface subcommand")
    try:
        assert args.subcommand[1] in arches_interface.arches_interface_subcommands
    except AssertionError:
        raise IOError(f"{args.subcommand[1]} is not a valid arches interface subcommand")


def process_subcommand(args: argparse.Namespace):

    subcommand = args.subcommand[1]

    if subcommand == arches_interface.LOAD_CONCEPTS_SUBCOMMAND:
        concept_data_batch: list = []
        for input_item in args.input:
            concept_data_batch.append(arches_interface.thesaurus_parser.extract_thesaurus(input_item))

        for concept_data in concept_data_batch:
            database_interface.DatabaseInterface.insert_concepts(concept_data,
                                                                 append=args.append, confirm=args.yes)

    elif subcommand == arches_interface.PRINT_CONCEPTS_SUBCOMMAND:
        concept_id_mappings = database_interface.DatabaseInterface.get_concept_id_mappings()
        concept_count = 0
        for thesaurus_index, thesaurus_name in enumerate(list(concept_id_mappings.keys())):
            print(f"{thesaurus_index}-{thesaurus_name}")
            for index, concept in enumerate(list(concept_id_mappings[thesaurus_name].keys())):
                print(f"\t{index}-{concept}")
            concept_count = concept_count + len(concept_id_mappings[thesaurus_name].keys())

        print(f"{len(concept_id_mappings.keys())} dictionaries summing {concept_count} concepts overall")
        exit(0)

