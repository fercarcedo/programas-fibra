import h3
import geojson
import json
import os
import argparse

# --- Configuration ---
parser = argparse.ArgumentParser(
    description="Generate H3 hexagon aggregations from GeoJSON data"
)
parser.add_argument(
    "--projects-status",
    type=str,
    help="Path to JSON file with project status and deadline data",
    required=True,
)
args = parser.parse_args()

# Set the input and output file paths
input_geojson_file = "centroids.merged.geojson"
output_json_file = "h3_aggregated.json"
hexagons_projects_file = "hexagons_projects.json"

# Set the desired H3 resolution.
# Resolution 5 is approximately a 10km hexagon radius.
H3_RESOLUTION = 5


def get_normalized_project_code(project_code):
    """Get a normalized version of project code by removing leading zeros from suffix.
    TSI-061000-2015-0114 -> TSI-061000-2015-114
    """
    if not project_code:
        return None
    parts = project_code.rsplit("-", 1)
    if len(parts) == 2:
        prefix, suffix = parts
        # Remove leading zeros from numeric suffix
        normalized_suffix = str(int(suffix))
        return prefix + "-" + normalized_suffix
    return None


# Load project status data
projects_status = {}
if args.projects_status:
    if os.path.exists(args.projects_status):
        with open(args.projects_status, "r") as f:
            projects_status = json.load(f)
        print(f"Loaded project status data from '{args.projects_status}'")
    else:
        print(f"Warning: Project status file '{args.projects_status}' not found")

# --- Data Aggregation ---
# Dictionary to store the aggregated data
h3_aggregations = {}
# Dictionary to store projects in each hexagon with counts
hexagons_projects = {}

# Check if the input file exists
if not os.path.exists(input_geojson_file):
    print(f"Error: The file '{input_geojson_file}' was not found.")
    exit()

# Read the GeoJSON file
with open(input_geojson_file, "r") as f:
    geojson_data = geojson.load(f)

# Process each feature in the GeoJSON
for feature in geojson_data["features"]:
    # Get coordinates and properties from the feature
    longitude, latitude = feature["geometry"]["coordinates"]
    properties = feature.get("properties", {})
    grantee = properties.get("grantee")
    program = properties.get("program_name")
    project = properties.get("project")

    # Convert the coordinates to an H3 index
    h3_index = h3.latlng_to_cell(latitude, longitude, H3_RESOLUTION)

    # Initialize the aggregation for this h3 index if it doesn't exist
    if h3_index not in h3_aggregations:
        h3_aggregations[h3_index] = {"h3Index": h3_index, "totalCount": 0, "counts": {}}

    # Track project in this hexagon with count
    # Normalize if original doesn't exist in projects_status
    project_to_store = project
    if project:
        if project not in projects_status:
            normalized = get_normalized_project_code(project)
            if normalized and normalized in projects_status:
                project_to_store = normalized

        if h3_index not in hexagons_projects:
            hexagons_projects[h3_index] = {}
        if project_to_store not in hexagons_projects[h3_index]:
            hexagons_projects[h3_index][project_to_store] = 0
        hexagons_projects[h3_index][project_to_store] += 1

    # Increment the nested counts by grantee and program
    if grantee:
        counts = h3_aggregations[h3_index]["counts"]
        if grantee not in counts:
            counts[grantee] = {}

        # Initialize program entry with status counts
        if program not in counts[grantee]:
            counts[grantee][program] = {"total": 0, "statuses": {}}

        counts[grantee][program]["total"] += 1

        # Track status count if project info is available
        if project_to_store and project_to_store in projects_status:
            status = projects_status[project_to_store].get("status")
            if status:
                counts[grantee][program]["statuses"][status] = (
                    counts[grantee][program]["statuses"].get(status, 0) + 1
                )

    # Increment the total count for the hexagon
    h3_aggregations[h3_index]["totalCount"] += 1

# Convert the dictionary values to a list of objects
aggregated_data_list = list(h3_aggregations.values())

# --- Output to JSON file ---
with open(output_json_file, "w") as f:
    json.dump(aggregated_data_list, f, indent=2, ensure_ascii=False)

with open(hexagons_projects_file, "w") as f:
    json.dump(hexagons_projects, f, indent=2)

print(f"Aggregation complete! Aggregated data saved to '{output_json_file}'.")
print(f"Hexagon projects mapping saved to '{hexagons_projects_file}'.")
print(f"Total hexagons generated: {len(aggregated_data_list)}")
