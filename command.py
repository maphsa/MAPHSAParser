import argparse
from enum import Enum
import pathlib

from database_interface import DatabaseInterface
import source_parser
import arches_interface


class Subcommands(Enum):
    parse = 'parse'
    arches = 'arches'
    database_interface = 'database_interface'


cli_parser = argparse.ArgumentParser()
cli_parser.add_argument('subcommand', nargs='+', type=str, help='main subcommand')
cli_parser.add_argument('-i', '--input', nargs='*', type=pathlib.Path, help='input files')
cli_parser.add_argument('-f', '--fake', action='store_true', help='fake insertion')

args: argparse.Namespace = cli_parser.parse_args()

match args.subcommand[0]:
    case Subcommands.parse.value:
        source_parser.source_parser.process_subcommand(args)
    case Subcommands.arches.value:
        arches_interface.arches_interface.process_subcommand(args)
    case Subcommands.database_interface.value:
        DatabaseInterface.process_subcommand(args)
    case _:
        raise ValueError(f"Unknown subcommand {args.subcommand[0]}")



