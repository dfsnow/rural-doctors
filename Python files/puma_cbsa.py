import config as config
import os
import geopandas as gpd
import pandas as pd
import cenpy as cp

######## Importing ########
# Importing CBSA population estimates from the census website
cen_api = cp.base.Connection(config.census_database)
cbsa_pop = cen_api.query(
    config.census_col_needed, geo_unit='metropolitan statistical area/micropolitan statistical area:*')
cbsa_pop.rename(columns={'B01001_001E': 'POP', cbsa_pop.columns[-1]: 'GEOID'}, inplace=True)

# Read PUMA and CBSA shapefiles from the shapefile dir for the specified year
puma = gpd.read_file(os.path.join(config.spatial_dir, 'ti_' + str(config.spatial_year) + '_us_puma.shp'))
cbsa = gpd.read_file(os.path.join(config.spatial_dir, 'ti_' + str(config.spatial_year) + '_us_cbsa.shp'))

######## Processing/Cleaning ########
# Erode a very small amount of each polygon so that shared borders aren't intersecting
cbsa['geometry'] = cbsa.geometry.buffer(config.spatial_buffer)

# Perform spatial join on PUMAs and CBSAs where intersecting
int_puma_cbsa = gpd.sjoin(puma, cbsa, how='left', op='intersects')
# int_puma_cbsa = gpd.sjoin(puma.set_geometry(puma.centroid), cbsa, how='left', op='within')

# Merge CBSA population data from CSV with spatial data files
merged_puma_cbsa = pd.DataFrame(cbsa_pop.merge(int_puma_cbsa, on='GEOID'))

# Filter the merged data, keeping only intersecting CBSAs with the highest population
merged_puma_cbsa = merged_puma_cbsa.sort_values('POP', ascending=False)
merged_puma_cbsa = merged_puma_cbsa[
    (~merged_puma_cbsa['GEOID10'].duplicated()) | (merged_puma_cbsa['GEOID'].isnull())]

# Remove all columns of dataframe except those needed, rename remaining columns
final_puma = merged_puma_cbsa[config.cbsa_col_needed]
final_puma.columns = config.cbsa_col_names 

######## Exporting ########
# Export data to CSV in the working dir
final_puma.to_csv(
    os.path.join(config.data_dir, str(config.spatial_year) + '_puma_cbsa_int.csv'))