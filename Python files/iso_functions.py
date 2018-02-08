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
    Removes points which are erroneously added to isochrones (by std deviation)

    :param points: Isochrone points in nested lists which are to be corrected
    :param std_devs: Threshold number of standard deviations away from the mean after which to toss points
    :return: Returns fixed points with outliers removed
    """
    corrected = []
    for iso_num in range(0, len(points)):
        mean = [st.mean(x) for x in zip(*points[iso_num])]
        sd = [st.stdev(x) for x in zip(*points[iso_num])]
        fixed_isos = [x for x in points[iso_num] if
                      (abs(mean[0] - x[0]) / sd[0] < std_devs
                       and abs(mean[1] - x[1]) / sd[1] < std_devs)]
        corrected.append(fixed_isos)
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


def shp_to_isochrones(shp_filename, shp_dir, duration):
    """
    Returns a dataframe of origin coordinates and their corresponding isochrone polygons for different durations

    :param shp_filename: Name of the shapefile to use for use with centroids
    :param shp_dir: Name of the shapefile directory
    :param duration: List of durations to create isochrones from
    :return: Dataframe of origin coords and their respective isochrones
    """
    df = pd.DataFrame()
    df['coords'] = get_centroids(shp_filename, shp_dir)
    df = df[130:132]  # just for testing
    if type(duration) is int or (type(duration) is list and len(duration) == 1):
        df['isochrones'] = iterate_isochrones(df['coords'], duration)
    else:
        for length in duration:
            iso = pd.Series(iterate_isochrones(df['coords'], length))
            df[length] = iso.values
    return df


test = shp_to_isochrones('ti_2015_us_puma.shp', 'shapefiles', duration=[15, 30])
print(test)


"""
To-do:
- Create function to change polygons into useable shapefiles with correct CRS
- Create function to limit the API queries and save outputs to CSV
- Correct isocronut function to return NaN in case of error

- Fix docstrings of puma_functions
"""
