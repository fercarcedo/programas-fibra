from geopandas import GeoDataFrame, read_file

def calculate_centroids(gdf_polygons: GeoDataFrame) -> GeoDataFrame:
    gdf_projected = gdf_polygons.to_crs(epsg=25830)

    gdf_centroids = gdf_projected.copy()
    gdf_centroids.geometry = gdf_projected.geometry.centroid

    columns_to_keep = [
        'program_name', 
        'grantee', 
        'autonomous_community', 
        'province', 
        'municipality', 
        'project',
        'geometry',
    ]
    gdf_centroids_reprojected = gdf_centroids.to_crs(epsg=4326)
    result_columns = [col for col in columns_to_keep if col in gdf_centroids_reprojected.columns]
    return gdf_centroids_reprojected[result_columns]

def write_centroids(file: str, output_file: str):
    gdf_polygons = read_file(file)
    gdf_centroids = calculate_centroids(gdf_polygons)
    gdf_centroids.to_file(output_file, driver='GeoJSON')