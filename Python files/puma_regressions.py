import config
import statsmodels.formula.api as smf
import puma_functions as pf
import pandas as pd
import os

phys = pd.read_csv('test.csv')
cbsa_pop = pf.sjoin_puma(
    year=2015,
    type='cbsa',
    join='intersect',
    puma_shapefile=os.path.join('shapefiles', 'ti_2015_us_puma.shp'),
    int_shapefile=os.path.join('shapefiles', 'ti_2015_us_cbsa.shp'),
    drop_geometry=True
)

df = pd.merge(phys, cbsa_pop, how='left', on='PUMA_GEOID')
df = df.fillna(0)

df['UR'] = pd.cut(
    df['CBSA_POP'],
    bins=config.reg_bins_d,
    labels=config.reg_labels_d,
    include_lowest=True)

reg = smf.wls(formula='PHYS_PER_100K ~ UR', data=df, weights=df['POP']).fit().summary()
print(reg)

# Writing everything to a TeX doc
# begintex = """
# \\documentclass{report}
# \\usepackage{booktabs}
# \\begin{document}
# """
# endtex = """
# \end{document}"""
#
# f = open('reg.tex', 'w')
# f.write(begintex)
# f.write(reg)
# f.write(endtex)
# f.close()

