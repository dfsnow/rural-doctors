geo_dict = {
    'cbsa': 'metropolitan statistical area/micropolitan statistical area:*',
    'uac': 'urban area:*',
    'csa': 'combined statistical area',
    'state': 'state'
}

cbsa_col_dict = {
    'GEOID10': 'PUMA_GEOID',
    'NAMELSAD10': 'PUMA_NAME',
    'GEOID': 'CBSA_GEOID',
    'NAME': 'CBSA_NAME',
    'POP': 'CBSA_POP'
}

uac_col_dict = {
    'GEOID10': 'PUMA_GEOID',
    'NAMELSAD10': 'PUMA_NAME',
    'UACE': 'UAC_POP',
    'NAME': 'UAC_NAME',
    'POP': 'UAC_POP'
}

csa_col_dict = {
    'GEOID10': 'PUMA_GEOID',
    'NAMELSAD10': 'PUMA_NAME',
    'GEOID': 'CSA_POP',
    'NAME': 'UAC_NAME',
    'POP': 'UAC_POP'
}