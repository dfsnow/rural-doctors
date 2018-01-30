library(sf)
library(rgdal)
library(glue)
library(dplyr)
library(maptools)

# Setup variables
file_name = 'ipums_puma_2010'
working_dir <- './R files/tempdir'

# Reading in the shapefiles
map <- readOGR(working_dir, file_name)

# Changing the CRS to 2163
crs <- CRS('+proj=laea +lat_0=45 +lon_0=-100 +x_0=0 +y_0=0 +a=6370997 +b=6370997 +units=m +no_defs')
map <- spTransform(map, crs)

# Extract Alaska, then scale, rotate and shift
alaska <- map[map@data$STATEFIP=="02",]
alaska <- elide(alaska, rotate=-50)
alaska <- elide(alaska, scale=max(apply(bbox(alaska), 1, diff)) / 2.3)
alaska <- elide(alaska, shift=c(-2100000, -2500000))
proj4string(alaska) <- proj4string(map)

# Extract, then rotate & shift hawaii
hawaii <- map[map@data$STATEFIP=="15",]
hawaii <- elide(hawaii, rotate=-35)
hawaii <- elide(hawaii, shift=c(5400000, -1600000))
proj4string(hawaii) <- proj4string(map)

# Remove old states and replace with transformed ones
map <- map[!map@data$STATEFIP %in% c("02", "15", "72"),]
map <- rbind(map, alaska, hawaii)

# Saving the resulting shapefile
writeOGR(map,
         dsn = working_dir,
         layer = paste0(file_name, '_fixed'),
         overwrite_layer = TRUE,
         driver = "ESRI Shapefile")



