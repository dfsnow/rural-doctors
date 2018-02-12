import iso_functions as iso
import os

df = iso.shp_to_isochrones(os.path.join('shapefiles', 'ti_2015_us_puma.shp'), duration=[30, 60])
iso.isochrones_to_shp(df, 'x.shp', crs=4269)

