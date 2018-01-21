import config as config
import os
import geopandas as gpd
import pandas as pd
import cenpy as cp

######## Setup/Importing ########
# Importing UAC population estimates from the census website
cen_api = cp.base.Connection(config.census_database)
uac_pop = cen_api.query(config.census_var_needed, geo_unit='urban area:*')
uac_pop.rename(columns={'B01001_001E': 'POP', uac_pop.columns[-1]: 'UACE10'}, inplace=True)

# Read PUMA and UAC shapefiles from the shapefile dir for the specified year
puma = gpd.read_file(os.path.join(config.spatial_dir, 'ti_' + str(config.spatial_year) + '_us_puma.shp'))
uac = gpd.read_file(os.path.join(config.spatial_dir, 'ti_' + str(config.spatial_year) + '_us_uac10.shp'))

######## Processing/Cleaning ########
# Erode a very small amount of each polygon so that shared borders aren't intersecting
uac['geometry'] = uac.geometry.buffer(config.spatial_buffer)

# Perform spatial join on PUMAs and UACs where intersecting or point-in-polygon
int_puma_uac = gpd.sjoin(puma, uac, how='left', op='intersects')
# int_puma_uac = gpd.sjoin(puma.set_geometry(puma.centroid), uac, how='left', op='within')

# Merge UAC population data from CSV with spatial data files
merged_puma_uac = pd.DataFrame(uac_pop.merge(int_puma_uac, on='UACE10'))

# Filter the merged data, keeping only intersecting UACs with the highest population
merged_puma_uac = merged_puma_uac.sort_values('POP', ascending=False)
merged_puma_uac = merged_puma_uac[
    (~merged_puma_uac['GEOID10_left'].duplicated()) | (merged_puma_uac['UACE10'].isnull())]

# Remove all columns of dataframe except those needed, rename remaining columns
final_uac = merged_puma_uac[config.uac_col_needed]
final_uac.columns = config.uac_col_names

######## Exporting ########
# Export data to CSV in the working dir
final_uac.to_csv(
    os.path.join(config.temp_dir, str(config.spatial_year) + '_puma_uac_int.csv'))
