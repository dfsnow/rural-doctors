# Config file for altering the behavior of puma_functions

geo_dict = {
    'cbsa': 'metropolitan statistical area/micropolitan statistical area:*',
    'uac': 'urban area:*',
    'csa': 'combined statistical area',
    'state': 'state'
}

col_dict = {
    'GEOID10': 'PUMA_GEOID',
    'NAMELSAD10': 'PUMA_NAME',
    'GEOID': 'XXX_GEOID',
    'NAME': 'XXX_NAME',
    'POP': 'XXX_POP'
}

census_occ_dict = {
    3060: 'PHYS',
    3110: 'PA',
    3050: 'PHARM',
    3010: 'DENTIST',
    3130: 'NURSE'
}

reg_bins_a = {
    1: 'Rural',
    5e5: '500k',
    1e6: '1M',
    5e6: '5M',
    1e8: 'BIG'
}

reg_bins_b = {
    1e4: 'Rural',
    5e4: 'Micro',
    2.5e6: 'Metro',
    1e8: 'Big'
}
