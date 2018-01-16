import config as config
import os
import geopandas as gpd
import pandas as pd

######## Importing ########
# Importing CBSA 2016 population estimates from CSV
cbsa_pop = pd.read_csv('cbsa_pop.csv')
cbsa_pop['GEOID'] = cbsa_pop['GEOID'].astype(str)

# Read PUMA and CBSA shapefiles from the shapefile dir for the specified year
puma = gpd.read_file(os.path.join(config.working_dir, 'ti_' + str(config.year_needed) + '_us_puma.shp'))
cbsa = gpd.read_file(os.path.join(config.working_dir, 'ti_' + str(config.year_needed) + '_us_cbsa.shp'))

######## Processing/Cleaning ########
# Erode a very small amount of each polygon so that shared borders aren't intersecting
cbsa['geometry'] = cbsa.geometry.buffer(config.buffer_amount)

# Perform spatial join on PUMAs and CBSAs where intersecting
int_puma_cbsa = gpd.sjoin(puma, cbsa, how='left', op='intersects')

# Merge CBSA population data from CSV with spatial data files
merged_puma_cbsa = pd.DataFrame(cbsa_pop.merge(int_puma_cbsa, on='GEOID'))

# Filter the merged data, keeping only intersecting CBSAs with the highest population
merged_puma_cbsa = merged_puma_cbsa.sort_values('2016', ascending=False)
merged_puma_cbsa = merged_puma_cbsa[
    (~merged_puma_cbsa['GEOID10'].duplicated()) | (merged_puma_cbsa['GEOID'].isnull())]

# Remove all columns of dataframe except those needed, rename remaining columns
final_puma = merged_puma_cbsa[config.cbsa_col_needed]
final_puma.columns = config.cbsa_col_names 

######## Exporting ########
# Export data to CSV in the working dir
final_puma.to_csv(
    os.path.join(config.working_dir, 'ti_' + str(config.year_needed) + '_us_puma_MERGED.csv'))