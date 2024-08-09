# CMPT 353 - Final Project
#
# vancouver_crime_map.py
#
# Authors: Benley Hsiang
#          April Nguyen
#          Gia Hue (Hayden) Mai
#
# Description:  Creates a choropleth map of the crimes count in Vancouver separated by neighbourhoods.
#               Uses the vancouver.geojson from https://opendata.vancouver.ca/explore/dataset/local-area-boundary/information/?disjunctive.name
#               Crime counts taken from the Vancouver Police Department (2003-2024) https://geodash.vpd.ca/opendata/
#               In order to match the VPD's information:
#                   - Stanley Park is omitted
#                   - Musqueam is merged with Dunbar Southlands
#
# Last modified: July 27, 2024

import pathlib
import os
import pandas as pd
import geopandas as gpd
# from operator import ne
# from shapely.ops import unary_union
import numpy as np
import folium
from folium import Choropleth

def main():
    # Load the crime data
    input_dir = pathlib.Path('datasets')
    data = pd.read_csv(input_dir / 'crimedata_van.zip', compression = 'zip')

    # Rename {Central Business District: Downtown, Musqueam: Dunbar Southlands}
    data['NEIGHBOURHOOD'] = data['NEIGHBOURHOOD'].replace({
        'Central Business District': 'Downtown',
        'Musqueam': 'Dunbar Southlands'
    })

    # Drop Stanley Park
    data = data[data['NEIGHBOURHOOD'] != 'Stanley Park']

    # Keep only 2021 data to match the census data
    data = data[data['YEAR'] == 2021]

    # Only care about the neighbourhood and how many crimes occurred in that neighbourhood (2 columns)
    crime_counts = data['NEIGHBOURHOOD'].value_counts().reset_index()  # count number of occurrences
    crime_counts.columns = ['NEIGHBOURHOOD', 'CRIME_COUNT']  # rename columns


    # # NEW VANCOUVER.GEOJSON CONTAINS BETTER REGION BOUNDARIES, NO NEED TO JOIN GEOMETRY :)
    # # THIS CODE IS LEFT HERE FOR FUTURE USE IF NEEDED

    # Load Vancouver neighborhoods GeoJSON file
    # gdf = gpd.read_file('vancouver.geojson')

    # # Extract geometries for Strathcona and Downtown Eastside
    # strathcona_geom = gdf[gdf['name'] == 'Strathcona'].geometry.values[0]
    # downtown_geom = gdf[gdf['name'] == 'Downtown Eastside'].geometry.values[0]

    # # Combine Strathcona and Downtown Eastside geometries
    # # https://shapely.readthedocs.io/en/stable/reference/shapely.unary_union.html
    # combined_geom = unary_union([strathcona_geom, downtown_geom])

    # # Create a new GeoDataFrame for the combined feature
    # combined_gdf = gpd.GeoDataFrame({
    #     'name': ['Strathcona'],  # the combined area is named Strathcona, as per the crimedata.csv
    #     'geometry': [combined_geom]
    #     },
    #     crs=gdf.crs)  # uses the same spatial reference system

    # # Filter out Strathcona and Downtown Eastside from the original GeoDataFrame
    # other_geometries = gdf[(gdf['name'] != 'Strathcona') & (gdf['name'] != 'Downtown Eastside')]

    # # Combine the original geometries with the new combined geometry
    # combined_gdf = pd.concat([other_geometries, combined_gdf], ignore_index=True)

    # # Convert all columns to strings where applicable to ensure JSON serialization
    # combined_gdf['created_at'] = combined_gdf['created_at'].astype(str)
    # combined_gdf['updated_at'] = combined_gdf['updated_at'].astype(str)

    # # Save the updated GeoJSON file
    # combined_gdf.to_file('vancouver_combined.geojson', driver='GeoJSON')


    # Load the Vancouver neighborhoods GeoJSON file
    # https://opendata.vancouver.ca/explore/dataset/local-area-boundary/information/?disjunctive.name
    # neighborhoods = gpd.read_file('vancouver_combined.geojson')
    neighborhoods = gpd.read_file(input_dir / 'vancouver.geojson')

    # Rename the GeoJSON 'name' column to 'NEIGHBOURHOOD' to match the crime data
    neighborhoods = neighborhoods.rename(columns={'name': 'NEIGHBOURHOOD'})

    # Merge the crime counts with the GeoDataFrame
    neighborhoods = neighborhoods.merge(crime_counts, on='NEIGHBOURHOOD', how='left')
    neighborhoods['CRIME_COUNT'] = neighborhoods['CRIME_COUNT'].fillna(0)

    # Create a folium map centered on Vancouver
    # https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_popup_and_tooltip.html
    map = folium.Map(location=[49.2827, -123.1207], zoom_start=12)

    # Values for scaling colour in choropleth layer
    # Using the logarithmic scale to better display choropleth information
    neighborhoods["CRIME_COUNT_log"] = np.log(neighborhoods.CRIME_COUNT)
    #bins = list(neighborhoods.CRIME_COUNT.quantile([0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]))
    bins = list(neighborhoods.CRIME_COUNT_log.quantile([0, 0.20, 0.4, 0.6, 0.95, 1.0]))


    # Add the choropleth layer
    # https://stackoverflow.com/questions/69607123/attempting-to-use-choropleth-maps-in-folium-for-first-time-index-error
    Choropleth(
        geo_data=neighborhoods,
        data=neighborhoods,
        columns=['NEIGHBOURHOOD', 'CRIME_COUNT_log'],
        key_on='feature.properties.NEIGHBOURHOOD',
        fill_color='BuPu',
        fill_opacity=0.75,
        line_opacity=0.2,
        bins = bins,
        legend_name='Log Scaled Crime Count'
    ).add_to(map)

    # Add a tooltip to display neighborhood names and crime counts
    # https://python-visualization.github.io/folium/latest/user_guide/geojson/geojson_popup_and_tooltip.html
    folium.GeoJson(
        neighborhoods,
        name='Neighborhoods',
        tooltip=folium.GeoJsonTooltip(
            fields=['NEIGHBOURHOOD', 'CRIME_COUNT'],
            aliases=['Neighbourhood', 'Crime Count'],
            localize=True
        )
    ).add_to(map)

    # Save the map to an HTML file
    map.save('vancouver_crime_map.html')

if __name__ == "__main__":
    main()
