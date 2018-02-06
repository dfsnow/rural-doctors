# Config file for altering the behavior of puma_functions and puma_regressions

sjoin_geo_dict = {
    'cbsa': 'metropolitan statistical area/micropolitan statistical area:*',
    'uac': 'urban area:*',
    'csa': 'combined statistical area:*',
    'state': 'state:*',
    'county': 'county:*'
}

sjoin_col_dict = {
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

reg_cbsa_bins_a = [0, 1, 5e5, 1e6, 5e6, 1e8]
reg_cbsa_labels_a = ['Rural', '500k', '1M', '5M', '5M+']

reg_cbsa_bins_b = [0, 1e4, 5e4, 2.5e6, 1e8]
reg_cbsa_labels_b = ['Rural', 'Micro', 'Metro', 'Big']


