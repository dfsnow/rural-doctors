library(tigris)
library(maps)
library(purrr)
library(rgdal)
library(glue)

# Use this variable to alter the year of the shapefile downloads
needed_year <- 2015

# Using the maps package to get all state FIPS codes into a dataframe
data(state.fips)


######## PUMAs ########
# Using the tigris package to download TIGER/Line files for PUMAs for
# each state, then combine them into a single shapefile/layer
assign(glue('ti_{y}_us_puma', y = needed_year), rbind_tigris(
  state.fips$fips %>%
    map(pumas, year = needed_year)))


######## CBSA/MSA ########
# Using the tigris package to download all the Core Based
# Statistical Areas (Metropolitan/Micropolitan Statistical Areas)
# for the needed year. Used assign() because of bug in tigris
assign(glue('ti_{y}_us_cbsa', y = needed_year), core_based_statistical_areas(
  year = needed_year))


######## Urban Areas ########
# Using the tigris package to download all US urban areas
assign(glue('ti_{y}_us_uac', y = needed_year), urban_areas(
  year = needed_year))


######## States ########
# Using the tigris package to download all US states area
assign(glue('ti_{y}_us_state', y = needed_year), states(
  year = needed_year))


######## Counties ########
# Using the tigris package to download all US counties area
assign(glue('ti_{y}_us_county', y = needed_year), counties(
  year = needed_year))


######## CSA ########
# Using the tigris package to download all US counties area
assign(glue('ti_{y}_us_csa', y = needed_year), combined_statistical_areas(
  year = needed_year))


######## Saving ########
# Saving all the resulting shapefiles to disk for use in Python or QGIS
spatial_df <- mget(ls(pattern = '_us_'))
spatial_df_names <- names(spatial_df)

spatial_df_names %>%
walk(function(x) {
  data <- spatial_df[[x]]
  writeOGR(
    data,
    dsn = "tempdir",
    layer = x,
    overwrite_layer = TRUE,
    driver = "ESRI Shapefile")
})
