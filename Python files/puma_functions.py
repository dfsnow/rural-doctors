import config as config
import geopandas as gpd
import pandas as pd
import cenpy as cp
import os
import re


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

    api_conn = cp.base.Connection('ACSSF1Y' + str(year))

    if type == 'county':
        geo_pop = api_conn.query(['B01001_001E'], geo_unit=config.sjoin_geo_dict[type])
        geo_pop.rename(columns={'B01001_001E': 'POP', 'state': 'STATEFIP', 'county': 'COUNTY'}, inplace=True)
        geo_pop[['STATEFIP', 'COUNTY']] = geo_pop[['STATEFIP', 'COUNTY']].astype(str)
        geo_pop['STATEFIP'] = geo_pop['STATEFIP'].str.zfill(2)
        geo_pop['COUNTY'] = geo_pop['COUNTY'].str.zfill(3)
        geo_pop['GEOID'] = geo_pop['STATEFIP'] + geo_pop['PUMA']
        geo_pop['GEOID'] = geo_pop['GEOID'].astype(int)
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


def get_puma_pop(acs_filename=None, acs_dir=None, occ_var='OCC2010'):

    """Function to get the medical population for each PUMA from an IPUMS CSV file. Outputs a dataframe of
    medical populations (as specified in the config file) for each PUMA. See arguments below:

    acs_filename = Name of the IPUMS CSV file from which to extract medical population, file must contain
    PERWT, STATEFIP, PUMA, YEAR and some occupation variable

    acs_dir = Directory containing the IPUMS CSV file

    occ_var = Variable containing occupation codes, OCC2010 by default
    """

    acs = pd.read_csv(os.path.join(acs_dir, acs_filename), low_memory=False)

    acs[['STATEFIP', 'PUMA']] = acs[['STATEFIP', 'PUMA']].astype(str)
    acs['STATEFIP'] = acs['STATEFIP'].str.zfill(2)
    acs['PUMA'] = acs['PUMA'].str.zfill(5)
    acs['PUMA_GEOID'] = acs['STATEFIP'] + acs['PUMA']
    acs['PUMA_GEOID'] = acs['PUMA_GEOID'].astype(int)

    puma_gen_pop = acs.groupby(['YEAR', 'PUMA_GEOID']).sum()['PERWT'].reset_index()
    puma_gen_pop = puma_gen_pop.rename(columns={'PERWT': 'POP'})

    puma_med_pop = acs[acs[occ_var].isin(config.census_occ_dict.keys())]
    puma_med_pop = puma_med_pop.groupby(
        ['YEAR', 'PUMA_GEOID', occ_var]).sum()['PERWT'].unstack(occ_var).reset_index()

    puma_pop = pd.merge(
        puma_med_pop,
        puma_gen_pop,
        how='left',
        left_on=['YEAR', 'PUMA_GEOID'],
        right_on=['YEAR', 'PUMA_GEOID'])
    puma_pop.columns.name = None
    puma_pop.rename(columns=config.census_occ_dict, inplace=True)

    for x in config.census_occ_dict.values():
        puma_pop[x + '_FRAC'] = puma_pop[x] / puma_pop['POP']

    puma_pop = puma_pop.fillna(0)

    return puma_pop
