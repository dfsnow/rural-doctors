######## Setup ########
# These are setup variables for running the PUMA and CBSA/UAC intersection scripts. Here you can set the year of
# the files you're working with, the total negative buffer for intersection purposes, the output/read directory
# for shapefiles, and the columns needed from each dataset

year_needed = 2017
buffer_amount = -0.0000000001
working_dir = 'shapefiles'

cbsa_col_needed = ['GEOID10', 'NAMELSAD10', 'GEOID', 'NAME', '2016']
cbsa_col_names = ['PUMA_GEOID', 'PUMA_NAME', 'CBSA_GEOID', 'CBSA_NAME', 'CBSA_POP']

uac_col_needed = ['GEOID10_left', 'NAMELSAD10_left', 'UACE10', 'NAME', 'POP']
uac_col_names = ['PUMA_GEOID', 'PUMA_NAME', 'UAC_ID', 'UAC_NAME', 'UAC_POP']


