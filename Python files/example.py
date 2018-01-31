import config as config
import puma_functions as pf
import pandas as pd
import os

# puma_pop = pf.get_puma_pop('2011-2016_acs.csv', acs_dir='tempdir')
# puma_pop.to_csv('2011-2016_puma_pop.csv')

# Reading the CSV created by the lines above, dropping all years except 2015
puma_pop = pd.read_csv(os.path.join('tempdir', '2011-2016_puma_pop.csv'))
puma_pop = puma_pop[puma_pop['YEAR'] == 2015]

# Joining PUMA and CBSA spatial files in the specified folder, by intersect
cbsa_pop = pf.sjoin_puma(
    year=2015,
    type='cbsa',
    join='intersect',
    shapefile_dir='shapefiles',
    puma_shapefile='ti_2015_us_puma.shp',
    int_shapefile='ti_2015_us_cbsa.shp',
    drop_geometry=True
)

df = pd.merge(puma_pop, cbsa_pop, how='left', on='PUMA_GEOID')
df['STATE'] = int(str(df['PUMA_GEOID'])[:2])

pf.reg_puma_pop(
    df,
    dep_var='NURSE_FRAC',
    pop_var='POP',
    cut_pop='CBSA_POP',
    cut_bins=[0] + list(config.reg_bins_a.keys()),
    cut_labels=list(config.reg_bins_a.values()),
    ctrl_vars=['STATE']
)
