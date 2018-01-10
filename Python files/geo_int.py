import os
import geopandas as gpd
import pandas as pd

######## Setup ########
# Set year of the files you need to work with
year_needed = 2017
shapefiles_dir = "Shapefiles"

# Importing CBSA 2016 population estimates from CSV
cbsa_pop = pd.read_csv('cbsa_pop.csv')
cbsa_pop['GEOID'] = cbsa_pop['GEOID'].astype(str)

# Read PUMA, CBSA, and Urban Area shapefiles from the shapefile dir for the specified year
puma = gpd.read_file(os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_pumas.shp'))
cbsa = gpd.read_file(os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_cbsa.shp'))
urban = gpd.read_file(os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_uac10.shp'))


######## Spatial Processing ########
# Perform spatial join on PUMAs and CBSAs where intersecting
int_puma_cbsa = gpd.sjoin(puma, cbsa, how='inner', op='intersects')
int_urban_cbsa = gpd.sjoin(urban, cbsa, how='inner', op='intersects')

# Merge CBSA population data with spatial data files
merged_puma_cbsa = pd.DataFrame(cbsa_pop.merge(int_puma_cbsa, on='GEOID'))
merged_urban_cbsa = pd.DataFrame(cbsa_pop.merge(int_urban_cbsa, on='GEOID'))

# Filter the merged data, keeping only intersecting CBSAs with the highest population
final_puma = gpd.GeoDataFrame(
    merged_puma_cbsa[
        merged_puma_cbsa['2016'] ==
        merged_puma_cbsa.groupby('GEOID10')['2016'].transform(max)])

final_urban = gpd.GeoDataFrame(
    merged_urban_cbsa[
        merged_urban_cbsa['2016'] ==
        merged_urban_cbsa.groupby(['GEOID10'])['2016'].transform(max)])


######## Exporting ########
# Save final PUMA shapefiles
final_puma.to_file(
    os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_pumas_MERGED.shp'),
    driver="ESRI Shapefile")
final_urban.to_file(
    os.path.join(shapefiles_dir, 'ti_' + str(year_needed) + '_us_urban_MERGED.shp'),
    driver="ESRI Shapefile")

