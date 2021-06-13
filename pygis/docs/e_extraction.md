---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
html_meta:
  "description lang=en": "Learn how to subset and extract data from a GeoDataFrame through clipping, selecting by attribute, and selecting by location."
  "keywords": "geospatial, attribute data, subset, extract, selection, vector, shapefile"
  "property=og:locale": "en_US"
---

----------------

```{admonition} Learning Objectives
* Clip a vector feature using another vector feature
* Select features by their attributes
* Select features by their locations
```
```{admonition} Review
* [Geospatial Vector Data](c_vectors.md)
* [Attributes & Indexing for Vector Data](e_attributes.md)
* [Creating Geospatial Vector Data](e_new_vectors.md)
```
----------------

# Extracting Spatial Data

Subsetting and extracting data is useful when we want to select or analyze a portion of the dataset based on a feature's location, attribute, or its spatial relationship to another dataset.

In this chapter, we will explore three ways that data from a GeoDataFrame can be subsetted and extracted: clip, select by attribute, and select by location.

## Setup

First, let's import the necessary modules.

```{code-cell} ipython3
# Import modules
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Polygon
```

We will utilize shapefiles of San Francisco Bay Area county boundaries and wells within the Bay Area and the surrounding 50 km. We will first load in the data and reproject the data.

```{important} All the data must have the same coordinate system in order for extraction to work correctly.
```

```{code-cell} ipython3
# Load data

# County boundaries
# Source: https://opendata.mtc.ca.gov/datasets/san-francisco-bay-region-counties-clipped?geometry=-125.590%2C37.123%2C-119.152%2C38.640
counties = gpd.read_file("../_static/e_vector_shapefiles/sf_bay_counties/sf_bay_counties.shp")

# Well locations
# Source: https://gis.data.ca.gov/datasets/3a3e681b894644a9a95f9815aeeeb57f_0?geometry=-123.143%2C36.405%2C-119.230%2C37.175
# Modified by author so that only the well locations within the counties and the surrounding 50 km were kept
wells = gpd.read_file("../_static/e_vector_shapefiles/sf_bay_wells_50km/sf_bay_wells_50km.shp")

# Reproject data to NAD83(HARN) / California Zone 3
# https://spatialreference.org/ref/epsg/2768/
proj = 2768
counties = counties.to_crs(proj)
wells = wells.to_crs(proj)
```

We will also create a rectangle over a part of the Bay Area. We have identified coordinates to use for this rectangle, but you can also use [bbox finder](http://bboxfinder.com/) to generate custom bounding boxes and obtain their coordinates.

```{code-cell} ipython3
# Create list of coordindate pairs
coordinates = [[1790787, 736108], [1929652, 736108], [1929652, 598414], [1790787, 598414]]

# Create a Shapely polygon from the coordinate-tuple list
poly_shapely = Polygon(coordinates)

# Create a dictionary with needed attributes and required geometry column
attributes_df = {'Attribute': ['name1'], 'geometry': poly_shapely}

# Convert shapely object to a GeoDataFrame
poly = gpd.GeoDataFrame(attributes_df, geometry = 'geometry', crs = "EPSG:2768")
```

We'll define some functions to make displaying and mapping our results a bit easier.

```{code-cell} ipython3
def display_table(table_name, attribute_table):
    '''Display the first and last five rows of attribute table.'''

    # Print title
    print("Attribute Table: {}".format(table_name))

    # Print number of rows and columns
    print("\nTable shape (rows, columns): {}".format(attribute_table.shape))

    # Display first five rows of attribute table
    print("\nFirst five rows:")
    display(attribute_table.head())

    # Display last five rows of attribute table
    print("\nLast five rows:")
    display(attribute_table.tail())


def plot_df(result_name, result_df, result_geom_type, area = None):
    '''Plot the result on a map and add the outlines of the original shapefiles.'''

    # Create subplots
    fig, ax = plt.subplots(1, 1, figsize = (10, 10))

    # Plot data depending on vector type
    # For points
    if result_geom_type == "point":

        # Plot data
        counties.plot(ax = ax, color = 'none', edgecolor = 'dimgray')
        wells.plot(ax = ax, marker = 'o', color = 'dimgray', markersize = 3)
        result_df.plot(ax = ax, marker = 'o', color = 'dodgerblue', markersize = 3)

    # For polygons
    else:

        # Plot overlay data
        result_df.plot(ax = ax, cmap = 'Set2', edgecolor = 'black')

        # Plot outlines of original shapefiles
        counties.plot(ax = ax, color = 'none', edgecolor = 'dimgray')

    # Add additional outlined boundary if specified
    if area is not None:

        # Plot data
        area.plot(ax = ax, color = 'none', edgecolor = 'lightseagreen', linewidth = 3)

    # Else, pass
    else:
        pass

    # Stylize plots
    plt.style.use('bmh')

    # Set title
    ax.set_title(result_name, fontdict = {'fontsize': '15', 'fontweight' : '3'})
```

Let's take a look at what our input data looks like.

```{code-cell} ipython3
# Create subplots
fig, ax = plt.subplots(1, 1, figsize = (10, 10))

# Plot data
counties.plot(ax = ax, color = 'bisque', edgecolor = 'dimgray')
wells.plot(ax = ax, marker = 'o', color = 'dodgerblue', markersize = 3)
poly.plot(ax = ax, color = 'aquamarine', edgecolor = 'lightseagreen', alpha = 0.55)

# Stylize plots
plt.style.use('bmh')

# Set title
ax.set_title('San Francisco Bay Area', fontdict = {'fontsize': '15', 'fontweight' : '3'})
```

## Clip

Clip extracts and keeps only the geometries of a vector feature that are within extent of another vector feature (think of it like a cookie-cutter or mask). We can use  `clip()` in `geopandas`, with the first parameter being the vector that will be clipped and the second parameter being the vector that will define the extent of the clip. All attributes for the resulting clipped vector will be kept.

```{note}
This function is only available in the more recent versions of `geopandas`.
```

Source: [Clip Vector Data with GeoPandas, GeoPandas](https://geopandas.org/gallery/plot_clip.html)

We will first clip the Bay Area counties polygon to our created rectangle polygon.

```{code-cell} ipython3
# Clip data
clip_counties = gpd.clip(counties, poly)

# Display attribute table
display(clip_counties)

# Plot clip
plot_df(result_name = "San Francisco Bay Area Counties\nClip", result_df = clip_counties, result_geom_type = "polygon", area = poly)
```

We can clip any vector type. Next, we will clip the wells point data to our created rectangle polygon.

```{code-cell} ipython3
# Clip data
clip_wells = gpd.clip(wells, poly)

# Display attribute table
display(clip_wells)

# Plot clip
plot_df(result_name = "San Francisco Bay Area Wells\nClip", result_df = clip_wells, result_geom_type = "point", area = poly)
```

## Select by Attribute

Selecting by attribute selects only the features in a dataset whose attribute values match the specified criteria. `geopandas` uses the indexing and selection methods in `pandas`, so data in a GeoDataFrame can be selected and queried in the same way a `pandas` dataframe can.

Sources: [Indexing and Selecting Data, GeoPandas](https://geopandas.org/docs/user_guide/indexing.html); [Indexing and selecting data, pandas](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html); [How do I select a subset of a DataFrame?, pandas](https://pandas.pydata.org/pandas-docs/stable/getting_started/intro_tutorials/03_subset_data.html)

We will use use different criteria to subset the wells dataset.

```{code-cell} ipython3
# Display attribute table
display(wells)
```

The criteria can use a variety of operators, including comparison and logical operators.

```{code-cell} ipython3
# Select wells that are public supply
wells_subset_1 = wells[(wells["WELL_USE"] == "Public Supply")]

# Display first five and last five rows of attribute table
display_table(table_name = "San Francisco Bay Area Wells - Public Supply", attribute_table = wells_subset_1)
```

```{code-cell} ipython3
# Select wells that are public supply and have a depth greater than 50 ft
wells_subset_2 = wells[(wells["WELL_USE"] == "Public Supply") & (wells["WELL_DEPTH"] > 50)]

# Display first five and last five rows of attribute table
display_table(table_name = "San Francisco Bay Area Wells - Public Supply with Depth Greater than 50 ft", attribute_table = wells_subset_2)
```

```{code-cell} ipython3
# Select wells that are public supply and have a depth greater than 50 ft OR are residential
wells_subset_3 = wells[((wells["WELL_USE"] == "Public Supply") & (wells["WELL_DEPTH"] > 50)) | (wells["WELL_USE"] == "Residential")]

# Display first five and last five rows of attribute table
display_table(table_name = "San Francisco Bay Area Wells - Public Supply with Depth Greater than 50 ft or Residential", attribute_table = wells_subset_3)
```

## Select by Location

Selecting by location selects features based on its relative spatial relationship with another dataset.

There are multiple spatial relationships available in `geopandas`.

| Spatial Relationship | Function(s) |
| :------------ | ---------------------------------------: |
| contains | `contains()` |
| covers | `covers()` |
| covered by | `covered_by()` |
| crosses | `crosses()` |
| disjoint | `disjoint()` |
| equal geometry | `geom_equals()`, `geom_almost_equals()`, `geom_equals_exact()` |
| intersects | `intersects()` |
| overlaps | `overlaps()` |
| touches | `touches()` |
| within | `within()` |

Source: [GeoSeries - Binary Predicates, GeoPandas](https://geopandas.org/docs/reference/geoseries.html#binary-predicates)

The functions for these spatial relationships will generally output a `pandas` series with Boolean values (`True` or `False`) whose indexing corresponds with the input dataset (from where we want to subset the data). We can use these Boolean values to subset the dataset (only the rows that have a `True` output will be retained).

These functions can be used to select features that have the specified spatial relationship with a single Shapely vector.

```{code-cell} ipython3
# Select wells that fall within Shapely rectangle
wells_location_subset_1 = wells[wells.within(poly_shapely)]

# Display first five and last five rows of attribute table
display_table(table_name = "San Francisco Bay Area Wells within a User-Defined Rectangle", attribute_table = wells_location_subset_1)

# Plot selection
plot_df(result_name = "San Francisco Bay Area Wells within a User-Defined Rectangle", result_df = wells_location_subset_1, result_geom_type = "point", area = poly)
```

If we're trying to select features that have a specified spatial relationship with another `geopandas` object, it gets a little tricky. This is because the `geopandas` spatial relationship functions verify the spatial relationship either row by row or index by index. In other words, the first row in the first dataset will be compared with the corresponding row or index in the second dataset, the second row in the first dataset will be compared with the corresponding row or index in the second dataset, and so on.

As a result, the number of rows need to correspond or the indices numbers need to match between the two datasets--or else we'll get a warning and the output will be empty.

Not easy if we want to check a bunch of features against one extent (with one geometry)... Fortunately, there are two workarounds that get the same result.

Source: [geopandas.GeoSeries.within, GeoPandas](https://geopandas.org/docs/reference/api/geopandas.GeoSeries.within.html)

### Workaround 1 - Manipulate extent GeoDataFrame

The first workaround copies the extent GeoDataFrame multiple times so that the number of rows (all with the exact same geometry) matches the number of rows in the GeoDataFrame in which we're selecting features.

```{code-cell} ipython3
# Select the Santa Clara County boundary
sc_county = counties[counties["coname"] == "Santa Clara County"]

# Multiply the boundary dataset by the number of rows in the wells dataset, and concatenate all the boundary datasets together into one dataframe
sc_county_replicate_df = pd.concat([sc_county] * wells.shape[0], ignore_index = True)

# Create a GeoDataFrame from the county dataframe
sc_county_replicate_gdf = gpd.GeoDataFrame(sc_county_replicate_df)

# Subset the GeoDataFrame by checking which wells are within Santa Clara County
wells_location_subset_2 = wells[wells.within(sc_county_replicate_gdf)]

# Display first five and last five rows of attribute table
display_table(table_name = "San Francisco Bay Area Wells within Santa Clara County", attribute_table = wells_location_subset_2)

# Plot selection
plot_df(result_name = "San Francisco Bay Area Wells within Santa Clara County", result_df = wells_location_subset_2, result_geom_type = "point", area = sc_county)
```

### Workaround 2 - Iterate through each feature

The second workaround iterates through each row of the GeoDataFrame from which we're selecting features, comparing each row/feature one at a time with the extent GeoDataFrame.

```{code-cell} ipython3
# Create copy of Santa Clara County boundary
sc_county_reset = sc_county.copy()

# Reset index of copied dataset (to 0)
sc_county_reset = sc_county_reset.reset_index(drop = True)

# Create empty list to hold Boolean values indicating if spatial relationship is met
criteria_met_list = []

# Iterate through each feature in wells dataset
for i in range(0, wells.shape[0]):

    # Get a well point by index
    well = wells.iloc[[i]]

    # Reset index of well point (to 0) to match the index-reset Santa Clara County boundary
    well = well.reset_index(drop = True)

    # Check if well is within Santa Clara County
    criteria_met = well.within(sc_county_reset)[0]

    # If criteria is met (True), append True to list
    if criteria_met:
        criteria_met_list.append(True)

    # Otherwise, criteria is not met (False), and append False to list
    else:
        criteria_met_list.append(False)

# Subset data based on the list of Boolean values
wells_location_subset_3 = wells[criteria_met_list]

# Display first five and last five rows of attribute table
display_table(table_name = "San Francisco Bay Area Wells within Santa Clara County", attribute_table = wells_location_subset_3)
```
