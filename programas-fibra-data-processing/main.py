import argparse
from lib.process_peba import execute as execute_peba
from lib.process_unico import execute as execute_unico

def read_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Process data from PEBA-NGA or UNICO fiber programs to generate a GeoJSON file"
    )
    subparsers = parser.add_subparsers(
        dest="program_type",
        required=True,
        help="Fiber program type: peba/unico"
    )

    peba_parser = subparsers.add_parser('peba', help="Process PEBA Excel file")
    add_peba_parser_options(peba_parser)

    unico_parser = subparsers.add_parser("unico", help="Process UNICO GeoJSON file")
    add_unico_parser_options(unico_parser)

    return parser.parse_args()

def add_peba_parser_options(peba_parser: argparse.ArgumentParser):
    peba_parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Path of the Excel file",
        required=True,
    )
    peba_parser.add_argument(
        "-e",
        "--entities",
        type=str,
        help="Path of the entities csv file from the CNIG",
        required=True,
    )
    peba_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Name of the result file",
        default="out.geojson",
        required=False,
    )

def add_unico_parser_options(unico_parser: argparse.ArgumentParser):
    unico_parser.add_argument(
        "-e",
        "--eligible-areas",
        type=str,
        help="Path of the GeoJSON file with the eligible areas",
        required=True,
    )
    unico_parser.add_argument(
        "-a",
        "--awarded-areas",
        type=str,
        help="Path of the Excel file with the awarded areas",
        required=True,
    )
    unico_parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        help="Name of the result file",
        default="out.geojson",
        required=False,
    )

def main():
    args = read_args()
    if args.program_type == "peba":
        execute_peba(args.file, args.entities, args.output)
    else:
        execute_unico(args.awarded_areas, args.eligible_areas, args.output_file)

if __name__ == '__main__':
    main()