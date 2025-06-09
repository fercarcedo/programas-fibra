import ijson
import pandas
import argparse
import simplejson as json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def read_args():
    parser = argparse.ArgumentParser(
        description="Process GeoJSON files from the UNICO fiber programs to only include awarded areas"
    )
    parser.add_argument(
        "-e",
        "--eligible-areas",
        type=str,
        help="Path of the GeoJSON file with the eligible areas",
        required=True,
    )
    parser.add_argument(
        "-a",
        "--awarded-areas",
        type=str,
        help="Path of the Excel file with the awarded areas",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        help="Name of the result file",
        default="out.geojson",
        required=False,
    )

    return parser.parse_args()


def read_awarded_area_codes(f):
    excel_df = pandas.read_excel(f, sheet_name="Ámbito", header=None)
    return set(excel_df[5].dropna().iloc[1:])


def filter_awarded_areas(f, awarded_area_codes):
    records = ijson.items(f, "features.item")
    return (r for r in records if r["properties"]["CodigoZona"] in awarded_area_codes)


def write_awarded_areas(f, areas):
    f.write('{"type": "FeatureCollection", "features": [')

    first_feature = True
    for area in areas:
        if not first_feature:
            f.write(",")
        else:
            first_feature = False
        json.dump(area, f, use_decimal=True, ensure_ascii=False)

    f.write("]}")


def process_eligible_areas(eligible_areas_file, awarded_area_codes, output_file):
    with open(eligible_areas_file, "rb") as f:
        with open(output_file, "w", encoding='utf-8') as out:
            areas = filter_awarded_areas(f, awarded_area_codes)
            write_awarded_areas(out, areas)


def main():
    args = read_args()
    awarded_area_codes = read_awarded_area_codes(args.awarded_areas)
    process_eligible_areas(args.eligible_areas, awarded_area_codes, args.output_file)


if __name__ == "__main__":
    main()
