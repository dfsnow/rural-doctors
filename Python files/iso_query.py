import iso_functions as iso
import pandas as pd
import os

df = iso.shp_to_isochrones(os.path.join('shapefiles', 'ti_2015_us_puma.shp'), duration=60)
df.to_csv(os.path.join('data', 'isochrones.csv'))

iso.isochrones_to_shp(df, os.path.join('shapefiles', 'isochrones.shp'), crs=4269)

# TODO Fix weird string matching error in isochrones to shp
# TODO Add method to split the big function into batches

# number_of_chunks = 10
# [df_i.to_csv('/data/bs_{id}.csv'.format(id=id)) for id, df_i in  enumerate(np.array_split(df, number_of_chunks))]
