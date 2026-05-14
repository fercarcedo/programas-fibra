from geopandas import GeoDataFrame
from shapely.geometry import Polygon, Point
from lib.centroid_calculator import calculate_centroids
from pytest import approx


def test_calculate_centroids():
    polygon = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])
    expected_centroid = Point(5, 2.5)

    gdf_polygon = GeoDataFrame(
        {"name": ["square"], "geometry": [polygon]}, crs="EPSG:4326"
    )

    gdf_result = calculate_centroids(gdf_polygon)

    assert gdf_result.crs == "EPSG:4326"

    centroid = gdf_result.iloc[0].geometry

    assert centroid.x == approx(expected_centroid.x, abs=0.1)
    assert centroid.y == approx(expected_centroid.y, abs=0.1)


def test_calculate_centroids_removes_extra_columns():
    polygon = Polygon([(0, 0), (10, 0), (10, 5), (0, 5)])

    gdf_polygon = GeoDataFrame(
        {
            "name": ["square"],
            "geometry": [polygon],
        },
        crs="EPSG:4326",
        columns=[
            "program_name",
            "grantee",
            "autonomous_community",
            "province",
            "municipality",
            "project",
            "geometry",
            "other",
            "some_column",
        ],
    )

    gdf_result = calculate_centroids(gdf_polygon)

    assert set(gdf_result.columns) == {
        "program_name",
        "grantee",
        "autonomous_community",
        "province",
        "municipality",
        "project",
        "geometry",
    }
