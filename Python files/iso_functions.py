import isocronut as isocronut
import pandas as pd
import geopandas as gpd
from shapely import geometry
import fiona
import os


def get_centroids(shp_filename, shp_dir):
    gdf = gpd.read_file(os.path.join(shp_dir, shp_filename))
    y = gdf['geometry'].centroid.y
    x = gdf['geometry'].centroid.x
    coords = [list(i) for i in zip(y, x)]
    return coords


def iterate_isochrone(coords, duration):
    iso_points = [isocronut.get_isochrone(x, duration) for x in coords]
    iso_polys = [geometry.Polygon([[p[0], p[1]] for p in x]) for x in iso_points]
    return iso_polys


def shp_to_isochones(shp_filename, shp_dir, duration=30):
    df = pd.DataFrame()
    df['coords'] = get_centroids(shp_filename, shp_dir)
    df = df[130:133] # just for testing
    df['isochrones'] = iterate_isochrone(df['coords'], duration)
    return df


test = shp_to_isochones('ti_2015_us_puma.shp', 'shapefiles', duration=30)
print(test)


# origin = '111 W Washington, Chicago'
# duration = 30
#
# isochrone = isocronut.get_isochrone(origin, duration, number_of_angles=8)
# poly = geometry.Polygon([[p[0], p[1]] for p in isochrone])
#
# schema = {
#     'geometry': 'Polygon',
#     'properties': {'id': 'int'},
# }
#
# with fiona.open('test.shp', 'w', 'ESRI Shapefile', schema) as c:
#     c.write({
#         'geometry': geometry.mapping(poly),
#         'properties': {'id': 123},
#     })
#
#
# print(isochrone)

"""
To-do:
- Create function to perform error checking on get_isochrone results (drop points very far from mean?)
- Create function wrapper to get_isochrone to ESRI shapefile with 2163 CRS
- Create map/lambda function to iterate over points

"""
