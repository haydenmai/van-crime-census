# CMPT 353 - Final Project
# Authors: Benley Hsiang
#          April Nguyen
#          Gia Hue (Hayden) Mai
#   
# Description: Create a regression model & doing statistical tests (ANOVA)
#              before the modelling step.
#              Crime data taken from the 
#                       Vancouver Police Department (2003-2024): https://geodash.vpd.ca/opendata/
#                       City of Montreal: https://donnees.montreal.ca/dataset/actes-criminels
#                       Toronto Police Service: https://data.torontopolice.on.ca/pages/5245ab054fed48758557597256227049
#              Canadian 2021 Census is obtain from the CensusMapper API in R: https://censusmapper.ca/api
#
# stats_analysis.py
# Last modified: July 31, 2024

import os
import pathlib
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import statsmodels.api as sm

def main():
    # read files
    input_dir = pathlib.Path('crime_census')
    van = gpd.read_file(input_dir / 'crime_census_van.geojson')
    tor = gpd.read_file(input_dir / 'crime_census_tor.geojson')
    mon = gpd.read_file(input_dir / 'crime_census_mon.geojson')

    # take the log as the data is right-skewed
    van['crime_rate_log'] = np.log(van.crime_rate + 0.000001)
    tor['crime_rate_log'] = np.log(tor.crime_rate + 0.000001)
    mon['crime_rate_log'] = np.log(mon.crime_rate + 0.000001)

    # normality test on the data
    print("Normality of crime_rate_log:")
    print("Vancouver:", stats.normaltest(van.crime_rate_log).pvalue)
    print("Toronto:", stats.normaltest(tor.crime_rate_log).pvalue)
    print("Montreal:", stats.normaltest(mon.crime_rate_log).pvalue)

    # Regression model of vancouver
    # Variables for regression
    X_vars = van[['pop_density', 'dropouts_to_grads', 'one_parent_to_two', 'crowded_to_not', 
                  'non_minority_to_minority', 'male_to_female',
                   'home_renters_to_owners', 'low_income_status_pct']].copy()

    # Ones for intercept because sm.OLS doesn't include an intercept
    X_vars['one'] = np.ones(X_vars.shape[0])

    # OLS Model
    print("\n")
    ols_model = sm.OLS(van.crime_rate_log, X_vars).fit()
    print(ols_model.summary())

    # making sure residuals are normal
    output_dir = pathlib.Path('stats_analysis')
    os.makedirs(output_dir, exist_ok=True)

    residuals = ols_model.resid
    sns.set_theme(style="darkgrid")
    plt.hist(residuals)
    plt.title("Residuals of OLS Regression")
    plt.ylabel("Count")
    plt.xlabel("Residual")
    plt.savefig(output_dir / "residuals.png")

    print("\nNormality Test of Residuals p-value:")
    print(stats.normaltest(residuals).pvalue)

    # anova of crime between 3 cities
    anova = stats.f_oneway(van.crime_rate_log, tor.crime_rate_log, mon.crime_rate_log)
    print("\n\nComparing Crime Rate of 3 Cities")
    print("ANOVA p-value result: {} \n".format(anova.pvalue))

    # tukey's HSD
    # convert dataframe into one column of values & one for labels using pd.melt
    data = pd.DataFrame(van.crime_rate_log)
    data = data.join(tor.crime_rate_log, how = 'outer', rsuffix = '_tor')
    data = data.join(mon.crime_rate_log, how = 'outer', rsuffix = '_mon')

    # rename columns for easier intepretation
    data = data.rename(columns = {'crime_rate_log':'Vancouver',
                                  'crime_rate_log_tor':'Toronto',
                                  'crime_rate_log_mon':'Montreal'})
    melt_data = pd.melt(data)
    melt_data = melt_data.dropna()

    # perform post hoc Tukey test
    posthoc = pairwise_tukeyhsd(melt_data.value, melt_data.variable,
                                alpha = 0.05)
    print(posthoc)

    # plotting
    fig = posthoc.plot_simultaneous()
    plt.savefig(output_dir / "residuals.png"'tukey_3_cities.png')
 

if __name__ == '__main__':
    main()
