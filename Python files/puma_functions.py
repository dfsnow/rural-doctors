import config
import utils
import geopandas as gpd
import pandas as pd
import cenpy as cp
import re


def get_puma_pop(year=2015):
    """ Get dataframe of general pop. of each PUMA for the specified year """
    api_conn = cp.base.Connection('ACSSF5Y' + str(year))
    df = api_conn.query(
        ['B01001_001E'],
        geo_unit='public use microdata area:*')
    df.rename(
        columns={
            'B01001_001E': 'POP',
            'state': 'STATEFIP',
            'public use microdata area': 'PUMA'
        },
        inplace=True)
    df = df[df['STATEFIP'] != 72]
    df = utils.concat_int_cols(df, 'STATEFIP', 'PUMA')
    return df


def sjoin_puma(
        year=2015, type='cbsa', join='intersect', puma_shapefile=None,
        int_shapefile=None, drop_geometry=True):
    """
    Perform spatial joins on census/TIGER shapefiles, drops duplicate PUMAs
    based on descending population of the intersecting geographic unit

    :param year: Year of the census population data to use for drops by pop
    :param type: Geographic unit which intersects PUMA
    :param join: Type of spatial join to perform, choose intersect or centroid
    :param puma_shapefile: Name of the PUMA shapefile from Tiger or elsewhere
    :param int_shapefile: Name of the intersecting shapefile
    :param drop_geometry: Drop all geometry and leave only the vars in config
    """
    api_conn = cp.base.Connection('ACSSF5Y' + str(year))
    if type == 'county':
        geo_pop = api_conn.query(
            ['B01001_001E'],
            geo_unit=config.sjoin_geo_dict[type])
        geo_pop.rename(
            columns={
                'B01001_001E': 'POP',
                'state': 'STATEFIP',
                'county': 'COUNTY'},
            inplace=True)
        geo_pop = utils.concat_int_cols(
            geo_pop, 'STATEFIP', 'COUNTY', 2, 3, 'GEOID')
    else:
        geo_pop = api_conn.query(
            ['B01001_001E'],
            geo_unit=config.sjoin_geo_dict[type])
        geo_pop.rename(
            columns={
                'B01001_001E': 'POP',
                geo_pop.columns[-1]: 'GEOID'},
            inplace=True)

    puma = gpd.read_file(str(puma_shapefile))
    match = gpd.read_file(str(int_shapefile))
    match = match.rename(columns=lambda x: re.sub('\d+', '', x))

    if join == 'intersect':
        match['geometry'] = match.geometry.buffer(-1e-10)
        geo_sjoined = gpd.sjoin(puma, match, how='left', op='intersects')
    elif join == 'centroid':
        geo_sjoined = gpd.sjoin(
            puma.set_geometry(puma.centroid),
            match,
            how='left',
            op='within')
    else:
        raise Exception('Join must be equal to either intersect or centroid.')

    geo_merged = pd.DataFrame(geo_pop.merge(geo_sjoined, on='GEOID'))
    geo_merged = geo_merged.sort_values('POP', ascending=False)
    geo_merged = geo_merged[(~geo_merged['GEOID10'].duplicated())]

    if drop_geometry:
        geo_merged = geo_merged[list(config.sjoin_col_dict.keys())]
        geo_merged.rename(columns=config.sjoin_col_dict, inplace=True)
        geo_merged.rename(
            columns=lambda x: re.sub('XXX', type.upper(), x),
            inplace=True)

    geo_merged['PUMA_GEOID'] = geo_merged['PUMA_GEOID'].astype(int)
    geo_merged = geo_merged.fillna(0)
    return geo_merged
