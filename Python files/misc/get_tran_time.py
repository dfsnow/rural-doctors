import config as config
import os
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# Importing PUMA shapefiles
puma = gpd.read_file(os.path.join(config.spatial_dir, 'ipums_puma_2010_fixed.shp'))
puma['GEOID'] = puma['GEOID'].astype(int)

# Importing ACS/IPUMS file
acs = pd.read_csv(os.path.join(
    config.temp_dir, config.census_filename + '.csv'),
    low_memory=False)

# Calculating the mean commute time by PUMA
puma_tran_time = acs.groupby(['STATEFIP', 'PUMA']).mean()['TRANTIME'].reset_index()

# Concatenating PUMA ID and STATE FIPS to make a PUMA GEOID
puma_tran_time[['STATEFIP', 'PUMA']] = puma_tran_time[['STATEFIP', 'PUMA']].astype(str)
puma_tran_time['STATEFIP'] = puma_tran_time['STATEFIP'].str.zfill(2)
puma_tran_time['PUMA'] = puma_tran_time['PUMA'].str.zfill(5)
puma_tran_time['PUMA_GEOID'] = puma_tran_time['STATEFIP'] + puma_tran_time['PUMA']
puma_tran_time['PUMA_GEOID'] = puma_tran_time['PUMA_GEOID'].astype(int)

# Spatial merge transportation time with the spatial data using PUMA_GEOID
puma_merged = puma.merge(puma_tran_time, left_on=['GEOID'], right_on=['PUMA_GEOID'], how='left')

# Save shapefile so we never have to process this data again
puma_merged.to_file(os.path.join(config.spatial_dir, str(config.spatial_year) + '_puma_tran_time.shp'))

# puma_merged = gpd.read_file(os.path.join(
#     config.spatial_dir, str(config.spatial_year) + '_puma_tran_time.shp')).to_crs(epsg=2163)

# Create PUMA choropleth from resulting data
puma_plot = puma_merged.plot(column='TRANTIME', colormap='OrRd')
fig = puma_plot.get_figure()
plt.axis('off')
fig.set_dpi(1200)
fig.savefig('commute_time.png')
