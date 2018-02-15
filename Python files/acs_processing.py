import puma_functions as pf
import acs_functions as af
import pandas as pd
import config
import utils
import os

# af.acs_process('2011-2016_acs_1yr_reduced.csv', 'data/')

df = pd.read_csv(os.path.join('data', '2011-2016_acs_PHYS.csv'))
df = af.acs_filter(df)
df = af.acs_counts(df)

df.to_csv('test.csv', index=False)

# TODO Fix puma matching/counts on acs_counts index, not filling with zeros
