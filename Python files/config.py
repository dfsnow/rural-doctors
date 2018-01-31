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
