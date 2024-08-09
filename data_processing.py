# CMPT 353 - Final Project
# Authors: Benley Hsiang
#          April Nguyen
#          Gia Hue (Hayden) Mai
#   
# Description: Process crimedata.csv for analysis. (ETL Task)
#              Outputs a file crime_census.csv for other files to run.
#              Crime data taken from the 
#                       Vancouver Police Department (2003-2024): https://geodash.vpd.ca/opendata/
#                       City of Montreal: https://donnees.montreal.ca/dataset/actes-criminels
#                       Toronto Police Service: https://data.torontopolice.on.ca/pages/5245ab054fed48758557597256227049
#              Canadian 2021 Census is obtain from the CensusMapper API in R: https://censusmapper.ca/api
#
# data_processing.py
# Last modified: July 29, 2024

import os
import pathlib
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# For renaming columns
rename_cols = {'v_CA21_1: Population, 2021' : 'pop_21',
               'v_CA21_5802: No high school diploma or equivalency certificate' : 'hs_dropout',
               'v_CA21_560: Median total income in 2020 among recipients ($)' : 'median_income',
               'Area (sq km)' : 'area_sqkm',
               'v_CA21_499: Total number of census families in private households' : 'total_families',
               'v_CA21_500: Total couple families' : 'two_parent_families',
               'v_CA21_507: Total one-parent families' : 'one_parent_families',
               'v_CA21_4257: Total - Private households by number of persons per room' : 'total_households',
               'v_CA21_4259: More than one person per room' : 'households_more_than_one_per_room',
               'v_CA21_5799: Total - Secondary (high) school diploma or equivalency certificate for the population aged 15 years and over in private households' : 'total_highschool_count',
               'v_CA21_11: 0 to 14 years' : 'age_0_to_14',
               'v_CA21_9: Total - Age' : 'age_count_males',
               'v_CA21_453: Marital status for the total population aged 15 years and over' : 'marital_count',
               'v_CA21_486: Divorced' : 'divorced', 
               'v_CA21_4914: Not a visible minority' : 'non_minority_count',
               'v_CA21_4872: Total - Visible minority for the population in private households' : 'minority_count', 
               'v_CA21_1040: Prevalence of low income based on the Low-income measure, after tax (LIM-AT) (%)' : 'low_income_status_pct',
               'v_CA21_4239: Renter' : 'home_renters',
               'v_CA21_4237: Total - Private households by tenure' : 'people_in_homes',
               }

# Dropping uneeded columns
drop_cols = ['CSD_UID', 'CMA_UID', 'Dwellings 2016', 'Population', 'Dwellings',
             'Population 2016', 'Households', 'Type', 'GeoUID', 'Households 2016',
             'Quality Flags', 'Shape Area', 'CD_UID', 'Region Name',
             'v_CA21_7: Land area in square kilometres']


# Description: Converts UTM Zone 10 XY Coordinates to a Point object
# Precondition: crime_row is a single row containing columns X & Y
# Returns a Point object
def utm10_to_Point(crime_row):
    return Point(crime_row.X, crime_row.Y)


# Description: Finds the nearest census geometry block given a Point
# Precondition: point is a row of crime data, census is the entire GeoDataFrame
# Returns the name of the census tract of where the crime occurred
def closest_CT(point, census):
    # make a list of distance between a crime and all CT blocks in the census
    # the distance() function is part of geopandas
    # calculates the distance between geometry in census to a single Point object in crime
    # return 0 if it is inside of the census, otherwise gives a value
    distances = census.geometry.distance(point.geometry)

    # get the index of the closest CT block to the point
    closest_index = distances.argmin()

    # take the row of the census & return
    census_CT = census.loc[closest_index]

    return census_CT['name']


# Description: Calculate the crime count for each census tract
# Precondition: crimes, census are data sets, epsg is a string containing EPSG information to such data
# Returns a GeoDataFrame containing the census data with crime counts
def census_crime_count(crimes, census, epsg):
    # Convert census's geometry from epsg:4326 to the appropriate EPSG for distance function
    census.geometry = census.geometry.to_crs(epsg)

    # Entity Resolution - where the crime happened on census tract
    # Find the closest CT and join that row with the crime (hopefully its accurate enough after EPSG conversion)
    # crime_CT will contain the best census tract, tracked by the index value
    # This is the same procedure as Exercise 4
    crime_CT = crimes.apply(closest_CT, census = census, axis = 1)

    # Name the Series to join
    crime_CT.name = "name"

    # Merging the two tables together by index
    crimes_census_CT = crimes.join(crime_CT, how = "right")

    # Group data by census tract and count the number of crimes occured that area
    # Pick any column and count, in this case 'X' is used
    crimes_census = crimes_census_CT.groupby(by = ['name']) \
                    .X.count() \
                    .rename("crime_count") \
                    .reset_index()
    
    # Outer join so now we will have NaN values for where crimes didn't occur in census tract
    crimes_census = crimes_census.merge(census['name'], on = ['name'], how = 'outer')

    # Fill those NaN with 0s
    crimes_census['crime_count'] = crimes_census['crime_count'].fillna(0)

    # Join the rest of the census data to the same census tract name
    crimes_census_final = crimes_census.merge(census, on = 'name', how = 'inner')

    return crimes_census_final


# Description: Takes the dataframe with census data and calculates the variables for analysis. 
#              Returns the dataframe with only the relevant variables.  
def feature_engineer(city_data):
    # Removing rows with empty values
    city_data = city_data.dropna()
    
    # Removing rows with 0
    city_data = city_data[city_data['pop_21'] != 0]
    city_data = city_data[city_data['total_families'] != 0]
    
    # Calculating population density
    city_data['pop_density'] = city_data['pop_21'] / city_data['area_sqkm']
    
    # Calculating proportion of high school dropouts to graduates
    city_data['dropouts_to_grads'] = city_data['hs_dropout'] / city_data['total_highschool_count']
    
    # Calculating proportion of single-parent to two-parent families
    city_data['one_parent_to_two'] = city_data['one_parent_families'] / city_data['total_families']
    
    # Calculating proportion of crowded to non-crowded households
    city_data['crowded_to_not'] = city_data['households_more_than_one_per_room'] / city_data['total_households']
    
    # Calculating proportion of children to adults
    city_data['children_to_adults'] = city_data['age_0_to_14'] / city_data['pop_21']
    
    # Calculating proportion of non-minorities to minorities
    city_data['non_minority_to_minority'] = city_data['non_minority_count'] / city_data['minority_count']
    
    # Calculating proportion of males to females
    city_data['male_to_female'] = city_data['age_count_males'] / city_data['pop_21']
    
    # Calculating divorce rate
    city_data['divorce_rate'] = city_data['divorced'] / city_data['marital_count']
    
    # Calculating proportion of home renters to home owners
    city_data['home_renters_to_owners'] = city_data['home_renters'] / city_data['people_in_homes']
    
    # Calculating crime rate
    city_data['crime_rate'] = city_data['crime_count'] / city_data['pop_21']
    
    # Keeping only the necessary columns
    city_data = city_data[['name', 'pop_density', 'dropouts_to_grads', 'one_parent_to_two', 
                           'crowded_to_not', 'children_to_adults', 'non_minority_to_minority',
                           'male_to_female', 'divorce_rate', 'home_renters_to_owners',
                           'low_income_status_pct', 'crime_rate', 'geometry']]
    
    # Returning the filtered dataframe
    return city_data


def main():
    input_dir = pathlib.Path('datasets')
    output_dir = pathlib.Path('crime_census')

    # Read the data
    crimes_van = pd.read_csv(input_dir / "crimedata_van.zip", compression = 'zip')
    crimes_tor = gpd.read_file(input_dir / "crimedata_tor.zip")
    crimes_mon = gpd.read_file(input_dir / "crimedata_mon.zip")
    van_census = gpd.read_file(input_dir / "censusdata_van.geojson")
    tor_census = gpd.read_file(input_dir / "censusdata_tor.geojson")
    mon_census = gpd.read_file(input_dir / "censusdata_mon.geojson")

    # Filter all crimes data to only contain 2021
    crimes_van = crimes_van[(crimes_van.YEAR == 2021)]
    crimes_tor = crimes_tor[(crimes_tor.OCC_YEAR == 2021)]
    crimes_mon = crimes_mon[(crimes_mon.DATE.dt.year == 2021)]

    # Filter out data where longitude and latitude are omitted
    crimes_van = crimes_van[(crimes_van.X > 0) | (crimes_van.Y > 0)]
    crimes_tor = crimes_tor[(crimes_tor.LONG_WGS84 < 0) | (crimes_tor.LAT_WGS84 > 0)]
    crimes_mon = crimes_mon[(crimes_mon.X.notnull()) | (crimes_mon.Y.notnull())]

    # Filter out best we could to have only crimes that occurs across datasets
    # Toronto: keep everything (?), does not contain homicides & vehicle collisions
    # Vancouver: remove vehicle collisions & homicide
    # Montreal: remove Infractions entrainant la mort (homicide, etc.), no vehicle collisions
    crimes_van = crimes_van[(crimes_van.TYPE != "Homicide") & 
                            (crimes_van.TYPE != "Vehicle Collision or Pedestrian Struck (with Fatality)") & 
                            (crimes_van.TYPE != "Vehicle Collision or Pedestrian Struck (with Injury)")]

    crimes_mon = crimes_mon[crimes_mon.CATEGORIE != "Infractions entrainant la mort"]

    # Drop all other columns that is not location or geometry since we don't care about them
    crimes_van_loc = crimes_van[['X', 'Y']]
    crimes_tor_loc = crimes_tor[['LONG_WGS84', 'LAT_WGS84', 'geometry']] \
                    .rename(columns = {'LONG_WGS84':'X'}) # just to work in transform_data()
    crimes_mon_loc = crimes_mon[['X', 'Y', 'geometry']]

    
    # CHANGE WHEN ADDING FEATURES
    # Same goes for census data, dropping is faster because the columns texts are way too long to copy paste
    van_census = van_census.drop(columns = drop_cols)
    tor_census = tor_census.drop(columns = drop_cols)
    mon_census = mon_census.drop(columns = drop_cols)

    # Shorten column names
    van_census = van_census.rename(columns = rename_cols)
    tor_census = tor_census.rename(columns = rename_cols)
    mon_census = mon_census.rename(columns = rename_cols)
    
    # Prep the data for census_crime_count()
    # Use utm_to_Point to get each row a Points object
    # Toronto and Montreal already have them
    crimes_van_Points = crimes_van_loc.apply(utm10_to_Point, axis = 1)

    # Converting XY data in crime to the format other geometry data are using
    # Data is using UTM Zone 10 and epsg:32610 is the appropriate format
    # Use .to_crs("epsg:4326") for mapping, epsg:32610 is for getting distance
    # https://gis.stackexchange.com/questions/431058/getting-wrong-coordinates-converting-utm-to-lon-lat-with-proj
    crimes_van_Points = gpd.GeoSeries(crimes_van_Points, crs = 32610)
    crimes_van_Points.name = 'geometry'
    crimes_van_loc = gpd.GeoDataFrame(crimes_van_loc)
    crimes_van_loc = crimes_van_loc.join(crimes_van_Points)

    # Convert other geometry GeoDataFrame to the same format for calculating distance
    # toronto is epsg:2958
    # montreal is epsg:2950
    # https://pyproj4.github.io/pyproj/stable/examples.html
    # Map: https://crs-explorer.proj.org/?ignoreWorld=false&allowDeprecated=false&authorities=EPSG&activeTypes=PROJECTED_CRS&map=osm
    crimes_tor_loc.loc[:, "geometry"] = crimes_tor_loc.geometry.to_crs(crs = 'epsg:2958')
    crimes_mon_loc.loc[:, "geometry"] = crimes_mon_loc.geometry.to_crs(crs = 'epsg:2950')

    # setting crs format to its proper EPSG, for some reason it doesn't get converted properly
    # https://stackoverflow.com/questions/66365200/to-crsepsg4326-retruns-different-coordinate
    temp = crimes_tor_loc.set_crs('epsg:2958', allow_override= True, inplace = True)
    crimes_mon_loc = crimes_mon_loc.copy().set_crs('epsg:2950', allow_override= True, inplace = True)


    # Merging Data - automated step because it's all now in the same format kinda
    # list for loop to use
    crimes_cities = [crimes_van_loc, crimes_tor_loc, crimes_mon_loc]
    census_cities = [van_census, tor_census, mon_census]
    epsg = ["epsg:32610", "epsg:2958", "epsg:2950"]
    cities_str = ['_van', '_tor', '_mon']

    # Make a folder
    os.makedirs(output_dir, exist_ok=True)

    # Loop for merging crime and census for 3 cities
    for i in range(3):
        # Function will merge data
        crime_census_save = census_crime_count(crimes_cities[i], census_cities[i], epsg[i])

        # Calculate features
        crime_census_save2 = feature_engineer(crime_census_save)
        
        # Convert to geo dataframe
        crimes_final = gpd.GeoDataFrame(crime_census_save2)

        # Convert geometry back to epsg:4326 & save file to crime_census as GeoJSON
        crimes_final.geometry = crimes_final.geometry.to_crs("epsg:4326")
        crimes_final.to_file(filename = output_dir / ('crime_census'+cities_str[i]+'.geojson'), driver='GeoJSON')


if __name__=='__main__':
    main()
