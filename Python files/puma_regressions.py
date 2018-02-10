import config as config
import statsmodels.formula.api as smf
import puma_functions as pf
import pandas as pd
import os

# puma_pop = pf.get_puma_pop(year=2015, acs_filename='2011-2016_acs.csv', acs_dir='tempdir')
# puma_pop.to_csv('2011-2015_puma_pop.csv')

# Reading the CSV created by the lines above, dropping 2011 and 2016, summing 2012-2015
puma_pop = pd.read_csv(os.path.join('tempdir', '2012-2015_puma_pop.csv'))

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
df = df.fillna(0)

# Creating cuts and regressions for CBSA pop
df['UR'] = pd.cut(
    df['CBSA_POP'],
    bins=config.reg_bins_d,
    labels=config.reg_labels_d,
    include_lowest=True)

df['PHYS_PER_100K'] = df['PHYS_FRAC'] * 1e5

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

