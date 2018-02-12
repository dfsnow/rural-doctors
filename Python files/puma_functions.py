import config as config
import geopandas as gpd
import pandas as pd
import cenpy as cp
import os
import re


def concat_cols(df, col1, col2, fill1=2, fill2=5, return_col='PUMA_GEOID'):
    df[[col1, col2]] = df[[col1, col2]].astype(str)
    df[col1] = df[col1].str.zfill(fill1)
    df[col2] = df[col2].str.zfill(fill2)
    df[return_col] = df[col1] + df[col2]
    df[return_col] = df[return_col].astype(int)
    return df


def sjoin_puma(year=2015, type='cbsa', join='intersect', puma_shapefile=None,
               int_shapefile=None, shapefile_dir='.', drop_geometry=True):

    """Function which performs spatial joins on census shapefiles. Outputs a dataframe of PUMAs
    and intersecting larger geographic units of your choice and specified method. Drops duplicate PUMAs
    based on descending population of the intersecting geographic unit. See arguments below:

    year = Year of the census population data to use for drops, between 2011 and 2016

    type = Geographic unit which intersects PUMA, choose from CBSA, UAC, CSA, state, or county

    join = Type of spatial join to perform, choose intersect or centroid

    puma_shapefile = Name of the PUMA shapefile from Tiger or elsewhere

    int_shapefile = Name of the intersecting shapefile (CBSA, CSA, State, etc.)

    shapefile_dir = Name of directory of shapefiles to use for intersection

    drop_geometry = If true, will drop all geometry and leave only the variables specified in the config file
    """

    api_conn = cp.base.Connection('ACSSF5Y' + str(year))

    if type == 'county':
        geo_pop = api_conn.query(['B01001_001E'], geo_unit=config.sjoin_geo_dict[type])
        geo_pop.rename(columns={'B01001_001E': 'POP', 'state': 'STATEFIP', 'county': 'COUNTY'}, inplace=True)
        geo_pop = concat_cols(geo_pop, 'STATEFIP', 'COUNTY', 2, 3, 'GEOID')
    else:
        geo_pop = api_conn.query(['B01001_001E'], geo_unit=config.sjoin_geo_dict[type])
        geo_pop.rename(columns={'B01001_001E': 'POP', geo_pop.columns[-1]: 'GEOID'}, inplace=True)

    puma = gpd.read_file(os.path.join(shapefile_dir, str(puma_shapefile)))
    match = gpd.read_file(os.path.join(shapefile_dir, str(int_shapefile)))
    match = match.rename(columns=lambda x: re.sub('\d+', '', x))

    if join == 'intersect':
        match['geometry'] = match.geometry.buffer(-1e-10)
        geo_sjoined = gpd.sjoin(puma, match, how='left', op='intersects')
    elif join == 'centroid':
        geo_sjoined = gpd.sjoin(puma.set_geometry(puma.centroid), match, how='left', op='within')
    else:
        raise Exception('Join must be equal to either intersect or centroid.')

    geo_merged = pd.DataFrame(geo_pop.merge(geo_sjoined, on='GEOID'))
    geo_merged = geo_merged.sort_values('POP', ascending=False)
    geo_merged = geo_merged[(~geo_merged['GEOID10'].duplicated())]

    if drop_geometry:
        geo_merged = geo_merged[list(config.sjoin_col_dict.keys())]
        geo_merged.rename(columns=config.sjoin_col_dict, inplace=True)
        geo_merged.rename(columns=lambda x: re.sub('XXX', type.upper(), x), inplace=True)

    geo_merged['PUMA_GEOID'] = geo_merged['PUMA_GEOID'].astype(int)
    geo_merged = geo_merged.fillna(0)

    return geo_merged


def get_puma_pop(year=2015, acs_filename=None, acs_dir=None, occ_var='OCC2010'):

    # Grabbing the general population of each PUMA from the census API
    api_conn = cp.base.Connection('ACSSF1Y' + str(year))

    puma_gen_pop = api_conn.query(['B01001_001E'], geo_unit='public use microdata area:*')
    puma_gen_pop.rename(columns={'B01001_001E': 'POP',
                            'state': 'STATEFIP',
                            'public use microdata area': 'PUMA'
                            }, inplace=True)

    puma_gen_pop = concat_cols(puma_gen_pop, 'STATEFIP', 'PUMA')

    # Loading IPUMS data and creating a PUMA_GEOID variable
    acs = pd.read_csv(os.path.join(acs_dir, acs_filename), low_memory=False)
    acs = concat_cols(acs, 'STATEFIP', 'PUMA')

    # Filtering IPUMS data for real doctors only
    acs = acs[(acs['YEAR'] > 2011) & (acs['YEAR'] < 2016)]
    acs = acs[acs['AGE'] >= 30]
    acs = acs[acs['UHRSWORK'] >= 30]

    # Getting the count of doctors in each PUMA
    puma_med_pop = acs[acs[occ_var].isin(config.census_occ_dict.keys())]
    puma_med_pop = puma_med_pop.groupby(
        ['PUMA_GEOID', occ_var]).sum()['PERWT'].unstack(occ_var).reset_index()

    # Merging the total population data with the medical population data
    puma_pop = pd.merge(
        puma_med_pop,
        puma_gen_pop,
        how='left',
        on=['PUMA_GEOID'])
    puma_pop.columns.name = None
    puma_pop.rename(columns=config.census_occ_dict, inplace=True)

    # Calculating the fraction of the population which is medical
    for x in config.census_occ_dict.values():
        puma_pop[x] = puma_pop[x] / len(set(acs['YEAR']))
        puma_pop[x + '_FRAC'] = puma_pop[x] / puma_pop['POP']

    # Cleaning up
    puma_pop = puma_pop.fillna(0)

    return puma_pop
"""

- Include as filter condition EDUCD as professional degree (114 - 116)
- Hours worked >= 30
- Age >= 25

- Reduce ACS into phys, nurse, etc

- Functionalize regression changes

- Check ACS vars
- Fix docstrings of puma_functions
"""
