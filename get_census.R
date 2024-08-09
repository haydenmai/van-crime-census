# CMPT 353 - Final Project
# Authors: Benley Hsiang
#          April Nguyen
#          Gia Hue (Hayden) Mai
#   
# Description: Retrieve censusmapper data from API
#
# get_census.R
# Last modified: July 29, 2024

#install.packages("cancensus")
#install.packages("sf")
library(cancensus)
library(sf)
options(cancensus.api_key='CensusMapper_1268dd90b165d7d942fd8688011dbcf5')

# retrieve data from censusmapper.ca
# if you want to modify "vectors", go to censusmapper.ca API and see the variable names in "Variable Selection"
censusdata_van <- get_census(dataset='CA21', 
                             regions=list(CT="9330008.01",CSD="5915022"), 
                             vectors=c("v_CA21_5802","v_CA21_560","v_CA21_1","v_CA21_7","v_CA21_499",
                                       "v_CA21_500","v_CA21_507","v_CA21_4257","v_CA21_4259","v_CA21_5799", 
                                       "v_CA21_4914","v_CA21_4872","v_CA21_11","v_CA21_9","v_CA21_1040","v_CA21_453","v_CA21_486","v_CA21_4239","v_CA21_4237"),
                             labels="detailed", 
                             geo_format="sf",
                             level='CT')

censusdata_mon <- get_census(dataset='CA21', 
                             regions=list(CSD=c("2466023","2466007","2466072","2466058","2466032","2466062","2466047","2466087","2466142","2466097","2466102","2466107","2466127","2466117","2466112")), 
                             vectors=c("v_CA21_5802","v_CA21_560","v_CA21_1","v_CA21_7","v_CA21_499",
                                       "v_CA21_500","v_CA21_507","v_CA21_4257","v_CA21_4259","v_CA21_5799",
                                       "v_CA21_4914","v_CA21_4872","v_CA21_11","v_CA21_9","v_CA21_1040","v_CA21_453","v_CA21_486","v_CA21_4239","v_CA21_4237"), 
                             labels="detailed", 
                             geo_format="sf",
                             level='CT')


censusdata_tor <- get_census(dataset='CA21', 
                             regions=list(CSD="3520005"), 
                             vectors=c("v_CA21_5802","v_CA21_560","v_CA21_1","v_CA21_7","v_CA21_499",
                                       "v_CA21_500","v_CA21_507","v_CA21_4257","v_CA21_4259","v_CA21_5799",
                                       "v_CA21_4914","v_CA21_4872","v_CA21_11","v_CA21_9","v_CA21_1040","v_CA21_453","v_CA21_486","v_CA21_4239","v_CA21_4237"), 
                             labels="detailed", 
                             geo_format="sf",
                             level='CT')

# save as GeoJSON files for geopandas in Python in datasets folder
# I tried .shp, but it also created a bunch of other files
st_write(censusdata_van, "datasets/censusdata_van.geojson", delete_dsn = TRUE)
st_write(censusdata_mon, "datasets/censusdata_mon.geojson", delete_dsn = TRUE)
st_write(censusdata_tor, "datasets/censusdata_tor.geojson", delete_dsn = TRUE)
