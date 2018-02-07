import isocronut as isocronut
import pandas as pd
import geopandas as gpd
from shapely import geometry
import statistics as st
import os


def get_centroids(shp_filename, shp_dir):
    """
    Gets the centroids of the polygons in a specified dataframe

    :param shp_filename: Shapefile to extract centroids from
    :param shp_dir: Shapefile directory to look for shapefiles in
    :return: Returns zipped list of lat, lng coordinates
    """
    gdf = gpd.read_file(os.path.join(shp_dir, shp_filename))
    y = gdf['geometry'].centroid.y
    x = gdf['geometry'].centroid.x
    coords = [list(i) for i in zip(y, x)]
    return coords


def check_isochrones(points, std_devs=3):
    """
    Removes points which are erroneously added to isochrones.
    Points which are x std devs away from the mean are removed.

    :param points: Isochrone points in nested lists which are to be corrected
    :param std_devs: Threshold number of standard deviations away from the mean after which to toss points
    :return: Returns fixed points with outliers removed
    """
    mean = [st.mean(x) for x in zip(*points)]
    sd = [st.stdev(x) for x in zip(*points)]
    corrected = [x for x in points if x[0] > mean[0] + std_devs*sd[0] | x[1] > mean[1] + std_devs*sd[1]]
    return corrected


def iterate_isochrones(coords, durations):
    """
    Iterates over a list of coordinates and returns isochrones for each duration

    :param coords: Coordinates to iterate over
    :param durations: Single or list of durations to calculate isochrones with
    :return: Returns isochrones as polygons
    """
    iso_points = [isocronut.get_isochrone(x, durations) for x in coords]
    iso_points = check_isochrones(iso_points)
    iso_polys = [geometry.Polygon([[p[0], p[1]] for p in x]) for x in iso_points]
    return iso_polys


def shp_to_isochone(shp_filename, shp_dir, durations=30):
    """
    Returns a dataframe of origin coordinates and their corresponding isochrone polygons for different durations

    :param shp_filename: Name of the shapefile to use for use with centroids
    :param shp_dir: Name of the shapefile directory
    :param durations: List of durations to create isochrones from
    :return: Dataframe of origin coords and their respective isochrones
    """
    df = pd.DataFrame()
    df['coords'] = get_centroids(shp_filename, shp_dir)
    df = df[130:133]  # just for testing
    if len(durations) == 0:
        df['isochrones'] = iterate_isochrones(df['coords'], durations)
    else:
        for length in durations:
            iso = iterate_isochrones(df['coords'], length)
            df.append(iso)
    return df


test = shp_to_isochone('ti_2015_us_puma.shp', 'shapefiles', duration=30)
print(test)


"""
To-do:
- Create function to perform error checking on get_isochrone results (drop points very far from mean?)
- Create function wrapper to get_isochrone to ESRI shapefile with 2163 CRS
- Create map/lambda function to iterate over points

"""
