import h3
import geojson
import json
import os

# --- Configuration ---
# Set the input and output file paths
input_geojson_file = 'centroids.merged.geojson'
output_json_file = 'h3_aggregated.json'

# Set the desired H3 resolution.
# Resolution 5 is approximately a 10km hexagon radius.
H3_RESOLUTION = 5

# --- Data Aggregation ---
# Dictionary to store the aggregated data
h3_aggregations = {}

# Check if the input file exists
if not os.path.exists(input_geojson_file):
    print(f"Error: The file '{input_geojson_file}' was not found.")
    exit()

# Read the GeoJSON file
with open(input_geojson_file, 'r') as f:
    geojson_data = geojson.load(f)

# Process each feature in the GeoJSON
for feature in geojson_data['features']:
    # Get coordinates and properties from the feature
    print(feature['geometry']['coordinates'])
    longitude, latitude = feature['geometry']['coordinates']
    properties = feature.get('properties', {})
    grantee = properties.get('grantee')

    # Convert the coordinates to an H3 index
    h3_index = h3.latlng_to_cell(latitude, longitude, H3_RESOLUTION)

    # Initialize the aggregation for this h3 index if it doesn't exist
    if h3_index not in h3_aggregations:
        h3_aggregations[h3_index] = {
            'h3Index': h3_index,
            'totalCount': 0,
            'granteeCounts': {}
        }

    # Increment the total count for the hexagon
    h3_aggregations[h3_index]['totalCount'] += 1

    # Increment the grantee-specific count
    if grantee:
        grantee_counts = h3_aggregations[h3_index]['granteeCounts']
        grantee_counts[grantee] = grantee_counts.get(grantee, 0) + 1

# Convert the dictionary values to a list of objects
aggregated_data_list = list(h3_aggregations.values())

# --- Output to JSON file ---
with open(output_json_file, 'w') as f:
    json.dump(aggregated_data_list, f, indent=2)

print(f"Aggregation complete! Aggregated data saved to '{output_json_file}'.")
print(f"Total hexagons generated: {len(aggregated_data_list)}")