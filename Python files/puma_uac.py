import config as config
import os
import geopandas as gpd
import pandas as pd

######## Setup/Importing ########
# Importing UAC 2010 population estimates from CSV
uac_pop = pd.read_csv('uac_pop.csv')
uac_pop['UACE10'] = uac_pop['UACE10'].astype(str)

# Read PUMA and UAC shapefiles from the shapefile dir for the specified year
puma = gpd.read_file(os.path.join(config.working_dir, 'ti_' + str(config.year_needed) + '_us_puma.shp'))
uac = gpd.read_file(os.path.join(config.working_dir, 'ti_' + str(config.year_needed) + '_us_uac10.shp'))

######## Processing/Cleaning ########
# Erode a very small amount of each polygon so that shared borders aren't intersecting
uac['geometry'] = uac.geometry.buffer(config.buffer_amount)

# Perform spatial join on PUMAs and UACs where intersecting
int_puma_uac = gpd.sjoin(puma, uac, how='left', op='intersects')

# Merge UAC population data from CSV with spatial data files
merged_puma_uac = pd.DataFrame(uac_pop.merge(int_puma_uac, on='UACE10'))

# Filter the merged data, keeping only intersecting UACs with the highest population
merged_puma_uac = merged_puma_uac.sort_values('POP', ascending=False)
merged_puma_uac = merged_puma_uac[(~merged_puma_uac['GEOID10_left'].duplicated()) | (merged_puma_uac['UACE10'].isnull())]

# Remove all columns of dataframe except those needed, rename remaining columns
final_uac = merged_puma_uac[config.uac_col_needed]
final_uac.columns = config.uac_col_names

######## Exporting ########
# Export data to CSV in the working dir
final_uac.to_csv(
    os.path.join(config.working_dir, 'ti_' + str(config.year_needed) + '_us_uac_MERGED.csv'))
