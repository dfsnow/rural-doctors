from shapely import geometry, wkt
import isocronut as isocronut
import pandas as pd
import geopandas as gpd
import statistics as st
import fiona


def get_centroids(filename):
    """
    Get the centroids of the polygons in a specified dataframe

    :param filename: Shapefile to extract centroids from
    :return: Returns list of lat, lng coordinates
    """
    gdf = gpd.read_file(filename)
    x = gdf['geometry'].centroid.x
    y = gdf['geometry'].centroid.y
    coords = [list(i) for i in zip(y, x)]
    print(coords)
    return coords


def check_isochrones(points, std_devs=2):
    """
    Remove points which are erroneously added to isochrones (by std deviation)

    :param points: Isochrone points in nested lists which are to be corrected
    :param std_devs: Toss points this many std devs from the mean
    :return: Fixed points with outliers removed
    """
    corrected = []
    for iso_num in range(0, len(points)):
        mean = [st.mean(x) for x in zip(*points[iso_num])]
        sd = [st.stdev(x) for x in zip(*points[iso_num])]
        fixed_isos = [x for x in points[iso_num] if abs(mean[0] - x[0]) / sd[0]
                      < std_devs and abs(mean[1] - x[1]) / sd[1] < std_devs]
        corrected.append(fixed_isos)
    return corrected


def iterate_isochrones(coords, durations, swap_xy):
    """
    Iterate over a list of coordinates and returns isochrones for each duration

    :param coords: Coordinates to iterate over
    :param durations: Single or list of durations to calculate isochrones with
    :param swap_xy: Swap final lat and long values
    :return: Isochrones as polygons
    """
    iso_points = [isocronut.get_isochrone(x, durations, tolerance=2)
                  for x in coords]
    iso_points = check_isochrones(iso_points)
    if swap_xy:
        iso_polys = [geometry.Polygon([[p[1], p[0]] for p in x])
                     for x in iso_points]
    else:
        iso_polys = [geometry.Polygon([[p[0], p[1]] for p in x])
                     for x in iso_points]
    return iso_polys


def shp_to_isochrones(filename, duration, swap_xy=True):
    """
    Get a dataframe of origin coordinates and their corresponding
    isochrone polygons for different durations

    :param shp_filename: Name of the shapefile to use for use with centroids
    :param duration: List of durations to create isochrones from
    :param swap_xy: Swap output lat and long values
    :return: Dataframe of origin coords and their respective isochrones
    """
    df = pd.DataFrame()
    df['coords'] = get_centroids(filename)
    df = df[100:102]  # just for testing
    if type(duration) is int or (type(duration) is list and len(duration) == 1):
        df['duration'] = duration
        df['geometry'] = iterate_isochrones(df['coords'], duration, swap_xy)
        print(df)
        return df
    else:
        for length in duration:
            iso = pd.Series(iterate_isochrones(df['coords'], length, swap_xy))
            print(iso)
            df[length] = iso.values
    if swap_xy:
        df['coords'] = [[str(p) for p in x] for x in df['coords']]
        df['coords'] = [str([[p[1], p[0]] for p in x]) for x in df['coords']]
    cols = [col for col in df.columns if isinstance(col, int)]
    df = pd.melt(df, id_vars='coords', value_vars=cols,
                 var_name='duration', value_name='geometry')
    return df


def isochrones_to_shp(df, filename, crs, format='ESRI Shapefile'):
    """
    Convert a dataframe of isochrones to a shapefile or GeoJSON

    :param df: Input dataframe
    :param filename: Filename to save as
    :param crs: CRS to use when creating the output
    :param format: Format to use for output, geojson or esri
    :return: Shapefile or GeoJSON with attached duration and origin point data
    """
    df['geometry'] = df['geometry'].astype(str).map(wkt.loads)
    crs = {'init': 'epsg:' + str(crs)}
    df = gpd.GeoDataFrame(df, crs=crs, geometry=df['geometry'])

    iso_schema = {
        'geometry': 'Polygon',
        'properties': {'id': 'int',
                       'coords': 'str',
                       'duration': 'int'}
    }

    with fiona.open(filename, 'w', format, iso_schema) as c:
        for index, geo in df.iterrows():
            c.write({
                'geometry': geometry.mapping(geo['geometry']),
                'properties': {'id': index,
                               'coords': str(geo['coords']),
                               'duration': int(geo['duration'])}
            })
