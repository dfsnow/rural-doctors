import col_dictionaries as dict
import geopandas as gpd
import pandas as pd
import cenpy as cp
import os
import re


def sjoin_puma(year='2015', type='cbsa', join='intersect', shapefile_dir='', drop_geometry=True):

    """This is a function which performs spatial joins on census shapefiles. It outputs a dataframe of PUMAs
    and intersecting larger geographic units of your choice and specified method. It drops duplicate PUMAs
    based on descending population of the intersecting geographic unit. See arguments below:

    year = Year of the census population data to use, between 2011 and 2016

    type = Geographic unit which intersects PUMA, choose from CBSA, UAC, CSA, or state

    join = Type of spatial join to perform, choose intersect or centroid

    shapefile_dir = Directory of shapefiles to use for intersection, must follow the naming convention
    ti_%YEAR%_us_%TYPE%.shp for PUMAs and other units

    drop_geometry = Will drop all geometry and leave only a dataframe crosswalk for output to a CSV
    """

    api_conn = cp.base.Connection('ACSSF1Y' + str(year))

    geo_pop = api_conn.query(['B01001_001E'], geo_unit=dict.geo_dict[type])
    geo_pop.rename(columns={'B01001_001E': 'POP', geo_pop.columns[-1]: 'GEOID'}, inplace=True)

    puma = gpd.read_file(os.path.join(shapefile_dir, 'ti_' + str(year) + '_us_puma.shp'))
    match = gpd.read_file(os.path.join(shapefile_dir, 'ti_' + str(year) + '_us_' + type + '.shp'))
    match = match.rename(columns=lambda x: re.sub('\d+', '', x))

    match['geometry'] = match.geometry.buffer(-(1e-10))

    if join == 'centroid':
        geo_sjoined = gpd.sjoin(puma.set_geometry(puma.centroid), match, how='left', op='within')
    else:
        geo_sjoined = gpd.sjoin(puma, match, how='left', op='intersects')

    geo_merged = pd.DataFrame(geo_pop.merge(geo_sjoined, on='GEOID'))

    geo_merged = geo_merged.sort_values('POP', ascending=False)
    geo_merged = geo_merged[(~geo_merged['GEOID10'].duplicated()) | (geo_merged['GEOID'].isnull())]
    if drop_geometry:
        if type == 'cbsa':
            geo_merged = geo_merged[list(dict.cbsa_col_dict.keys())]
            geo_merged.rename(columns=dict.cbsa_col_dict, inplace=True)
        elif type == 'uac':
            geo_merged = geo_merged[list(dict.uac_col_dict.keys())]
            geo_merged.rename(columns=dict.uac_col_dict, inplace=True)
        elif type == 'csa':
            geo_merged = geo_merged[list(dict.csa_col_dict.keys())]
            geo_merged.rename(columns=dict.csa_col_dict, inplace=True)



    






