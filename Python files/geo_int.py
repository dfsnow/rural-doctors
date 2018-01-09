import os
import geopandas as gpd


year_needed = 2017
batch_size = 10

shapefiles_dir = os.path.expanduser(
    "~/Harris Drive/Research/Projects/Rural Doctors/Shapefiles/")

puma = gpd.read_file(os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_pumas.shp'))
cbsa = gpd.read_file(os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_cbsa.shp'))
# urban = gpd.read_file(os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_uac10.shp'))

final = []

for index, orig in puma.iterrows():
    for index2, ref in cbsa.iterrows():
        if ref['geometry'].intersects(orig['geometry']):
            MSA_NAME = ref['NAME']
            final.append({'geometry':ref['geometry'].intersection(orig['geometry']),'TEST':MSA_NAME})
    print("Iteration: %s/%s" % (index, len(puma)))


final.to_file(shapefiles_dir, driver="ESRI Shapefile")
