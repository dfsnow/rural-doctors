import config as config
import statsmodels.formula.api as smf
import puma_functions as pf
import pandas as pd
import os
import cenpy as cp

# puma_pop = pf.get_puma_pop(year=2015, acs_filename='2011-2016_acs.csv', acs_dir='tempdir')
# puma_pop.to_csv('2011-2015_puma_pop.csv')

# Reading the CSV created by the lines above, dropping 2011 and 2016, summing 2012-2015
api_conn = cp.base.Connection('ACSSF5Y2015')

puma_gen_pop = api_conn.query(['B01001_001E'], geo_unit='public use microdata area:*')
puma_gen_pop.rename(columns={'B01001_001E': 'POP',
                             'state': 'STATEFIP',
                             'public use microdata area': 'PUMA'
                             }, inplace=True)

puma_gen_pop = puma_gen_pop[puma_gen_pop['STATEFIP'] != 72]
puma_gen_pop = pf.concat_cols(puma_gen_pop, 'STATEFIP', 'PUMA')


df = pd.read_csv(os.path.join('tempdir', 'phys_acs.csv'))
puma_med_pop = df[df['YEAR'] > 2011].groupby(["STATEFIP", "PUMA"]).sum()["PERWT"].reset_index()
puma_med_pop['STATEFIP'] = puma_med_pop['STATEFIP'].astype(int)
puma_med_pop['PUMA'] = puma_med_pop['PUMA'].astype(int)
puma_med_pop = pf.concat_cols(puma_med_pop, 'STATEFIP', 'PUMA')

puma_pop = pd.merge(
    puma_gen_pop,
    puma_med_pop,
    how='left',
    on=['PUMA_GEOID']).fillna(0)

puma_pop['PHYS'] = puma_pop['PERWT'] / 5
puma_pop['PHYS_FRAC'] = puma_pop['PHYS'] / puma_pop['POP']
puma_pop['PHYS_PER_100K'] = puma_pop['PHYS_FRAC'] * 1e5

puma_pop.to_csv('test2.csv')

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
df['STATEFIP_y'] = df['STATEFIP_y'].astype(int)
df['STATEFIP_x'] = df['STATEFIP_x'].astype(int)
df = df[(df['STATEFIP_x'] != 72) & (df['STATEFIP_y'] != 72)]
df = df.fillna(0)

# Creating cuts and regressions for CBSA pop
df['UR'] = pd.cut(
    df['CBSA_POP'],
    bins=config.reg_bins_d,
    labels=config.reg_labels_d,
    include_lowest=True)

df['PHYS_PER_100K'] = df['PHYS_FRAC'] * 1e5

# puma = pd.read_csv('puma.csv')
# puma['UR'] = pd.Categorical(puma['UR'], ordered=True,
#                             categories=['Rural', '1M', '2.5M', '6M', 'BIG'])


reg = smf.wls(formula='PHYS_PER_100K ~ UR', data=df, weights=df['POP']).fit().summary()
print(reg)
# # Writing everything to a TeX doc
# # begintex = """
# # \\documentclass{report}
# # \\usepackage{booktabs}
# # \\begin{document}
# # """
# # endtex = """
# # \end{document}"""
# #
# # f = open('reg.tex', 'w')
# # f.write(begintex)
# # f.write(reg)
# # f.write(endtex)
# # f.close()

