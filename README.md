# CMPT 353 Project - Vancouver Crime Rates
A project done by April Nguyen, Benley Hsiang, and Hayden Mai for CMPT 353: Computational Data Science at SFU.

This project explores the effect of socioeconomic factors on the number of crimes in Vancouver as well as investigating the possibility of modelling other urban cities using Vancouver’s population demographics.

## Requirements
To run this project from start to finish, you will need:
- [Python 3.10](https://www.python.org/downloads/)
- [R (4.3.3 or higher)](https://mirror.rcg.sfu.ca/mirror/CRAN/)

## Running The Project
The following files are needed for/generated during this project:
- The 3 `crimedata_xxx.zip` inside of `datasets`. 
    - Contains police records of crimes in Vancouver, Toronto, and Montreal.
- The 3 `censusdata_xxx.geojson` either generated in **Step 1** [using R](https://mirror.rcg.sfu.ca/mirror/CRAN/) or extracted from `censusdata.zip`. 
    - These files are generated/located in `datasets` as well. 
    - Contains 2021 Census data from Statistics Canada for Vancouver, Toronto, and Montreal.
- The 3 `crime_census_xxx.geojson` generated in the `crime_census` folder by running `data_processing.py` in **Step 2** 
    - This is the combined crime and census datasets for each city.
- `vancouver.geojson` in `datasets` folder is used for `vancouver_crime_map.py`, which will generate a choropleth in HTML of Vancouver.

### 1. Retrieving Data From R
First, we will need census datasets. To run `get_census.R` to obtain the 3 `censusdata_xxx.geojson`, run the following in RGui (or R 4.3.3) application.

**Note**: You need to set your working directory using `setwd(C:/Users/...)` before running this code, you can use `getwd()` to check if you are in the project's folder.
```R
install.packages("cancensus")
install.packages("sf")
source('get_census.R')
```

That should create 3 new files (`censusdata_xxx.geojson`) in `datasets`, assuming that `setwd()` was used.

If the Censusmapper API is unavailable, the `censusdata.zip` inside `datasets` will contain the 3 necessary census datasets for this project after unzipping. The 3 `censusdata_xxx.geojson` files should be inserted into `datasets` when extracted.

### 2. Processing Data in Python
After obtaining the data from R, we can then move to Python for data cleaning and analysis.

The following libraries are needed:
- pandas
- numpy
- geopandas
- shapely
- matplotlib
- folium
- seaborn
- pathlib
- scipy
- scikit-learn

Which can be done through the terminal:
```
pip install --user pandas numpy geopandas shapely matplotlib folium seaborn pathlib scipy scikit-learn
```

`data_processing.py` can now run in the terminal:
```
python3 data_processing.py
```

This will take a moment (about 1-2 minutes) to combine `crimedata_xxx.zip` with `censusdata_xxx.geojson` and output 3 more files (`crime_census_xxx.geojson`) in `crime_census` folder which are used for all of the other python files.

### 3. Analysis
After running `data_processing.py`, you can now run `initial_plots.py`, `stat_analysis.py`, `vancouver_crime_map.py`, and `crime_model.py` in any order.
```
python3 initial_plots.py
python3 stats_analysis.py
python3 vancouver_crime_map.py
python3 crime_model.py
```
#### Expected Outputs
- ##### `initial_plots.py`
    - In `initial_plot/van` folder:
        - histogram of vancouver log(crime_rate)
        - boxplot of vancouver log(crime rate)
        - scatter plots of crime_rate vs all other features with linear regression
        - scatter plots of log(crime_rate) vs all other features with linear regression
        - histogram of residuals of log(crime_rate) vs all other features
        - txt file with information from the linear regression

- ##### `stat_analysis.py`
    - On the terminal:
        - OLS Regression Results
        - p-value of normality test on the residuals
        - p-value of normality tests on log(crime_rate)
        - p-value of ANOVA test of 3 cities
    - In `stats_analysis` folder:
        - residuals histogram `residuals.png` 
        - Tukey's HSD comparisons saved as `tukey_3_cities.png`

- ##### `vancouver_crime_map.py`
    - A choropleth map of crime count in Vancouver `vancouver_crime_map.html`

- ##### `crime_model.py`
    - On the terminal:
        - Validation scores for the combined data
        - Validation scores for each city
        - Feature importance values
    - In the folder `feature_importance`:
        - Feature importance based on MDI saved as `feat_imp_mean_dec.png`
        - Feature importance based on permutation saved as `feat_imp_perm.png`
---
## Understanding The Project
That's it! To further understand the use of these data and code, `Final_Project_Report.pdf` is provided as an in-depth explanation of our methods and findings for this project.
