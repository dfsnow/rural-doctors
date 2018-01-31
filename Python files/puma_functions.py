import config as config
import seaborn as sns
import statsmodels.formula.api as smf
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

    year = Year of the census population data to use, between 2011 and 2016

    type = Geographic unit which intersects PUMA, choose from CBSA, UAC, CSA, or state

    join = Type of spatial join to perform, choose intersect or centroid

    puma_shapefile = Name of the PUMA shapefile from Tiger or elsewhere

    int_shapefile = Name of the intersecting shapefile (CBSA, CSA, State, etc.)

    shapefile_dir = Name of directory of shapefiles to use for intersection

    drop_geometry = If true, will drop all geometry and leave only the variables specified in the config file
    """

    api_conn = cp.base.Connection('ACSSF1Y' + str(year))

    geo_pop = api_conn.query(['B01001_001E'], geo_unit=config.geo_dict[type])
    geo_pop.rename(columns={'B01001_001E': 'POP', geo_pop.columns[-1]: 'GEOID'}, inplace=True)

    puma = gpd.read_file(os.path.join(shapefile_dir, str(puma_shapefile)))
    match = gpd.read_file(os.path.join(shapefile_dir, str(int_shapefile)))
    match = match.rename(columns=lambda x: re.sub('\d+', '', x))

    if join == 'intersect':
        match['geometry'] = match.geometry.buffer(-1e-10)
        geo_sjoined = gpd.sjoin(puma, match, how='left', op='intersects')
    elif join == 'centroid':
        geo_sjoined = gpd.sjoin(puma.set_geometry(puma.centroid), match, how='left', op='within')

    geo_merged = pd.DataFrame(geo_pop.merge(geo_sjoined, on='GEOID'))

    geo_merged = geo_merged.sort_values('POP', ascending=False)
    geo_merged = geo_merged[(~geo_merged['GEOID10'].duplicated()) | (geo_merged['GEOID'].isnull())]

    if drop_geometry:
        geo_merged = geo_merged[list(config.col_dict.keys())]
        geo_merged.rename(columns=config.col_dict, inplace=True)
        geo_merged.rename(columns=lambda x: re.sub('XXX', type.upper(), x), inplace=True)

    return geo_merged


def get_puma_pop(acs_filename=None, acs_dir=None):

    """Function to get the medical population for each PUMA from an IPUMS CSV file. Outputs a dataframe of
    medical populations (as specified in the config file) for each PUMA. See arguments below:

    acs_filename = Name of the IPUMS CSV file from which to extract medical population

    acs_dir = Directory containing the IPUMS CSV file
    """

    acs = pd.read_csv(os.path.join(acs_dir, acs_filename), nrows=20000, low_memory=False)

    acs[['STATEFIP', 'PUMA']] = acs[['STATEFIP', 'PUMA']].astype(str)
    acs['STATEFIP'] = acs['STATEFIP'].str.zfill(2)
    acs['PUMA'] = acs['PUMA'].str.zfill(5)
    acs['PUMA_GEOID'] = acs['STATEFIP'] + acs['PUMA']
    acs['PUMA_GEOID'] = acs['PUMA_GEOID'].astype(int)

    puma_gen_pop = acs.groupby(['YEAR', 'PUMA_GEOID']).sum()['PERWT'].reset_index()
    puma_gen_pop = puma_gen_pop.rename(columns={'PERWT': 'POP'})

    puma_med_pop = acs[acs['OCC2010'].isin(config.census_occ_dict.keys())]
    puma_med_pop = puma_med_pop.groupby(
        ['YEAR', 'PUMA_GEOID', 'OCC2010']).sum()['PERWT'].unstack('OCC2010').reset_index()

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

    return puma_pop


def reg_puma
    



