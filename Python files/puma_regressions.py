import config as config
import statsmodels.formula.api as smf
import puma_functions as pf
import pandas as pd
import os
import cenpy as cp

puma_pop = pf.get_puma_pop('2011-2016_acs.csv', acs_dir='tempdir')
puma_pop.to_csv('2011-2016_puma_pop.csv')


# # Reading the CSV created by the lines above, dropping 2011 and 2016, summing 2012-2015
# puma_pop = pd.read_csv(os.path.join('tempdir', '2011-2016_puma_pop.csv'))
# puma_pop = puma_pop[puma_pop['YEAR'].isin(range(2012, 2016))]
# puma_pop = puma_pop.groupby('PUMA_GEOID').sum().reset_index()

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

# Merging CBSA pop data and PUMA pop data
df = pd.merge(puma_pop, cbsa_pop, how='left', on='PUMA_GEOID')
df = pd.merge(puma_pop, geo_pop, how='left', on='PUMA_GEOID')
df = df.fillna(0)

# Creating cuts and regressions for CBSA pop
df['UR'] = pd.cut(
    df['CBSA_POP'],
    bins=config.reg_bins_c,
    labels=config.reg_labels_c,
    include_lowest=True)

df['PHYS_PER_100K'] = df['PHYS_FRAC'] * 1e5

reg = smf.wls(formula='PHYS_PER_100K ~ UR', data=df, weights=df['POP2']).fit().summary().as_latex()

# Writing everything to a TeX doc
begintex = """
\\documentclass{report}
\\usepackage{booktabs}
\\begin{document}
"""
endtex = """
\end{document}"""

f = open('reg.tex', 'w')
f.write(begintex)
f.write(reg)
f.write(endtex)
f.close()

"""
- Remove people under 25, those who work less than 30 hours per week (UHOURSWORK)
- Add age, OCC2010
- Use pop from census 2015
- 2351 PUMAs
- 2303 PUMAs with PYHS
- Aggregate years together, 1 PUMA 1 obs
- Change cuts to 0, 250K, 1M, 2.5M, 6M, BIG
- Add 2016 data

- Learn command line functions
"""