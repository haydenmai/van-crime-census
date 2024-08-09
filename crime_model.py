# CMPT 353 - Final Project
# Authors: Benley Hsiang
#          April Nguyen
#          Gia Hue (Hayden) Mai
#   
# Description: Trains different models on the combined Vancouver, Toronto, and Montreal census data.
#              Prints the validation scores of each model, the feature importance values of the 
#              Random Forest model, and saves images of the feature importance plots. 
#              Crime data taken from the 
#                       Vancouver Police Department (2003-2024): https://geodash.vpd.ca/opendata/
#                       City of Montreal: https://donnees.montreal.ca/dataset/actes-criminels
#                       Toronto Police Service: https://data.torontopolice.on.ca/pages/5245ab054fed48758557597256227049
#              Canadian 2021 Census is obtain from the CensusMapper API in R: https://censusmapper.ca/api
#
# crime_model.py
# Last modified: July 31, 2024

import os
import pathlib
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.inspection import permutation_importance

OUTPUT_TEMPLATE = (                
    'Gaussian Regressor:           {gauss:.3f}\n'
    'kNN Regressor:                {kNN:.3f}\n'
    'Random Forest Regressor:      {rand_f:.3f}\n'
    'Gradient Boosting Regressor:  {grad_b:.3f}\n'
)

def main():
    # Reading the GeoJSON file
    input_dir = pathlib.Path('crime_census')
    vancouver = gpd.read_file(input_dir / 'crime_census_van.geojson')
    toronto = gpd.read_file(input_dir / 'crime_census_tor.geojson')
    montreal = gpd.read_file(input_dir / 'crime_census_mon.geojson')
        
    # Setting columns for vancouver data    
    X_van = vancouver[['pop_density', 'dropouts_to_grads', 'one_parent_to_two', 'crowded_to_not', 
                'children_to_adults', 'non_minority_to_minority', 'male_to_female',
                'divorce_rate', 'home_renters_to_owners', 'low_income_status_pct']]
    y_van = vancouver['crime_rate']
    
    # Setting columns for toronto data    
    X_tor = toronto[['pop_density', 'dropouts_to_grads', 'one_parent_to_two', 'crowded_to_not', 
                'children_to_adults', 'non_minority_to_minority', 'male_to_female',
                'divorce_rate', 'home_renters_to_owners', 'low_income_status_pct']]
    y_tor = toronto['crime_rate']
        
    # Setting columns for montreal data    
    X_mon = montreal[['pop_density', 'dropouts_to_grads', 'one_parent_to_two', 'crowded_to_not', 
                'children_to_adults', 'non_minority_to_minority', 'male_to_female',
                'divorce_rate', 'home_renters_to_owners', 'low_income_status_pct']]
    y_mon = montreal['crime_rate']

    # Partitioning the data
    X_train_van, X_valid_van, y_train_van, y_valid_van = train_test_split(X_van, y_van, train_size = 0.8) # Needs tweaking
    X_train_tor, X_valid_tor, y_train_tor, y_valid_tor = train_test_split(X_tor, y_tor, train_size = 0.8)
    X_train_mon, X_valid_mon, y_train_mon, y_valid_mon = train_test_split(X_mon, y_mon, train_size = 0.8)

    # Combining all cities' training data
    X_train_van_tor = pd.concat([X_train_van, X_train_tor])
    X_train_cities = pd.concat([X_train_van_tor, X_train_mon])
    
    y_train_van_tor = pd.concat([y_train_van, y_train_tor])
    y_train_cities = pd.concat([y_train_van_tor, y_train_mon])
    
    # Combining all cities' validation data
    X_valid_van_tor = pd.concat([X_valid_van, X_valid_tor])
    X_valid_cities = pd.concat([X_valid_van_tor, X_valid_mon])
    
    y_valid_van_tor = pd.concat([y_valid_van, y_valid_tor])
    y_valid_cities = pd.concat([y_valid_van_tor, y_valid_mon])
    
    # Gaussian Process Regressor
    gauss_model = make_pipeline(
        StandardScaler(), 
        GaussianProcessRegressor()
    )
    
    # k-Nearest Neighbors Regressor
    kNN_model = make_pipeline(
        StandardScaler(), 
        KNeighborsRegressor(n_neighbors = 6) # Needs tweaking
    )

    # Random Forest Regressor
    randforest_model = make_pipeline(
        StandardScaler(), 
        RandomForestRegressor(n_estimators = 400, max_depth = 15, min_samples_leaf = 10) # Needs tweaking
    )
    
    # Gradient boosting Regressor
    grad_boost_model = make_pipeline(
        StandardScaler(), 
        GradientBoostingRegressor(n_estimators = 300, max_depth = 15, min_samples_leaf = 10) # Needs tweaking
    )
    
    # Training the models
    models = [gauss_model, kNN_model, randforest_model, grad_boost_model]
    for i, model in enumerate(models):  
        model.fit(X_train_cities, y_train_cities)
        
    # Printing validation scores
    print('Validation scores:\n')
    print(OUTPUT_TEMPLATE.format(
        gauss = gauss_model.score(X_valid_cities, y_valid_cities),
        kNN = kNN_model.score(X_valid_cities, y_valid_cities),
        rand_f = randforest_model.score(X_valid_cities, y_valid_cities),
        grad_b = grad_boost_model.score(X_valid_cities, y_valid_cities),
    ))
    
    # Printing validation scores for Vancouver data
    print('\nValidating with Vancouver data:\n')
    print(OUTPUT_TEMPLATE.format(
        gauss = gauss_model.score(X_valid_van, y_valid_van),
        kNN = kNN_model.score(X_valid_van, y_valid_van),
        rand_f = randforest_model.score(X_valid_van, y_valid_van),
        grad_b = grad_boost_model.score(X_valid_van, y_valid_van),
    ))
    
    # Printing validation scores for Toronto data
    print('\nValidating with Toronto data:\n')
    print(OUTPUT_TEMPLATE.format(
        gauss = gauss_model.score(X_valid_tor, y_valid_tor),
        kNN = kNN_model.score(X_valid_tor, y_valid_tor),
        rand_f = randforest_model.score(X_valid_tor, y_valid_tor),
        grad_b = grad_boost_model.score(X_valid_tor, y_valid_tor),
    ))
        
    # Printing validation scores for Montreal data
    print('\nValidating with Montreal data:\n')
    print(OUTPUT_TEMPLATE.format(
        gauss = gauss_model.score(X_valid_mon, y_valid_mon),
        kNN = kNN_model.score(X_valid_mon, y_valid_mon),
        rand_f = randforest_model.score(X_valid_mon, y_valid_mon),
        grad_b = grad_boost_model.score(X_valid_mon, y_valid_mon),
    ))
    
    
    
    # FEATURE IMPORTANCE BASED ON FEATURE PERMUTATION 
    # https://scikit-learn.org/stable/modules/permutation_importance.html

    # Setting feature names
    feature_names = ['pop_density', 'dropouts_to_grads', 'one_parent_to_two', 'crowded_to_not', 
                'children_to_adults', 'non_minority_to_minority', 'male_to_female',
                'divorce_rate', 'home_renters_to_owners', 'low_income_status_pct']

    # Getting feature importance
    result = permutation_importance(
        randforest_model, X_valid_cities, y_valid_cities, n_repeats=10, random_state=42, n_jobs=2
    )

    # https://scikit-learn.org/stable/modules/permutation_importance.html
    print('\nFeature importance values:\n')
    for i in result.importances_mean.argsort()[::-1]:
        if result.importances_mean[i] - 2 * result.importances_std[i] > 0:
            print(f"{feature_names[i]:<8}"
                f"{result.importances_mean[i]:.3f}"
                f" +/- {result.importances_std[i]:.3f}")


    # Putting results into series to plot
    forest_importances = pd.Series(result.importances_mean, index=feature_names)

    # Plotting
    fig, ax = plt.subplots()
    forest_importances.plot.bar(yerr=result.importances_std, ax=ax)
    ax.set_title("Feature importances using permutation on full model")
    ax.set_ylabel("Mean accuracy decrease")
    fig.tight_layout()
    
    # Make a folder
    output_dir = pathlib.Path('feature_importance')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(output_dir/'feat_imp_perm.png')
    
    
    
    # FEATURE IMPORTANCE BASED ON MEAN DECREASE IN IMPURITY
    # https://scikit-learn.org/stable/modules/permutation_importance.html
    
    # Getting feature importance
    importances = randforest_model.named_steps['randomforestregressor'].feature_importances_

    # Calculating standard deviation
    std = np.std([tree.feature_importances_ for tree in randforest_model.named_steps['randomforestregressor'].estimators_], axis=0)

    # Putting into a series to plot
    forest_importances = pd.Series(importances, index=feature_names)

    # Plotting
    fig, ax = plt.subplots()
    forest_importances.plot.bar(yerr=std, ax=ax)
    ax.set_title("Feature importances using MDI")
    ax.set_ylabel("Mean decrease in impurity")
    fig.tight_layout()
    plt.savefig(output_dir/'feat_imp_mean_dec.png')
    

if __name__ == '__main__':
    main()
