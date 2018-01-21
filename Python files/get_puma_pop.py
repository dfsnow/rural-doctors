import config as config
import os
import pandas as pd
import geopandas as gpd
import requests
import seaborn as sns
import statsmodels.formula.api as smf
import cenpy as cp

# File in the temp dir with aggregated PUMA counts of medical occupations
file_check = os.path.join(config.temp_dir, config.census_filename + '_puma_med_pop.csv')
merge_format = '{:06d}".format'

# If statement which checks for existence of aggregate file and creates one if does not exist
if os.path.isfile(file_check):
    puma_med_pop = pd.read_csv(file_check)
else:
    acs = pd.read_csv(os.path.join(
        config.temp_dir, config.census_filename + '.csv'),
        low_memory=False)
    # Dropping non-med people and summarizing OCC by PERWT for each state and puma, then rename columns
    puma_med_pop = acs[acs['OCC2010'].isin(config.census_occ_codes.keys())]
    puma_med_pop = puma_med_pop.groupby(['STATEFIP', 'PUMA', 'OCC2010']).sum()['PERWT'].reset_index()

    # Converting the resulting integers to strings which can be properly concatenated into PUMA_GEOID
    puma_med_pop[['STATEFIP', 'PUMA']] = puma_med_pop[['STATEFIP', 'PUMA']].astype(str)
    puma_med_pop['STATEFIP'] = puma_med_pop['STATEFIP'].str.zfill(2)
    puma_med_pop['PUMA'] = puma_med_pop['PUMA'].str.zfill(5)
    puma_med_pop['PUMA_GEOID'] = puma_med_pop['STATEFIP'] + puma_med_pop['PUMA']

    # Spreading the med pop values into their own columns, then renaming
    puma_med_pop = puma_med_pop.pivot(index='PUMA_GEOID', columns='OCC2010', values='PERWT')
    puma_med_pop.columns.name = None
    puma_med_pop.rename(columns=config.census_occ_codes, inplace=True)

    # Save the resulting file as a CSV to be reused later
    puma_med_pop.to_csv(os.path.join(config.temp_dir, config.census_filename + '_puma_med_pop.csv'))

# Grabbing overall PUMA populations from the census API
cen_api = cp.base.Connection(config.census_database)
puma_pop = cen_api.query(
    config.census_var_needed, geo_unit='public use microdata area:*')
puma_pop.rename(columns={'B01001_001E': 'POP', puma_pop.columns[-1]: 'GEOID'}, inplace=True)



