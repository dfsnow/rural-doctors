import isocronut as isocronut
from shapely import geometry
import fiona

# test = gpd.read_file(os.path.join('shapefiles', 'ti_2015_us_puma.shp'))

origin = '111 W Washington, Chicago'
duration = 30

# isochrone = isocronut.generate_isochrone_map(origin, duration, number_of_angles=20)
isochrone = isocronut.get_isochrone(origin, duration, number_of_angles=10)
poly = geometry.Polygon([[p[0], p[1]] for p in isochrone])

schema = {
    'geometry': 'Polygon',
    'properties': {'id': 'int'},
}

with fiona.open('test.shp', 'w', 'ESRI Shapefile', schema) as c:
    c.write({
        'geometry': geometry.mapping(poly),
        'properties': {'id': 123},
    })


print(isochrone)

"""
To-do:
- Create quick function to extract PUMA centroids
- Create function to perform error checking on get_isochrone results (drop points very far from mean?)
- Create function wrapper to get_isochrone to ESRI shapefile with 2163 CRS
- Create map/lambda function to iterate over points

- Move puma_functions docstrings to README, comment functions, refactor, cleanup

- Fill puma_functions with NA
- Add checking function for categorical in regressions
- Fix regression returning zeros/NaN

- Output regressions to PDF with latex

"""
