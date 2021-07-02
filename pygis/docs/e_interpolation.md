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
  "description lang=en": "Learn how to interpolate data."
  "keywords": "geospatial, interpolation, vector, shapefile"
  "property=og:locale": "en_US"
---

----------------

```{admonition} Learning Objectives
* Conduct various types of interpolation on point dataset
* Obtain interpolated values at specified unsampled locations
```
```{admonition} Review
* [Geospatial Vector Data](c_vectors.md)
* [Attributes & Indexing for Vector Data](e_attributes.md)
* [Creating Geospatial Vector Data](e_new_vectors.md)
* [Merge Data & Dissolve Polygons](e_vector_merge_dissolve.md)
```

----------------

# Interpolation

Interpolation is the process of using locations with known, sampled values (of a phenomenon) to estimate the values at unknown, unsampled areas. [^bolstad]

In this chapter, we will explore three interpolation methods: Thiessen polygons (Voronoi diagrams), k-nearest neighbors (KNN), and kriging.

We will first begin by importing modules (click the + below to show code cell).

```{code-cell} ipython3
:tags: [hide-cell]

# Import modules
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pykrige.ok import OrdinaryKriging
import random
import rasterio
import rasterio.mask
from rasterio.plot import show
from rasterio.transform import Affine
from scipy.spatial import Voronoi, voronoi_plot_2d
from shapely.geometry import Polygon, Point
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor
```

We will utilize shapefiles of San Francisco Bay Area county boundaries and rainfall "values" that were "sampled" in the Bay Area. We will load in the data and reproject the data (click the + below to show code cell).

```{code-cell} ipython3
:tags: [hide-cell]

# Load data

# County boundaries
# Source: https://opendata.mtc.ca.gov/datasets/san-francisco-bay-region-counties-clipped?geometry=-125.590%2C37.123%2C-119.152%2C38.640
counties = gpd.read_file("../_static/e_vector_shapefiles/sf_bay_counties/sf_bay_counties.shp")

# Rainfall measurement "locations"
# Source: https://earthworks.stanford.edu/catalog/stanford-td754wr4701
# Modified by author by clipping raster to San Francisco Bay Area, generating random points, and extracting raster values (0-255) to the points
rainfall = gpd.read_file("../_static/e_vector_shapefiles/sf_bay_rainfall/sf_bay_rainfall.shp")

# Reproject data to WGS 84 UTM Zone 10N
# https://spatialreference.org/ref/epsg/wgs-84-utm-zone-10n/
proj = 32610
counties = counties.to_crs(proj)
rainfall = rainfall.to_crs(proj)
```

Next, we'll prepare the data for geoprocessing (click the + below to show code cell).

```{code-cell} ipython3
:tags: [hide-cell]

# Get X and Y coordinates of rainfall points
x_rain = rainfall["geometry"].x
y_rain = rainfall["geometry"].y

# Create list of XY coordinate pairs
coords_rain = [list(xy) for xy in zip(x_rain, y_rain)]

# Get minimum and maximum coordinate values of rainfall points
min_x_rain, min_y_rain, max_x_rain, max_y_rain = rainfall.total_bounds

# Get extent of counties feature
min_x_counties, min_y_counties, max_x_counties, max_y_counties = counties.total_bounds

# Get list of rainfall "values"
value_rain = list(rainfall["VALUE"])

# Create a copy of counties dataset
counties_dissolved = counties.copy()

# Add a field with constant value of 1
counties_dissolved["constant"] = 1

# Dissolve all counties to create one polygon
counties_dissolved = counties_dissolved.dissolve(by = "constant").reset_index(drop = True)
```

We will also define a function for exporting rasters.

```{code-cell} ipython3
def export_kde_raster(Z, XX, YY, min_x, max_x, min_y, max_y, proj, filename):
    '''Export and save a kernel density raster.'''

    # Get resolution
    xres = (max_x - min_x) / len(XX)
    yres = (max_y - min_y) / len(YY)

    # Set transform
    transform = Affine.translation(min_x - xres / 2, min_y - yres / 2) * Affine.scale(xres, yres)

    # Export array as raster
    with rasterio.open(
            filename,
            mode = "w",
            driver = "GTiff",
            height = Z.shape[0],
            width = Z.shape[1],
            count = 1,
            dtype = Z.dtype,
            crs = proj,
            transform = transform,
    ) as new_dataset:
            new_dataset.write(Z, 1)
```

With any model used for prediction, it is important to assess the model fit for unknown points (or the accuracy of the values predicted by the model in relation to their actual true values, which we may not even know). Thus, in order to assess the fit, we can set aside a portion of our dataset--this portion will not be "seen" by the model (in other words, it will not be used to build the model). Instead, we can use this "unseen" subsetted data to validate or test the model since we know what their actual true values are (and we can compare it to the values that the model predicts). The other portion will be used to build the model.

We will separate our rainfall dataset into two subsets: one for training and the other for testing. These subsets will be used in our KNN and kriging analyses.

```{code-cell} ipython3
# Split data into testing and training sets
coords_rain_train, coords_rain_test, value_rain_train, value_rain_test = train_test_split(coords_rain, value_rain, test_size = 0.33, random_state = 42)

# Create separate GeoDataFrames for testing and training sets
coords_rain_train_gdf = gpd.GeoDataFrame(geometry = [Point(x, y) for x, y in coords_rain_train], crs = proj)
coords_rain_test_gdf = gpd.GeoDataFrame(geometry = [Point(x, y) for x, y in coords_rain_test], crs = proj)
```

In addition to the testing dataset, we will also generate random unsampled points for which we will predict the values using each method (click the + below to show code cell). Unlike the previous testing dataset, we do not know the actual values for each data point.

```{code-cell} ipython3
:tags: [hide-cell]

# Set random seed
random.seed(10)

# Create empty lists
random_coords_list = [] # Hold randomly-generated coordinates
random_points_list = [] # Hold Point object of randomly-generated coordinates

# Create random points
# Number of random points created is specified by the number passed in 'range()'
for i in range(4):

    # Ensure randomly-generated points are within the counties boundary
    while True:

        # Generate random X and Y values
        random_x = random.uniform(min_x_counties, max_x_counties)
        random_y = random.uniform(min_y_counties, max_y_counties)

        # Create point from values
        random_point = [Point(random_x, random_y)]

        # Create a GeoDataFrame from point
        random_point_gdf = gpd.GeoDataFrame(random_point, columns = ['geometry'], crs = proj)

        # Check if point is within counties boundary
        if random_point_gdf.within(counties_dissolved)[0]:

            # If within, append coordinates and Point object to respective lists
            random_coords_list.append([random_x, random_y])
            random_points_list.append(random_point)

            # Break out of while loop
            break

        # If point not within, continue while loop
        else:
            pass

# Create GeoDataFrame holding all the random points
random_points = gpd.GeoDataFrame(random_points_list, columns = ['geometry'], crs = proj)
```

Plotting the randomly-generated points allows us to make sure the randomly-generated points are within our counties boundaries.

```{code-cell} ipython3
# Create subplots
fig, ax = plt.subplots(1, 1, figsize = (10, 10))

# Stylize plots
plt.style.use('bmh')

# Plot data
counties.plot(ax = ax, color = 'bisque', edgecolor = 'dimgray')
coords_rain_train_gdf.plot(ax = ax, marker = 'o', color = 'limegreen', markersize = 3)
coords_rain_test_gdf.plot(ax = ax, marker = 'o', color = 'royalblue', markersize = 3)
random_points.plot(ax = ax, marker = 'o', color = 'lightseagreen', markersize = 100)

# Set title
ax.set_title('San Francisco Bay Area - Rainfall Measurement Locations & Random Points', fontdict = {'fontsize': '15', 'fontweight' : '3'})
```

In the map above, the green and blue points are the rainfall points that we loaded separated into the training set and testing set, respectively. The large turquoise (blue-green) points are the random points that we generated.

## Thiessen Polygons (Voronoi Diagrams)

Thiessen polygons (also known as Voronoi diagrams) polygons allow us to perform nearest neighbor interpolation, which is perhaps the most basic type of interpolation. Thiessen polygons are be constructed around each sampled point so all the space within a specific polygon is closest in distance to that sampled point (as compared to other sampled points). Then, to perform nearest neighbor interpolation, all that space is assigned the value of that sampled point. [^bolstad]

We can use the [`scipy` package](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Voronoi.html) to create Thiessen polygons. After running the `Voronoi()` function, we can use the `vertices` attribute to get a list of vertices, which we can subsequently use to generate polygons.

```{attention} When creating Thiessen polygons, the sample points toward the edges of the point shapefile's extent will have infinite Voronoi regions, because not all sides of these edge points have adjacent sample points that would constrain the regions. Consequently, these infinite regions will not be exported. To mitigate this issue, we can create dummy points well beyond the extent of our datasets, which will create finite Voronoi regions for all of our actual sample points. Then, we can clip the regions to our extent shapefile (creating dummy points far away from our actual sample points will ensure the dummy points and their infinite Voronoi regions do not interfere with the sample points and their associated finite Voronoi regions after all regions are clipped).
```

```{code-cell} ipython3
# Extend extent of counties feature by using buffer
counties_buffer = counties.buffer(100000)

# Get extent of buffered input feature
min_x_cty_tp, min_y_cty_tp, max_x_cty_tp, max_y_cty_tp = counties_buffer.total_bounds

# Use extent to create dummy points and add them to list of coordinates
coords_tp = coords_rain + [[min_x_cty_tp, min_y_cty_tp], [max_x_cty_tp, min_y_cty_tp],
                           [max_x_cty_tp, max_y_cty_tp], [min_x_cty_tp, max_y_cty_tp]]

# Compute Voronoi diagram
tp = Voronoi(coords_tp)

# Create empty list of hold Voronoi polygons
tp_poly_list = []

# Create a polygon for each region
# 'regions' attribute provides a list of indices of the vertices (in the 'vertices' attribute) that make up the region
# Source: https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Voronoi.html
for region in tp.regions:

    # Ignore region if -1 is in the list (based on documentation)
    if -1 in region:

        # Return to top of loop
        continue

    # Otherwise, pass
    else:
        pass

    # Check that region list has values in it
    if len(region) != 0:

        # Create a polygon by using the region list to call the correct elements in the 'vertices' attribute
        tp_poly_region = Polygon(list(tp.vertices[region]))

        # Append polygon to list
        tp_poly_list.append(tp_poly_region)

    # If no values, return to top of loop
    else:
        continue

# Create GeoDataFrame from list of polygon regions
tp_polys = gpd.GeoDataFrame(tp_poly_list, columns = ['geometry'], crs = proj)

# Clip polygon regions to the counties boundary
tp_polys_clipped = gpd.clip(tp_polys, counties_dissolved)
```

A spatial join can be conducted to assign the rainfall "values" to its associated Thiessen polygon.

```{code-cell} ipython3
# If rainfall point within the polygon, assign that rainfall value to the polygon
tp_polys_clipped_values = gpd.sjoin(rainfall, tp_polys_clipped, how = "right", op = 'within')

# Drop un-needed column
tp_polys_clipped_values = tp_polys_clipped_values.drop("index_left", axis = 1)

# Rename column
tp_polys_clipped_values = tp_polys_clipped_values.rename(columns = {"VALUE": "VALUE_Predict"})

# Display head of attribute table
print("Attribute Table: Thiessen Polygon Interpolated Values")
display(tp_polys_clipped_values.head())
```

A second spatial join can be conducted to assign those values from the Thiessen polygons to the random points (only if a random point falls within a polygon).

```{code-cell} ipython3
# If random point is within a polygon, assign that polygon's value to the random point
random_points_tp = gpd.sjoin(random_points, tp_polys_clipped_values, how = "left", op = 'within')

# Drop un-needed column
random_points_tp = random_points_tp.drop("index_right", axis = 1)

# Rename column
random_points_tp = random_points_tp.rename(columns = {"VALUE": "VALUE_Predict"})

# Display attribute table
print("Attribute Table: Random Points Interpolated Values - Thiessen Polygon Method")
display(random_points_tp)
```

Plotting the data, we see that each polygon has one point (and vice-versa). All space within one polygon is closest to the known point (gray dot) within the polygon.

```{code-cell} ipython3
# Create subplots
fig, ax = plt.subplots(1, 1, figsize = (10, 10))

# Stylize plots
plt.style.use('bmh')

# Plot data
counties_dissolved.plot(ax = ax, color = 'none', edgecolor = 'dimgray')
tp_polys_clipped.plot(ax = ax, cmap = 'Set3', edgecolor = 'white', linewidth = 0.5)
rainfall.plot(ax = ax, marker = 'o', color = 'dimgray', markersize = 3)

# Set title
ax.set_title('San Francisco Bay Area - Rainfall Measurement Locations & Thiessen Polygons', fontdict = {'fontsize': '15', 'fontweight' : '3'})
```

In addition to `vertices`, there are a few other attributes we can call if we want to further explore the polygons. These attributes will provide actual values (e.g., vertices) or provide the indices for querying other attributes. [^scipy_voronoi]

In the example below, we demonstrate how to get the Thiessen polygon of one point. We use the `point_region` attribute to provide the index of a point's Voronoi region, and we use that index to get the region in `regions`. That provides indices of the vertices that make up the polygon, which we use to get the appropriate values in `vertices`.

```{code-cell} ipython3
# Set index for feature of interest
feature_index_one = 5

# Get a Voronoi polygon for one feature
# 'point_region' attribute provides the index of the Voronoi region belonging to a specified point
# Can use the index to call the appropriate element in the 'regions' attribute
tp_poly_region_one = Polygon(tp.vertices[tp.regions[tp.point_region[feature_index_one]]])

# Create GeoDataFrame for polygon
tp_poly_region_one = gpd.GeoDataFrame([tp_poly_region_one], columns = ['geometry'], crs = proj)

# Clip polygon to county boundary
tp_poly_region_one = gpd.clip(tp_poly_region_one, counties_dissolved)

# Get the equivalent feature from the rainfall dataset
rain_one = rainfall.iloc[[feature_index_one]]

# Add the rainfall value to the polygon attribute table
tp_poly_region_one["VALUE_Predict"] = rain_one["VALUE"].values

# Display attribute table
print("Attribute Table: Thiessen Polygon Interpolated Value")
display(tp_poly_region_one)
```

Here's how that one Thiessen polygon looks.

```{code-cell} ipython3
# Create subplots
fig, ax = plt.subplots(1, 1, figsize = (10, 10))

# Stylize plots
plt.style.use('bmh')

# Plot data
tp_poly_region_one.plot(ax = ax, color = 'lightseagreen', edgecolor = 'white', linewidth = 0.5)
rain_one.plot(ax = ax, marker = 'o', color = 'dimgray', markersize = 100)

# Set title
ax.set_title('San Francisco Bay Area - One Point and Thiessen Polygon', fontdict = {'fontsize': '15', 'fontweight' : '3'})
```

## K-Nearest Neighbors

KNN (also stylized as kNN) is a neighbor-based learning method that can be used for interpolation. Unlike the Thiessen polygons method, KNN looks for a specified number `K` of sampled points closest to an unknown point. The `K` known points can be used to predict the value (discrete or continuous) of the unknown point. [^sk_nn]

We can use the [`scikit-learn` module](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.KNeighborsRegressor.html) to perform KNN analysis.

```{code-cell} ipython3
# Set number of neighbors to look for
neighbors = 5

# Initialize KNN regressor
knn_regressor = KNeighborsRegressor(n_neighbors = neighbors, weights = "distance")

# Fit regressor to data
knn_regressor.fit(coords_rain_train, value_rain_train)
```

Now that we have created the KNN model, we can get the in-sample r-squared value. An in-sample statistic, as suggested by its name, is calculated by using the data that were used to build the model (the training dataset).

```{code-cell} ipython3
# Generate in-sample R^2
in_r_squared_knn = knn_regressor.score(coords_rain_train, value_rain_train)
print("KNN in-sample r-squared: {}".format(round(in_r_squared_knn, 2)))
```

Similarily, we can also get the out-of-sample r-squared value, which is calculated by using the data points that the model did not use (the testing dataset). We can also compare the test dataset's actual values to the values as predicted by the model.

```{code-cell} ipython3
# Generate out-of-sample R^2
out_r_squared_knn = knn_regressor.score(coords_rain_test, value_rain_test)
print("KNN out-of-sample r-squared: {}".format(round(out_r_squared_knn, 2)))

# Predict values for testing dataset
coords_rain_test_predict_knn = knn_regressor.predict(coords_rain_test)

# Create dictionary holding the actual and predicted values
predict_dict_knn = {"Coordinate Pair": coords_rain_test, "Actual Value": value_rain_test, "VALUE_Predict": coords_rain_test_predict_knn}

# Create dataframe from dictionary
predict_df_knn = pd.DataFrame(predict_dict_knn)

# Display attribute table
print("\nAttribute Table: Testing Set Interpolated Values - KNN Method")
display(predict_df_knn.head(2))
```

Out-of-sample r-squared looks pretty strong!

Finally, we can try to predict the values for our actual unknown points. Remember that KNN uses `K` nearest neighbors to get a value, so let's take a look at the nearest neighbors for each of our random unknown points.

```{tip}
If you are just interested in identifying the `k` nearest neighbors (no interpolation), use the [`NearestNeighbors()` function](https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestNeighbors.html#sklearn.neighbors.NearestNeighbors).
```

```{code-cell} ipython3
# Get nearest neighbors (index and distance)
distances, indices = knn_regressor.kneighbors(random_coords_list)

# Get the nearest point(s) and distance for each random point
for i in range(len(random_coords_list)):

    print("For the point {}, the closest rainfall measurement location(s) is/are:".format(random_coords_list[i]))

    # Get nearest point(s) from the GeoDataFrame using index values provided by KNN
    nearest_points = rainfall.loc[indices[i]]

    # Add distance (values provided by KNN) as a column to the GeoDataFrame values
    nearest_points["Distance"] = distances[i]

    # Display first five rows of attribute table
    display(nearest_points.head())

    print("\n")
```

Now, we can predict the values.

```{code-cell} ipython3
# Predict rainfall "values" for the random points
predict = knn_regressor.predict(random_coords_list)

# Make copy of GeoDataFrame
random_points_knn = random_points.copy()

# Add predictions as a column to GeoDataFrame
random_points_knn["VALUE_Predict"] = predict

# Display attribute table
print("Attribute Table: Random Points Interpolated Values - KNN Method")
display(random_points_knn)
```

## Kriging

Kriging is a type of interpolation that uses a semivariogram, which measures spatial autocorrelation (how similar close points are in value and how this similarity changes as distance between points increases). Thus, the semivariogram determines how much influence a known point has on an unknown point as the distance between the known point and the unknown point increases. In other words, the weight of a known point on an unknown point decreases with increasing distance, and the semivariogram determines how quickly that weight tapers with increasing distance. [^bolstad], [^esri_kriging]

For more information, see this [ArcGIS help guide on kriging](https://pro.arcgis.com/en/pro-app/latest/tool-reference/3d-analyst/how-kriging-works.htm).

Two Python packages that can be used for kriging include `scikit-learn` and `pykrige`. These packages work best when the input data has a WGS 84 projection, so we will begin by reprojecting all of our data to that coordinate system (click the + below to show code cell).

```{code-cell} ipython3
:tags: [hide-cell]

# Set projection to WGS 84 and reproject data
proj_wgs = 4326
counties_wgs = counties.to_crs(proj_wgs)
rainfall_wgs = rainfall.to_crs(proj_wgs)
coords_rain_train_gdf_wgs = coords_rain_train_gdf.to_crs(proj_wgs)
coords_rain_test_gdf_wgs = coords_rain_test_gdf.to_crs(proj_wgs)
random_points_wgs = random_points.to_crs(proj_wgs)

# Get X and Y coordinates of rainfall points
x_rain_wgs = rainfall_wgs["geometry"].x
y_rain_wgs = rainfall_wgs["geometry"].y

# Create list of XY coordinate pairs
coords_rain_train_wgs = [list(xy) for xy in zip(coords_rain_train_gdf_wgs["geometry"].x, coords_rain_train_gdf_wgs["geometry"].y)]
coords_rain_test_wgs = [list(xy) for xy in zip(coords_rain_test_gdf_wgs["geometry"].x, coords_rain_test_gdf_wgs["geometry"].y)]
random_coords_list_wgs = [list(xy) for xy in zip(random_points_wgs["geometry"].x, random_points_wgs["geometry"].y)]

# Get minimum and maximum coordinate values of rainfall points
min_x_rain_wgs, min_y_rain_wgs, max_x_rain_wgs, max_y_rain_wgs = rainfall_wgs.total_bounds
```

### Method 1 - Using `scikit-learn`

Kriging can be performed using [Gaussian processes from the `scikit-learn` module](https://scikit-learn.org/stable/modules/gaussian_process.html) (Gaussian processes is essentially equivalent to kriging). Various kernels for Gaussian processes can be specified. We will continue to use the training and testing datasets created from our KNN analysis.

```{code-cell} ipython3
# Create a 100 by 100 cell mesh grid
# Horizontal and vertical cell counts should be the same
XX_sk_krig, YY_sk_krig = np.mgrid[min_x_rain_wgs:max_x_rain_wgs:100j, min_y_rain_wgs:max_y_rain_wgs:100j]

# Create 2-D array of the coordinates (paired) of each cell in the mesh grid
positions_sk_krig = np.vstack([XX_sk_krig.ravel(), YY_sk_krig.ravel()]).T

# Generate Gaussian Process model (can change parameters as desired)
gp = GaussianProcessRegressor(n_restarts_optimizer = 10)

# Fit kernel density estimator to coordinates and values
gp.fit(coords_rain_train_wgs, value_rain_train)

# Evaluate the model on coordinate pairs
Z_sk_krig = gp.predict(positions_sk_krig)

# Reshape the data to fit mesh grid
Z_sk_krig = Z_sk_krig.reshape(XX_sk_krig.shape)
```

Next, we can calculate our r-squared statistics and predictions.

```{code-cell} ipython3
# Generate in-sample R^2
in_r_squared_sk_krig = gp.score(coords_rain_train_wgs, value_rain_train)
print("Kriging in-sample r-squared: {}".format(round(in_r_squared_sk_krig, 2)))

# Generate out-of-sample R^2
out_r_squared_sk_krig = gp.score(coords_rain_test_wgs, value_rain_test)
print("Kriging out-of-sample r-squared: {}".format(round(out_r_squared_sk_krig, 2)))

# Predict values for testing dataset
coords_rain_test_predict_sk_krig = gp.predict(coords_rain_test_wgs)

# Create dictionary holding the actual and predicted values
predict_dict_sk_krig = {"Coordinate Pair": coords_rain_test_wgs, "Actual Value": value_rain_test, "VALUE_Predict": coords_rain_test_predict_sk_krig}

# Create dataframe from dictionary
predict_df_sk_krig = pd.DataFrame(predict_dict_sk_krig)

# Display attribute table
print("\nAttribute Table: Testing Set Interpolated Values - Scikit-Learn Kriging Method")
display(predict_df_sk_krig.head(2))
```

Model seems like a good fit! Let's export the raster.

```{code-cell} ipython3
# Flip array vertically and rotate 270 degrees
Z_sk_krig = np.rot90(np.flip(Z_sk_krig, 0), 3)

# Export raster
export_kde_raster(Z = Z_sk_krig, XX = XX_sk_krig, YY = YY_sk_krig,
                  min_x = min_x_rain_wgs, max_x = max_x_rain_wgs, min_y = min_y_rain_wgs, max_y = max_y_rain_wgs,
                  proj = proj_wgs, filename = "../temp/e_bay-area-rain_sk_kriging.tif")
```

```{attention} The resulting raster should be clipped. Because the resulting raster covers the extent of the points in a bounding box fashion, the raster in this case covers areas that are not within the counties boundaries (such as in the ocean) where we do not have sample points. Thus, there will be interpolated values in those areas that might not make sense.
```

Finally, we import the raster, extract the interpolated values of the raster to our random points, mask it to the counties boundaries, and plot the data.

```{code-cell} ipython3
# Open raster
raster_sk = rasterio.open("../temp/e_bay-area-rain_sk_kriging.tif")

# Create copy of random points GeoDataFrame
random_points_sk_krig = random_points_wgs.copy()

# Extract raster value at each random point and add the values to the GeoDataFrame
random_points_sk_krig["VALUE_Predict"] = [x[0] for x in raster_sk.sample(random_coords_list_wgs)]

# Display attribute table
print("Attribute Table: Random Points Interpolated Values - Scikit-Learn Kriging Method")
display(random_points_sk_krig)
```

```{code-cell} ipython3
# Mask raster to counties shape
out_image_sk, out_transform_sk = rasterio.mask.mask(raster_sk, counties_wgs.geometry.values, crop = True)

# Stylize plots
plt.style.use('bmh')

# Plot data
fig, ax = plt.subplots(1, figsize = (10, 10))
show(out_image_sk, ax = ax, transform = out_transform_sk, cmap = "RdPu")
ax.plot(x_rain_wgs, y_rain_wgs, 'k.', markersize = 2, alpha = 0.5)
random_points_sk_krig.plot(ax = ax, color = 'dimgray', markersize = 100)
counties_wgs.plot(ax = ax, color = 'none', edgecolor = 'dimgray')
plt.gca().invert_yaxis()

# Set title
ax.set_title('San Francisco Bay Area - Interpolating Rainfall using Kriging from Scikit-Learn', fontdict = {'fontsize': '15', 'fontweight' : '3'})

# Display plot
plt.show()
```

### Method 2 - Using `PyKrige`

The [`pykrige` module](https://geostat-framework.readthedocs.io/projects/pykrige/en/stable/index.html) offers ordinary and universal kriging. It also supports various variogram models in addition to Gaussian.

```{code-cell} ipython3
# Adapted from: https://geostat-framework.readthedocs.io/projects/pykrige/en/latest/examples/04_krige_geometric.html

# Create a 100 by 100 grid
# Horizontal and vertical cell counts should be the same
XX_pk_krig = np.linspace(min_x_rain_wgs, max_x_rain_wgs, 100)
YY_pk_krig = np.linspace(min_y_rain_wgs, max_y_rain_wgs, 100)

# Generate ordinary kriging object
OK = OrdinaryKriging(
    np.array(x_rain_wgs),
    np.array(y_rain_wgs),
    value_rain,
    variogram_model = "linear",
    verbose = False,
    enable_plotting = False,
    coordinates_type = "geographic",
)

# Evaluate the method on grid
Z_pk_krig, sigma_squared_p_krig = OK.execute("grid", XX_pk_krig, YY_pk_krig)

# Export raster
export_kde_raster(Z = Z_pk_krig, XX = XX_pk_krig, YY = YY_pk_krig,
                  min_x = min_x_rain_wgs, max_x = max_x_rain_wgs, min_y = min_y_rain_wgs, max_y = max_y_rain_wgs,
                  proj = proj_wgs, filename = "../temp/e_bay-area-rain_pk_kriging.tif")

# Open raster
raster_pk = rasterio.open("../temp/e_bay-area-rain_pk_kriging.tif")

# Create copy of random points GeoDataFrame
random_points_pk_krig = random_points_wgs.copy()

# Extract raster value at each random point and add the values to the GeoDataFrame
random_points_pk_krig["VALUE_Predict"] = [x[0] for x in raster_pk.sample(random_coords_list_wgs)]

# Display attribute table
print("Attribute Table: Random Points Interpolated Values - PyKrige Kriging Method")
display(random_points_pk_krig)

# Mask raster to counties shape
out_image_pk, out_transform_pk = rasterio.mask.mask(raster_pk, counties_wgs.geometry.values, crop = True)

# Stylize plots
plt.style.use('bmh')

# Plot data
fig, ax = plt.subplots(1, figsize = (10, 10))
show(out_image_pk, ax = ax, transform = out_transform_pk, cmap = "RdPu")
ax.plot(x_rain_wgs, y_rain_wgs, 'k.', markersize = 2, alpha = 0.5)
random_points_pk_krig.plot(ax = ax, color = 'dimgray', markersize = 100)
counties_wgs.plot(ax = ax, color = 'none', edgecolor = 'dimgray')
plt.gca().invert_yaxis()

# Set title
ax.set_title('San Francisco Bay Area - Interpolating Rainfall using Kriging from PyKrige', fontdict = {'fontsize': '15', 'fontweight' : '3'})

# Display plot
plt.show()
```

[^bolstad]: GIS Fundamentals: A First Text on Geographic Information Systems, 5th ed., Paul Bolstad
[^scipy_voronoi]: [scipy.spatial.Voronoi, SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Voronoi.html)
[^sk_nn]: [Nearest Neighbors, scikit-learn](https://scikit-learn.org/stable/modules/neighbors.html)
[^esri_kriging]: [How Kriging works, Esri](https://pro.arcgis.com/en/pro-app/latest/tool-reference/3d-analyst/how-kriging-works.htm)