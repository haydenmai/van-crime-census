# CMPT 353 - Final Project
# Authors: Benley Hsiang
#          April Nguyen
#          Gia Hue (Hayden) Mai
#   
# Description: For each city, outputs a boxplot and histogram of the crime counts, and correlation matrix.
#              Scatter plot is created to visualize relationship between demographic feature counts and crime counts
#               - data points are created by taking the crime count and the feature count we are investigating
#                   - one data point corresponds to one geographic area
#                   - i.e. One data point is (x,y) = (feature count of geographic area, crime count of geographic area) 
#              Uses the crime_census_{city}.geojson data created by data_processing.py
#              Demographic features include: 
#               - 'pop_density'
#               - 'dropouts_to_grads'
#               - 'one_parent_to_two'
#               - 'crowded_to_not', 
#               - 'children_to_adults'
#               - 'non_minority_to_minority'
#               - 'male_to_female',
#               - 'divorce_rate'
#               - 'home_renters_to_owners'
#               - 'low_income_status_pct'
#
# initial_plots.py
# Last modified: July 31, 2024

import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import scipy
from scipy.stats import linregress
import os
import seaborn as sns
import pathlib

def main():
    cities = ['van']
    y = 'crime_rate'
    demographics = ['pop_density', 'dropouts_to_grads', 'one_parent_to_two', 'crowded_to_not', 
                'children_to_adults', 'non_minority_to_minority', 'male_to_female',
                'divorce_rate', 'home_renters_to_owners', 'low_income_status_pct']
    os.makedirs('initial_plots', exist_ok=True)
    for city in cities:
        city_folder = os.path.join('initial_plots', city)
        os.makedirs(city_folder, exist_ok=True)
        filename = 'crime_census_' + city + '.geojson'
        input_dir = pathlib.Path('crime_census')
        data = gpd.read_file(input_dir / filename)

        # Create a box plot. Shows the median, quartiles, range, outliers of crime counts for each city
        plt.figure(figsize=(10,5))
        data = data.dropna(subset=demographics)
        plt.boxplot(data[y], notch=True, vert=False)
        plt.title(f'Box Plot for {y} in {city}')
        saved_boxplot = os.path.join(city_folder, city + '_boxplot' + '.png')
        plt.savefig(saved_boxplot)
        plt.close()

        # Create a histogram to look at the rougth shape of the distribution of crime counts for each city
        plt.figure(figsize=(10,5))
        plt.hist(data[y])
        plt.title(f'Histogram for {y} in {city}')
        saved_hist = os.path.join(city_folder, city + '_hist' + '.png')
        plt.savefig(saved_hist)
        plt.close()

        for x in demographics:
            # Transform crime by the log
            data['log_' + y] = np.log(data[y] + 0.0000001)  # Adding 1 to avoid log(0)

            # Create a scatter plot of crime count vs some demographic feature with a linear regression
            fit = linregress(data[x], data[y])
            data['prediction'] = data[x]*fit.slope + fit.intercept
            plt.figure(figsize=(10,5))
            plt.plot(data[x], data[y], 'b.', alpha=0.5)
            plt.plot(data[x], data['prediction'], 'r-', linewidth=1)
            plt.grid(color='grey', linestyle='-', linewidth=0.5)
            plt.xlabel(x)
            plt.ylabel(y)
            plt.title(f'Scatter Plot for ({x}, {y})', fontsize=20)
            saved_plot = os.path.join(city_folder, x + '_scatter' + '.png')
            plt.savefig(saved_plot)
            plt.close()

            # Create a scatter plot of log(crime count) vs some demographic feature with a linear regression
            fit_logcrime = linregress(data[x], data['log_' + y])
            data['prediction'] = data[x]*fit_logcrime.slope + fit_logcrime.intercept
            plt.figure(figsize=(10,5))
            plt.plot(data[x], data['log_' + y], 'b.', alpha=0.5)
            plt.plot(data[x], data['prediction'], 'r-', linewidth=1)
            plt.grid(color='grey', linestyle='-', linewidth=0.5)
            plt.xlabel(x)
            plt.ylabel('log_' + y)
            plt.title(f'Scatter Plot for ({x}, log({y}))', fontsize=20)
            saved_plot = os.path.join(city_folder, x + '_logcrime_scatter' + '.png')
            plt.savefig(saved_plot)
            plt.close()

            # Some (maybe) useful information we get from the linear regression
            saved_linregress = os.path.join(city_folder, x + '_linregress' + '.txt')
            with open(saved_linregress, 'w') as file:
                file.write(f'Information we get from the linear regression for ({x}, {y})\n')
                file.write(f'{"Correlation coefficient:":<25}{fit.rvalue:>10.6f}\n')
                file.write(f'{"p-value:":<25}{fit.pvalue:>10.6f}\n')
                file.write(f'{"Error of slope:":<25}{fit.stderr:>10.6f}\n')
                file.write(f'{"Error of intercept:":<25}{fit.intercept_stderr:>10.6f}\n\n')

                file.write(f'Information we get from the linear regression for ({x}, log({y}))\n')
                file.write(f'{"Correlation coefficient:":<25}{fit_logcrime.rvalue:>10.6f}\n')
                file.write(f'{"p-value:":<25}{fit_logcrime.pvalue:>10.6f}\n')
                file.write(f'{"Error of slope:":<25}{fit_logcrime.stderr:>10.6f}\n')
                file.write(f'{"Error of intercept:":<25}{fit_logcrime.intercept_stderr:>10.6f}\n')

        # Create a correlation matrix for the demographic features and log(crime count)
        # https://www.geeksforgeeks.org/how-to-create-a-seaborn-correlation-heatmap-in-python/
        plt.figure(figsize=(10, 10))
        corr_matrix = data[['log_' + y] + demographics]
        # Generate a mask for the upper triangle
        mask = np.triu(np.ones_like(corr_matrix.corr(), dtype=bool))
        sns.heatmap(corr_matrix.corr(), mask = mask, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
        plt.title(f'Correlation matrix for {city}')
        plt.tight_layout()
        saved_corr_matrix = os.path.join(city_folder, city + '_correlation_matrix' + '.png')
        plt.savefig(saved_corr_matrix)
        plt.close()

    return

if __name__=='__main__':
    main()
