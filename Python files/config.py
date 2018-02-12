# Config file for altering the behavior of puma_functions and puma_regressions
api_key2 = 'AIzaSyBrF3K4-hyWFzTHhuoLFvFKdLHxAGM-uUU'
api_key = 'AIzaSyCwq01goipCnW90-LMSSvCrkXcFzU_dBYk'

# Dictionary for use with cenpy and the sjoin_puma function, specifies geographic unit
sjoin_geo_dict = {
    'cbsa': 'metropolitan statistical area/micropolitan statistical area:*',
    'puma': 'public use microdata area:*',
    'uac': 'urban area:*',
    'csa': 'combined statistical area:*',
    'state': 'state:*',
    'county': 'county:*'
}

# Dictionary which determine which columns remain as output from sjoin_puma
sjoin_col_dict = {
    'GEOID10': 'PUMA_GEOID',
    'NAMELSAD10': 'PUMA_NAME',
    'GEOID': 'XXX_GEOID',
    'NAME': 'XXX_NAME',
    'POP': 'XXX_POP'
}

# Dictionary determining which occupation codes get_puma_pop should filter for
census_occ_dict = {
    3060: 'PHYS',
    3110: 'PA',
    3050: 'PHARM',
    3010: 'DENTIST',
    3130: 'NURSE'
}

# Various regression bins for use with puma_regressions
reg_bins_a = [0, 1, 5e5, 1e6, 5e6, 1e8]
reg_labels_a = ['Rural', '500k', '1M', '5M', '5M+']

reg_bins_b = [0, 1e4, 5e4, 2.5e6, 1e8]
reg_labels_b = ['Rural', 'Micro', 'Metro', 'Big']

reg_bins_c = [0, 1, 7.5e5, 2.5e6, 6e6, 1e8]
reg_labels_c = ['Rural', '750k', '2.5M', '6M', 'BIG']

reg_bins_d = [0, 2.5e5, 1e6, 2.5e6, 6e6, 1e8]
reg_labels_d = ['Rural', '1M', '2.5M', '6M', 'BIG']



