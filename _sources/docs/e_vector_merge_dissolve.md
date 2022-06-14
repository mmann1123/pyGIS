---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.12
    jupytext_version: 1.8.2
kernelspec:
  display_name: 'Python 3.7.10 64-bit (''pygisbookgw'': conda)'
  name: python371064bitpygisbookgwconda0513153e7d7b4503839be1e6673bfbb2
html_meta:
  "description lang=en": "Learn how to merge new data into a shapefiles attribute table, dissolve polygons by attributes, and other group-by operations in geopandas."
  "description lang=fr": "Découvrez comment fusionner de nouvelles données dans une table attributaire de fichiers de formes, dissoudre des polygones par attributs et d'autres opérations de regroupement dans les géopandas."
  "description lang=es": "Aprenda a fusionar nuevos datos en una tabla de atributos de shapefiles, disolver polígonos por atributos y otras operaciones de agrupamiento en geopandas."
  "keywords": "python, spatial, polygon,vector,  shapefile, dissolve by attributes, merge attributes"
  "property=og:locale": "en_US"
---

# Merge Data & Dissolve Polygons

By: Steven Chao

---------------
```{admonition} Learning Objectives
* Import dataframes into Python for analysis
* Perform basic dataframe column operations
* Merge dataframes using a unique key
* Group attributes based on a similar attribute
* Dissolve vector geometries based on attribute values
```
```{admonition} Review
* [Data Structures](c_features.md)
* [Vector Data ](c_vectors.md)
```
--------------

## Introduction

Dataframes are widely used in Python for manipulating data. Recall that a dataframe is essentially an Excel spreadsheet (a 2-D table of rows and columns); in fact, many of the functions that you might use in Excel can often be replicated when working with dataframes in Python!

This chapter will introduce you to some of the basic operations that you can perform on dataframes. We will use these basic operations in order to calculate and map poverty rates in the Commonwealth of Virginia. We will pull data from the US Census Bureau's [American Community Survey (ACS)](https://www.census.gov/programs-surveys/acs) 2019 (see [this page](https://www.census.gov/data/developers/data-sets/acs-5year.html) for the data).

```{code-cell} ipython3
# Import modules
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from census import Census
from us import states
```


## Accessing Data

### Import census data

Let's begin by accessing and importing census data. Importing census data into Python requires a Census API key. A key can be obtained from [Census API Key](http://api.census.gov/data/key_signup.html).  **It will provide you with a unique 40 digit text string. Please keep track of this number. Store it in a safe place.**

```{code-cell} ipython3
:tags: ["remove-output"]
# Set API key
c = Census("CENSUS API KEY HERE")
```

```{code-cell} ipython3
:tags: ["hide-cell"]
#ignore this, I am just reading in my api key privately
with open("../../../census_api.txt", "r") as f:
    c = Census(f.read().replace('\n', ''))
```

With the Census API key set, we will access the census data at the tract level for the Commonwealth of Virginia from the 2019 ACS, specifically the `ratio of income to poverty in the past 12 months` (`C17002_001E`, total; `C17002_002E`, < 0.50; and `C17002_003E`, 0.50 - 0.99) variables and the `total population` (`B01003_001E`) variable. For more information on why these variables are used, refer to the US Census Bureau's [article on how the Census Bureau measures poverty](https://www.census.gov/topics/income-poverty/poverty/guidance/poverty-measures.html) and the [list of variables found in ACS](https://api.census.gov/data/2019/acs/acs5/variables.html).

The `census` package provides us with some easy convenience methods that allow us to obtain data for a wide variety of geographies. The FIPS code for Virginia is 51, but if needed, we can also use the `us` library to help us figure out the relevant FIPS code.

```{code-cell} ipython3
# Obtain Census variables from the 2019 ACS at the tract level for the Commonwealth of Virginia (FIPS code: 51)
# C17002_001E: count of ratio of income to poverty in the past 12 months (total)
# C17002_002E: count of ratio of income to poverty in the past 12 months (< 0.50)
# C17002_003E: count of ratio of income to poverty in the past 12 months (0.50 - 0.99)
# B01003_001E: total population
# Sources: https://api.census.gov/data/2019/acs/acs5/variables.html; https://pypi.org/project/census/
va_census = c.acs5.state_county_tract(fields = ('NAME', 'C17002_001E', 'C17002_002E', 'C17002_003E', 'B01003_001E'),
                                      state_fips = states.VA.fips,
                                      county_fips = "*",
                                      tract = "*",
                                      year = 2017)
```

Now that we have accessed the data and assigned it to a variable, we can read the data into a dataframe using the `pandas` library.

```{code-cell} ipython3
# Create a dataframe from the census data
va_df = pd.DataFrame(va_census)

# Show the dataframe
print(va_df.head(2))
print('Shape: ', va_df.shape)
```

By showing the dataframe, we can see that there are 1907 rows (therefore 1907 census tracts) and 8 columns.

### Import Shapefile

Let's also read into Python a shapefile of the Virginia census tracts and reproject it to the UTM Zone 17N projection. (This shapefile can be downloaded on the Census Bureau's website on the [Cartographic Boundary Files page](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html) or the [TIGER/Line Shapefiles page](https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html).)

```{code-cell} ipython3
# Access shapefile of Virginia census tracts
va_tract = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2019/TRACT/tl_2019_51_tract.zip")

# Reproject shapefile to UTM Zone 17N
# https://spatialreference.org/ref/epsg/wgs-84-utm-zone-17n/
va_tract = va_tract.to_crs(epsg = 32617)

# Print GeoDataFrame of shapefile
print(va_tract.head(2))
print('Shape: ', va_tract.shape)

# Check shapefile projection
print("\nThe shapefile projection is: {}".format(va_tract.crs))
```

By printing the shapefile, we can see that the shapefile also has 1907 rows (1907 tracts). This number matches with the number of census records that we have on file. Perfect!

Not so fast, though. We have a potential problem: We have the census data, and we have the shapefile of census tracts that correspond with that data, but they are stored in two separate variables (`va_df` and `va_tract` respectively)! That makes it a bit difficult to map since these two separate datasets aren't connected to each other.

## Performing Dataframe Operations

### Create new column from old columns to get combined FIPS code

To solve this problem, we can join the two dataframes together via a field or column that is common to both dataframes, which is referred to as a key.

Looking at the two datasets above, it appears that the `GEOID` column from `va_tract` and the `state`, `county`, and `tract` columns combined from `va_df` could serve as the unique key for joining these two dataframes together. In their current forms, this join will not be successful, as we'll need to merge the `state`, `county`, and `tract` columns from `va_df` together to make it parallel to the `GEOID` column from `va_tract`. We can simply add the columns together, much like math or the basic operators in Python, and assign the "sum" to a new column.

To create a new column--or call an existing column in a dataframe--we can use indexing with `[]` and the column name (string). (There is a different way if you want to access columns using the index number; read more about indexing and selecting data [in the pandas documentation](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html).)

```{code-cell} ipython3
# Combine state, county, and tract columns together to create a new string and assign to new column
va_df["GEOID"] = va_df["state"] + va_df["county"] + va_df["tract"]
```

Printing out the first rew rows of the dataframe, we can see that the new column `GEOID` has been created with the values from the three columns combined.

```{code-cell} ipython3
# Print head of dataframe
va_df.head(2)
```

### Remove dataframe columns that are no longer needed

To reduce clutter, we can delete the `state`, `county`, and `tract` columns from `va_df` since we don't need them anymore. Remember that when we want to modify a dataframe, we must assign the modified dataframe back to the original variable (or a new one, if preferred). Otherwise, any modifications won't be saved. An alternative to assigning the dataframe back to the variable is to simply pass `inplace = True`. For more information, see the [pandas help documentation on `drop`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.drop.html).

```{code-cell} ipython3
# Remove columns
va_df = va_df.drop(columns = ["state", "county", "tract"])

# Show updated dataframe
va_df.head(2)
```

### Check column data types

The key in both dataframe must be of the same data type. Let's check the data type of the `GEOID` columns in both dataframes. If they aren't the same, we will have to change the data type of columns to make them the same.

```{code-cell} ipython3
# Check column data types for census data
print("Column data types for census data:\n{}".format(va_df.dtypes))

# Check column data types for census shapefile
print("\nColumn data types for census shapefile:\n{}".format(va_tract.dtypes))

# Source: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dtypes.html
```

Looks like the `GEOID` columns are the same!

### Merge dataframes

Now, we are ready to merge the two dataframes together, using the `GEOID` columns as the primary key. We can use the `merge` method in `GeoPandas` called on the `va_tract` shapefile dataset.

```{code-cell} ipython3
# Join the attributes of the dataframes together
# Source: https://geopandas.org/docs/user_guide/mergingdata.html
va_merge = va_tract.merge(va_df, on = "GEOID")

# Show result
print(va_merge.head(2))
print('Shape: ', va_merge.shape)
```

Success! We still have 1907 rows, which means that all rows (or most of them) were successfully matched! Notice how the census data has been added on after the shapefile data in the dataframe.

Some additional notes about joining dataframes:
* the columns for the key do not need to have the same name.
* for this join, we had a one-to-one relationship, meaning one attribute in one dataframe matched to one (and only one) attribute in the other dataframe. Joins with a many-to-one, one-to-many, or many-to-many relationship are also possible, but in some cases, they require some special considerations. See this [Esri ArcGIS help documentation on joins and relates](https://desktop.arcgis.com/en/arcmap/10.3/manage-data/tables/about-joining-and-relating-tables.htm) for more information.

### Subset dataframe

Now that we merged the dataframes together, we can further clean up the dataframe and remove columns that are not needed. Instead of using the `drop` method, we can simply select the columns we want to keep and create a new dataframe with those selected columns.

```{code-cell} ipython3
# Create new dataframe from select columns
va_poverty_tract = va_merge[["STATEFP", "COUNTYFP", "TRACTCE", "GEOID", "geometry", "C17002_001E", "C17002_002E", "C17002_003E", "B01003_001E"]]

# Show dataframe
print(va_poverty_tract.head(2))
print('Shape: ', va_poverty_tract.shape)
```

Notice how the number of columns dropped from 13 to 9.

### Dissolve geometries and get summarized statistics to get poverty statistics at the county level

Next, we will group all the census tracts within the same county (`COUNTYFP`) and aggregate the poverty and population values for those tracts within the same county. We can use the `dissolve` function in `GeoPandas`, which is the spatial version of `groupby` in `pandas`. We use `dissolve` instead of `groupby` because the former also groups and merges all the geometries (in this case, census tracts) within a given group (in this case, counties).

```{code-cell} ipython3
# Dissolve and group the census tracts within each county and aggregate all the values together
# Source: https://geopandas.org/docs/user_guide/aggregation_with_dissolve.html
va_poverty_county = va_poverty_tract.dissolve(by = 'COUNTYFP', aggfunc = 'sum')

# Show dataframe
print(va_poverty_county.head(2))
print('Shape: ', va_poverty_county.shape)
```

Notice that we got the number of rows down from 1907 to 133.

### Perform column math to get poverty rates

We can estimate the poverty rate by dividing the sum of `C17002_002E` (ratio of income to poverty in the past 12 months, < 0.50) and `C17002_003E` (ratio of income to poverty in the past 12 months, 0.50 - 0.99) by `B01003_001E` (total population).

Side note: Notice that `C17002_001E` (ratio of income to poverty in the past 12 months, total), which theoretically should count everyone, does not exactly match up with `B01003_001E` (total population). We'll disregard this for now since the difference is not too significant.

```{code-cell} ipython3
# Get poverty rate and store values in new column
va_poverty_county["Poverty_Rate"] = (va_poverty_county["C17002_002E"] + va_poverty_county["C17002_003E"]) / va_poverty_county["B01003_001E"] * 100

# Show dataframe
va_poverty_county.head(2)
```

## Plotting Results

Finally, since we have the spatial component connected to our census data, we can plot the results!

```{code-cell} ipython3
# Create subplots
fig, ax = plt.subplots(1, 1, figsize = (20, 10))

# Plot data
# Source: https://geopandas.readthedocs.io/en/latest/docs/user_guide/mapping.html
va_poverty_county.plot(column = "Poverty_Rate",
                       ax = ax,
                       cmap = "RdPu",
                       legend = True)

# Stylize plots
plt.style.use('bmh')

# Set title
ax.set_title('Poverty Rates (%) in Virginia', fontdict = {'fontsize': '25', 'fontweight' : '3'})
```
 