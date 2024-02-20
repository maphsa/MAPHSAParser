import argparse

from database_interface import DatabaseInterface
from source_parser import ExistingSources, source_meta, post_process_commands
from source_parser.sicg import sicg_parser
from source_parser.icanh import icanh_parser


def validate_arguments(args: argparse.Namespace):
    try:
        assert len(args.subcommand) > 1
    except AssertionError:
        raise IOError(f"Missing arches interface subcommand")
    try:
        assert ExistingSources.has_value(args.subcommand[1])
    except AssertionError:
        raise IOError(f"{args.subcommand[1]} is not a valid source parser subcommand")

    if args.fake:
        print("FAKING, SKIPPING INSERTION OF DATA")
        input("Press any key to continue and accept...")


def post_process():
    for ppc in post_process_commands:
        if ".sql" in ppc:
            DatabaseInterface.run_post_process_command(ppc)
        else:
            raise IOError(f"Unknown post process command type {ppc}")


def process_subcommand(args: argparse.Namespace):

    validate_arguments(args)
    parser = eval(source_meta[args.subcommand[1]]['parser'])
    parser.process_input(args.input, source_meta[args.subcommand[1]], args.supp, not args.fake)
    post_process()
