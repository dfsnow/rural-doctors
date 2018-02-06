import config as config
import statsmodels.formula.api as smf
import puma_functions as pf
import pandas as pd
import os

# puma_pop = pf.get_puma_pop('2011-2016_acs.csv', acs_dir='tempdir')
# puma_pop.to_csv('2011-2016_puma_pop.csv')

# Reading the CSV created by the lines above, dropping 2016
puma_pop = pd.read_csv(os.path.join('tempdir', '2011-2016_puma_pop.csv'))
puma_pop = puma_pop[puma_pop['YEAR'] != 2016]

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
df = df.fillna(0)

df['UR'] = pd.cut(df['CBSA_POP'],
    bins=config.reg_cbsa_bins_a,
    labels=config.reg_cbsa_labels_a,
    include_lowest=True)

test = smf.wls(formula='PHYS_FRAC ~ UR', data=df, weights=df['POP']).fit().summary()

print(test)



