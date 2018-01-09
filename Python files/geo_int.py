import os
import geopandas as gpd
import numpy as np
from shapely.geometry import LineString
import pandas as pd
import seaborn as sns

batch_size = 10
year_needed = 2017

shapefiles_dir = os.path.expanduser(
    "~/Harris Drive/Research/Projects/Rural Doctors/Shapefiles/")

puma = gpd.read_file(os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_pumas.shp'))
cbsa = gpd.read_file(os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_cbsa.shp'))
# urban = gpd.read_file(os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_uac10.shp'))

row_cnt_cbsa = len(cbsa)
iterations_cbsa = int(np.ceil(row_cnt / b))

row_cnt_puma = len(puma)
iterations_puma = int(np.ceil(row_cnt / b))

start_idx = 0
end_idx = start_idx + b

final = gpd.GeoDataFrame()


for orig in cbsa.iterrows():
    for ref in puma.iterrows():
        if ref['geometry'].intersects(orig['geometry']):
         MSA_NAME = orig['NAME']
         data.append({'geometry':ref['geometry'].intersection(orig['geometry']),'MSA_NAME':MSA_NAME})

cbsa.to_file("test.shp")
