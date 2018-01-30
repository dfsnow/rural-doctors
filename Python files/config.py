######## Config ########
# Spatial data settings for working with shapefiles downloaded via R script
spatial_year = 2015  # year of spatial data files
spatial_buffer = -0.0000000001  # negative buffer for shinking PUMAs, in degrees
spatial_dir = 'shapefiles'  # directory in which shapefiles are located

# Census database for downloading population totals using cenpy
census_database = 'ACSSF5Y2015'  # census database name to pull from using cenpy
census_var_needed = ['B01001_001E']  # names of census variables to pull from database

# Lists and dictionaries for slicing and filtering downloaded IPUMS flat file/CSV
census_filename = '2011-2016_acs'
census_occ_codes = {
    3060: 'PHYS',
    3110: 'PA',
    3050: 'PHARM',
    3010: 'DENTIST',
    3130: 'NURSE'
}

# Data year and directory for all CSV files
temp_dir = 'tempdir'

# Columns needed + respective names for the final CBSA CSV
cbsa_col_needed = ['GEOID10', 'NAMELSAD10', 'GEOID', 'NAME', 'POP']
cbsa_col_names = ['PUMA_GEOID', 'PUMA_NAME', 'CBSA_GEOID', 'CBSA_NAME', 'CBSA_POP']

# Columns needed + respective names for the final UAC CSV
uac_col_needed = ['GEOID10_left', 'NAMELSAD10_left', 'UACE10', 'NAME10', 'POP']
uac_col_names = ['PUMA_GEOID', 'PUMA_NAME', 'UAC_ID', 'UAC_NAME', 'UAC_POP']

