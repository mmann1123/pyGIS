# %%
import geowombat as gw
from geowombat.data import l8_224078_20200518, l8_224078_20200518_polygons
from geowombat.ml import fit, predict, fit_predict
import geopandas as gpd
from sklearn_xarray.preprocessing import Featurizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB

le = LabelEncoder()

# The labels are string names, so here we convert them to integers
labels = gpd.read_file(l8_224078_20200518_polygons)
labels["lc"] = le.fit(labels.name).transform(labels.name)
print(labels)
# %%


import matplotlib.pyplot as plt

# Use a data pipeline
pl = Pipeline([("scaler", StandardScaler()), ("pca", PCA()), ("clf", GaussianNB())])

fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

# Fit the classifier
with gw.config.update(ref_res=100):
    with gw.open(l8_224078_20200518) as src:
        X, Xy, clf = fit(src, pl, labels, col="lc")
        y = predict(src, X, clf)
        y.plot(robust=True, ax=ax)
plt.tight_layout(pad=1)


# %%
from geowombat.ml import fit_predict

fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

with gw.config.update(ref_res=300):
    with gw.open(l8_224078_20200518) as src:
        y = fit_predict(src, pl, labels, col="lc")
        y.plot(robust=True, ax=ax)
plt.tight_layout(pad=1)

# %%
from sklearn.cluster import KMeans

cl = Pipeline([("clf", KMeans(n_clusters=6, random_state=0))])

fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

# Fit_predict unsupervised classifier
with gw.config.update(ref_res=300):
    with gw.open(l8_224078_20200518) as src:
        y = fit_predict(src, cl)
        y.plot(robust=True, ax=ax)
plt.tight_layout(pad=1)
# %%
fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

with gw.config.update(ref_res=100):
    with gw.open(
        [l8_224078_20200518, l8_224078_20200518],
        time_names=["t1", "t2"],
        stack_dim="time",
    ) as src:
        y = fit_predict(src, pl, labels, col="lc")
        print(y)
        # plot one time period prediction
        y.sel(time="t1").plot(robust=True, ax=ax)
# %%
fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

with gw.config.update(ref_res=100):
    with gw.open(l8_224078_20200518) as src:
        X, Xy, clf = fit(src, pl, labels, col="lc")
        y = predict(src, X, clf)
        y.plot(robust=True, ax=ax)
# %%
pl = Pipeline([("scaler", StandardScaler()), ("pca", PCA()), ("clf", GaussianNB())])

param_grid = {"scaler__with_std": [True, False], "pca__n_components": [1, 2, 3]}
# %%
from sklearn.model_selection import GridSearchCV, KFold
from sklearn_xarray.model_selection import CrossValidatorWrapper

pl = Pipeline([("scaler", StandardScaler()), ("pca", PCA()), ("clf", GaussianNB())])

cv = CrossValidatorWrapper(KFold())
gridsearch = GridSearchCV(
    pl,
    cv=cv,
    scoring="balanced_accuracy",
    param_grid={"scaler__with_std": [True, False], "pca__n_components": [1, 2, 3]},
)

fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

with gw.config.update(ref_res=300):
    with gw.open(l8_224078_20200518) as src:
        # fit a model to get Xy used to train model
        X, Xy, pipe = fit(src, pl, labels, col="lc")
        gridsearch.fit(*Xy)
        print(gridsearch.cv_results_)
        print(gridsearch.best_score_)
        print(gridsearch.best_params_)
        pipe.set_params(**gridsearch.best_params_)
        y = predict(src, X, pipe)
        y.plot(robust=True, ax=ax)
plt.tight_layout(pad=1)
# %%
import numpy as np

x = np.linspace(-90, 90, 6)
y = np.linspace(90, -90, 6)
X, Y = np.meshgrid(x, y)
X
# %%
import matplotlib.pyplot as plt

Z1 = np.abs(((X - 10) ** 2 + (Y - 10) ** 2) / 1**2)
Z2 = np.abs(((X + 10) ** 2 + (Y + 10) ** 2) / 2.5**2)
Z = Z1 - Z2

plt.imshow(Z)
plt.title("Temperature")
plt.show()
# %%
from rasterio.transform import Affine
import rasterio as rio

res = (x[-1] - x[0]) / 240.0
transform = Affine.translation(x[0] - res / 2, y[0] - res / 2) * Affine.scale(res, res)

# open in 'write' mode, unpack profile info to dst
with rio.open(
    "../temp/new_raster.tif",
    "w",
    driver="GTiff",  # output file type
    height=Z.shape[0],  # shape of array
    width=Z.shape[1],
    count=1,  # number of bands
    dtype=Z.dtype,  # output datatype
    crs="+proj=latlong",  # CRS
    transform=transform,  # location and resolution of upper left cell
) as dst:
    # check for number of bands
    if dst.count == 1:
        # write single band
        dst.write(Z, 1)
    else:
        # write each band individually
        for band in range(len(Z)):
            # write data, band # (starting from 1)
            dst.write(Z[band], band + 1)
# %%
import geowombat as gw
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.patheffects as pe
from geowombat.data import l8_224077_20200518_B4, l8_224078_20200518_B4
from os.path import basename


def plot(bounds_by, ref_image=None, cmap="viridis"):
    fig, ax = plt.subplots(dpi=200)
    with gw.config.update(ref_image=ref_image):
        with gw.open(
            [l8_224077_20200518_B4, l8_224078_20200518_B4],
            band_names=["nir"],
            chunks=256,
            mosaic=True,
            bounds_by=bounds_by,
            persist_filenames=True,
        ) as srca:
            # Plot the NIR band
            srca.where(srca != 0).sel(band="nir").plot.imshow(
                robust=True, cbar_kwargs={"label": "DN"}, ax=ax
            )
            # Plot the image chunks
            srca.gw.chunk_grid.plot(color="none", edgecolor="k", ls="-", lw=0.5, ax=ax)
            # Plot the image footprints
            srca.gw.footprint_grid.plot(color="none", edgecolor="orange", lw=2, ax=ax)
            # Label the image footprints
            for row in srca.gw.footprint_grid.itertuples(index=False):
                ax.scatter(
                    row.geometry.centroid.x,
                    row.geometry.centroid.y,
                    s=50,
                    color="red",
                    edgecolor="white",
                    lw=1,
                )
                ax.annotate(
                    basename(row.footprint).replace(".TIF", ""),
                    (row.geometry.centroid.x, row.geometry.centroid.y),
                    color="black",
                    size=8,
                    ha="center",
                    va="center",
                    path_effects=[pe.withStroke(linewidth=1, foreground="white")],
                )
            # Set the display bounds
            ax.set_ylim(
                srca.gw.footprint_grid.total_bounds[1] - 10,
                srca.gw.footprint_grid.total_bounds[3] + 10,
            )
            ax.set_xlim(
                srca.gw.footprint_grid.total_bounds[0] - 10,
                srca.gw.footprint_grid.total_bounds[2] + 10,
            )
    title = (
        f"Image {bounds_by}"
        if bounds_by
        else str(Path(ref_image).name.split(".")[0]) + " as reference"
    )
    size = 12 if bounds_by else 8
    ax.set_title(title, size=size)
    plt.tight_layout(pad=1)


# %%
from geowombat.data import l8_224078_20200518
import rasterio

fig, ax = plt.subplots(dpi=200)
with gw.open(l8_224078_20200518, nodata=0) as src:
    src = src.gw.mask_nodata()
    src.sel(band=[3, 2, 1]).plot.imshow(robust=True, ax=ax)
plt.tight_layout(pad=1)
# %%
with rasterio.open(
    "../data/LC08_L2SP_016040_20210317_20210328_02_T1_clip.tif", mode="r", nodata=0
) as src:
    # Get red band
    band_red = src.read(3)

    # Get NIR band
    band_nir = src.read(4)

    # Allow division by zero
    np.seterr(divide="ignore", invalid="ignore")

    # Calculate NDVI
    ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)

# Set pixels whose values are outside the NDVI range (-1, 1) to NaN
# Likely due to errors in the Landsat imagery
ndvi[ndvi > 1] = np.nan
ndvi[ndvi < -1] = np.nan

# Plot raster
plt.imshow(ndvi)
plt.title("NDVI")
plt.show()

# Show raster values
print("Raster values:\n", ndvi)
# %%
import geowombat as gw
import matplotlib.pyplot as plt

fig, ax = plt.subplots(dpi=200)


LS = "../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF"
precip = "../data/precipitation_20200601_500m.tif"

with gw.config.update(ref_image=LS):
    with gw.open(precip, resampling="bilinear", nodata=-9999) as src:
        print(src)
        ax.imshow(src.data[0])

# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots(dpi=200)
from geowombat.data import rgbn

proj4 = "+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

with gw.config.update(ref_crs=proj4):
    with gw.open(rgbn, nodata=0) as src:
        # replace nodata with nan
        src = src.gw.mask_nodata()
        print(src.transform)
        print(src.crs)
        print(src.resampling)
        print(src.res)
        src.sel(band=[3, 2, 1]).plot.imshow(robust=True, ax=ax)

plt.tight_layout(pad=1)

# %%
from geowombat.data import l8_224078_20200518

with gw.config.update(scale_factor=0.0001):
    with gw.open(l8_224078_20200518) as src:
        print(src.values[0])
        print(src.scales)
        print(src.gw.scale_factor)

# %%

from fiona.crs import from_epsg

# Set the GeoDataFrame's coordinate system to WGS84
from_epsg(4326)
# %%
import numpy as np

x = np.linspace(-90, 90, 6)
y = np.linspace(90, -90, 6)
X, Y = np.meshgrid(x, y)
X
import matplotlib.pyplot as plt

Z1 = np.abs(((X - 10) ** 2 + (Y - 10) ** 2) / 1**2)
Z2 = np.abs(((X + 10) ** 2 + (Y + 10) ** 2) / 2.5**2)
Z = Z1 - Z2

plt.imshow(Z)
plt.title("Temperature")
plt.show()
# %%
from rasterio.transform import Affine
import rasterio as rio

res = (x[-1] - x[0]) / 240.0
transform = Affine.translation(x[0] - res / 2, y[0] - res / 2) * Affine.scale(res, res)

# open in 'write' mode, unpack profile info to dst
with rio.open(
    "../temp/new_raster.tif",
    "w",
    driver="GTiff",  # output file type
    height=Z.shape[0],  # shape of array
    width=Z.shape[1],
    count=1,  # number of bands
    dtype=Z.dtype,  # output datatype
    crs="+proj=latlong",  # CRS
    transform=transform,  # location and resolution of upper left cell
) as dst:
    # check for number of bands
    if dst.count == 1:
        # write single band
        dst.write(Z, 1)
    else:
        # write each band individually
        for band in range(len(Z)):
            # write data, band # (starting from 1)
            dst.write(Z[band], band + 1)

# %%

# Import modules
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from io import StringIO

data = """
ID,X,Y
1,  -87.789,  41.976
1,  -87.482,  41.677
2,  -87.599,  41.908
2,  -87.598,  41.708
2,  -87.643,  41.675
"""
# use StringIO to read in text chunk
df = pd.read_table(StringIO(data), sep=",")

# zip the coordinates into a point object and convert to a GeoData Frame
points = [Point(xy) for xy in zip(df.X, df.Y)]
points = gpd.GeoDataFrame(df, geometry=points, crs="EPSG:4326")
# create line for each ID
lines = points.groupby(["ID"])["geometry"].apply(lambda x: LineString(x.tolist()))
lines = gpd.GeoDataFrame(lines, geometry="geometry", crs="EPSG:4326")
lines.reset_index(inplace=True)

# %%
# plot county outline and add wells to axis (ax)
lines.plot(column="ID")

# plot county outline and add wells to axis (ax)
lines = lines.to_crs(3857)
# check the linear unit name in `unit_name`.
print(lines.crs.axis_info)

buf = lines.buffer(distance=1000)
bp = buf.plot()
lines.plot(ax=bp, color="red")
print(buf)

line_buffer = lines.copy()
line_buffer["geometry"] = buf
print(line_buffer)


buf = lines.buffer(distance=3000, cap_style=2)
bp = buf.plot()
lines.plot(ax=bp, color="red")

buf_right = lines.buffer(distance=3000, single_sided=True)
bp = buf_right.plot(color="green")

buf_left = lines.buffer(distance=-1500, single_sided=True)
buf_left.plot(ax=bp, color="purple")
lines.plot(ax=bp, color="white")

from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points

orig = Point(1, 1.67)
dest1, dest2, dest3 = Point(0, 1.45), Point(2, 2), Point(0, 2.5)


destinations = MultiPoint([dest1, dest2, dest3])
print(destinations)

nearest_geoms = nearest_points(orig, destinations)
original_point, nearest_destination = nearest_geoms
print(nearest_geoms)
print("Coordinates of original point:", original_point)
print("Coordinates of closest destination point:", nearest_destination)

# %%
from shapely.ops import nearest_points


def _nearest(row, df1, df2, geom1="geometry", geom2="geometry", df2_column=None):
    """Find the nearest point and return the corresponding value from specified column."""

    # create object usable by Shapely
    geom_union = df2.unary_union

    # Find the geometry that is closest
    nearest = df2[geom2] == nearest_points(row[geom1], geom_union)[1]
    # Get the corresponding value from df2 (matching is based on the geometry)
    if df2_column is None:
        value = df2[nearest].index[0]
    else:
        value = df2[nearest][df2_column].values[0]
    return value


def nearest(df1, df2, geom1_col="geometry", geom2_col="geometry", df2_column=None):
    """Find the nearest point and return the corresponding value from specified column.
    :param df1: Origin points
    :type df1: geopandas.GeoDataFrame
    :param df2: Destination points
    :type df2: geopandas.GeoDataFrame
    :param geom1_col: name of column holding coordinate geometry, defaults to 'geometry'
    :type geom1_col: str, optional
    :param geom2_col: name of column holding coordinate geometry, defaults to 'geometry'
    :type geom2_col: str, optional
    :param df2_column: column name to return from df2, defaults to None
    :type df2_column: str, optional
    :return: df1 with nearest neighbor index or df2_column appended
    :rtype: geopandas.GeoDataFrame
    """
    df1["nearest_id"] = df1.apply(
        _nearest,
        df1=df1,
        df2=df2,
        geom1=geom1_col,
        geom2=geom2_col,
        df2_column=df2_column,
        axis=1,
    )
    return df1


# generate origin and destination points as geodataframe
orig = {
    "name": ["Origin_1", "Origin_2"],
    "geometry": [Point(-77.3, 38.94), Point(-77.41, 39.93)],
}
orig = gpd.GeoDataFrame(orig, crs="EPSG:4326")
print(orig)

dest = {
    "name": ["Baltimore", "Washington", "Fredrick"],
    "geometry": [
        Point(
            -76.61,
            39.29,
        ),
        Point(-77.04, 38.91),
        Point(-77.40, 39.41),
    ],
}
dest = gpd.GeoDataFrame(dest, crs="EPSG:4326")
print(dest)

near = nearest(df1=orig, df2=dest, df2_column="name")
near.head()


# %%
nearest(df1=orig, df2=dest, df2_column="name")

# %%
import geowombat as gw
import numpy as np
from itertools import product
import rasterio
from rasterio.transform import Affine
import matplotlib.pyplot as plt

# Generate mesh grid for rasters
x = np.linspace(-90, 90, 6)
y = np.linspace(90, -90, 6)
X, Y = np.meshgrid(x, y)

# Generate values for mesh grid
Z1 = np.abs(((X - 10) ** 2 + (Y - 10) ** 2) / 1**2)
Z2 = np.abs(((X + 10) ** 2 + (Y + 10) ** 2) / 2.5**2)
Z3 = np.abs(((X + 3) + (Y - 8) ** 2) / 3**2)

# Generate raster values
Z = Z1 - Z2

# Set transform
xres = (x[-1] - x[0]) / len(x)
yres = (y[-1] - y[0]) / len(y)
transform = Affine.translation(x[0] - xres / 2, y[0] - yres / 2) * Affine.scale(
    xres, yres
)

# Save first raster
with rasterio.open(
    "../temp/window_raster.tif",
    mode="w",
    driver="GTiff",
    height=Z.shape[0],
    width=Z.shape[1],
    count=1,
    dtype=Z.dtype,
    crs="+proj=latlong",
    transform=transform,
) as new_dataset:
    new_dataset.write(Z, 1)

# Open and read raster
src = rasterio.open("../temp/window_raster.tif")
raster = src.read(1)

# Plot raster
plt.imshow(raster, cmap="BrBG")
plt.title("Raster")
plt.show()

# Show raster values
print(raster)
# %%
with gw.open("../temp/window_raster.tif") as src:
    # Create plot
    fig, ax = plt.subplots(dpi=200)

    # Calculate local average
    output_gw = src.gw.moving(stat="mean", w=5, n_jobs=4, nodata=0)
    print(output_gw)

    # Plot raster
    output_gw.sel(band=1).gw.imshow(robust=True, ax=ax)
    plt.tight_layout(pad=1)
# %%


def create_grid(feature, shape, side_length):
    """Create a grid consisting of either rectangles or hexagons with a specified side length that covers the extent of input feature."""

    # Slightly displace the minimum and maximum values of the feature extent by creating a buffer
    # This decreases likelihood that a feature will fall directly on a cell boundary (in between two cells)
    # Buffer is projection dependent (due to units)
    feature = feature.buffer(20)

    # Get extent of buffered input feature
    min_x, min_y, max_x, max_y = feature.total_bounds

    # Create empty list to hold individual cells that will make up the grid
    cells_list = []

    # Create grid of squares if specified
    if shape in ["square", "rectangle", "box"]:
        # Adapted from https://james-brennan.github.io/posts/fast_gridding_geopandas/
        # Create and iterate through list of x values that will define column positions with specified side length
        for x in np.arange(min_x - side_length, max_x + side_length, side_length):
            # Create and iterate through list of y values that will define row positions with specified side length
            for y in np.arange(min_y - side_length, max_y + side_length, side_length):
                # Create a box with specified side length and append to list
                cells_list.append(box(x, y, x + side_length, y + side_length))

    # Otherwise, create grid of hexagons
    elif shape == "hexagon":
        # Set horizontal displacement that will define column positions with specified side length (based on normal hexagon)
        x_step = 1.5 * side_length

        # Set vertical displacement that will define row positions with specified side length (based on normal hexagon)
        # This is the distance between the centers of two hexagons stacked on top of each other (vertically)
        y_step = math.sqrt(3) * side_length

        # Get apothem (distance between center and midpoint of a side, based on normal hexagon)
        apothem = math.sqrt(3) * side_length / 2

        # Set column number
        column_number = 0

        # Create and iterate through list of x values that will define column positions with vertical displacement
        for x in np.arange(min_x, max_x + x_step, x_step):
            # Create and iterate through list of y values that will define column positions with horizontal displacement
            for y in np.arange(min_y, max_y + y_step, y_step):
                # Create hexagon with specified side length
                hexagon = [
                    [
                        x + math.cos(math.radians(angle)) * side_length,
                        y + math.sin(math.radians(angle)) * side_length,
                    ]
                    for angle in range(0, 360, 60)
                ]

                # Append hexagon to list
                cells_list.append(Polygon(hexagon))

            # Check if column number is even
            if column_number % 2 == 0:
                # If even, expand minimum and maximum y values by apothem value to vertically displace next row
                # Expand values so as to not miss any features near the feature extent
                min_y -= apothem
                max_y += apothem

            # Else, odd
            else:
                # Revert minimum and maximum y values back to original
                min_y += apothem
                max_y -= apothem

            # Increase column number by 1
            column_number += 1

    # Else, raise error
    else:
        raise Exception("Specify a rectangle or hexagon as the grid shape.")

    # Create grid from list of cells
    grid = gpd.GeoDataFrame(cells_list, columns=["geometry"], crs=proj)

    # Create a column that assigns each grid a number
    grid["Grid_ID"] = np.arange(len(grid))

    # Return grid
    return grid


# %%

# Set side length for cells in grid
# This is dependent on projection chosen as length is in units specified in projection
side_length = 5000

# Set shape of grid
shape = "hexagon"
# shape = "rectangle"

import geopandas as gpd
import geoplot as gplt
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import Affine
from scipy import stats
from shapely.geometry import Polygon, box
from sklearn.datasets import fetch_species_distributions
from sklearn.neighbors import KernelDensity

# County boundaries
# Source: https://opendata.mtc.ca.gov/datasets/san-francisco-bay-region-counties-clipped?geometry=-125.590%2C37.123%2C-119.152%2C38.640
counties = gpd.read_file(
    "../_static/e_vector_shapefiles/sf_bay_counties/sf_bay_counties.shp"
)

# Well locations
# Source: https://gis.data.ca.gov/datasets/3a3e681b894644a9a95f9815aeeeb57f_0?geometry=-123.143%2C36.405%2C-119.230%2C37.175
# Modified by author so that only the well locations within the counties and the surrounding 50 km were kept
wells = gpd.read_file(
    "../_static/e_vector_shapefiles/sf_bay_wells_50km/sf_bay_wells_50km.shp"
)

# Reproject data to NAD83(HARN) / California Zone 3
# https://spatialreference.org/ref/epsg/2768/
proj = 2768
counties = counties.to_crs(proj)
wells = wells.to_crs(proj)

# Create a column that assigns each well a number
wells["Well_ID"] = np.arange(wells.shape[0])


# %%
# Create grid
bay_area_grid = create_grid(feature=wells, shape=shape, side_length=side_length)

# Create subplots
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plot data
counties.plot(ax=ax, color="bisque", edgecolor="dimgray")
wells.plot(ax=ax, marker="o", color="dodgerblue", markersize=3)
bay_area_grid.plot(ax=ax, color="none", edgecolor="lightseagreen", alpha=0.55)

# Set title
ax.set_title(
    "San Francisco Bay Area - Boundaries, Wells, and Grids",
    fontdict={"fontsize": "15", "fontweight": "3"},
)
# %%
# Perform spatial join, merging attribute table of wells point and that of the cell with which it intersects
# predicate = "intersects" also counts those that fall on a cell boundary (between two cells)
# predicate = "within" will not count those fall on a cell boundary
wells_cell = gpd.sjoin(wells, bay_area_grid, how="inner", op="intersects")

# Remove duplicate counts
# With intersect, those that fall on a boundary will be allocated to all cells that share that boundary
wells_cell = wells_cell.drop_duplicates(subset=["Well_ID"]).reset_index(drop=True)

# Set field name to hold count value
count_field = "Count"

# Add a field with constant value of 1
wells_cell[count_field] = 1

# Group GeoDataFrame by cell while aggregating the Count values
wells_cell = wells_cell.groupby("Grid_ID").agg({count_field: "sum"})

# Merge the resulting grouped dataframe with the grid GeoDataFrame, using a left join to keep all cell polygons
bay_area_grid = bay_area_grid.merge(wells_cell, on="Grid_ID", how="left")

# Fill the NaN values (cells without any points) with 0
bay_area_grid[count_field] = bay_area_grid[count_field].fillna(0)

# Convert Count field to integer
bay_area_grid[count_field] = bay_area_grid[count_field].astype(int)

# Display grid attribute table
display(bay_area_grid)
# %%
# Create subplots
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plot data
counties.plot(ax=ax, color="none", edgecolor="dimgray")
wells.plot(ax=ax, marker="o", color="dimgray", markersize=3)
bay_area_grid.plot(
    ax=ax,
    column="Count",
    cmap="RdPu",
    edgecolor="lightseagreen",
    linewidth=0.5,
    alpha=0.70,
    legend=True,
)

# Set title
ax.set_title(
    "San Francisco Bay Area - Binning Well Points",
    fontdict={"fontsize": "15", "fontweight": "3"},
)
# %%
# Select the Santa Clara County boundary
sc_county = counties[counties["coname"] == "Santa Clara County"]

# Subset the GeoDataFrame by checking which wells are within Santa Clara County
sc_county_wells = wells[wells.within(sc_county.geometry.values[0])]

# Create grid
sc_county_grid = create_grid(
    feature=sc_county_wells, shape=shape, side_length=side_length
)

# Create subplots
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plot data
sc_county.plot(ax=ax, color="bisque", edgecolor="dimgray")
sc_county_wells.plot(ax=ax, marker="o", color="dodgerblue", markersize=3)
sc_county_grid.plot(ax=ax, color="none", edgecolor="lightseagreen", alpha=0.55)

# Set title
ax.set_title(
    "Santa Clara County - Boundaries, Wells, and Grids",
    fontdict={"fontsize": "15", "fontweight": "3"},
)

# %%


# Create empty list used to hold count values for each grid
counts_list = []

# Create empty list to hold index of points that have already been matched to a grid
counted_points = []

# Iterate through each cell in grid
for i_1 in range(0, sc_county_grid.shape[0]):
    # Get a cell by index
    cell = sc_county_grid.iloc[[i_1]]

    # Reset index of cell to 0
    cell = cell.reset_index(drop=True)

    # Set point count to 0
    count = 0

    # Iterate through each feature in wells dataset
    for i_2 in range(0, sc_county_wells.shape[0]):
        # Check if index of point is in list of indices whose points have already been matched to a grid and counted
        if i_2 in counted_points:
            # If already counted, skip remaining statements in loop and start at top of loop
            continue

        # Otherwise, continue with remaining statements
        else:
            pass

        # Get a well point by index
        well = sc_county_wells.iloc[[i_2]]

        # Reset index of well point (to 0) to match the index-reset cell
        well = well.reset_index(drop=True)

        # Check if well intersects the cell
        # Best to use intersects instead of within or contains, as intersect will count points that fall exactly on the cell boundaries
        # Points that fall exactly on a cell boundary (between two cells) will be allocated to the first of the two cells called in script
        criteria_met = well.intersects(cell)[0]

        # If preferred, can check if well is within cell or if cell contains well
        # Both statements do the same thing
        # criteria_met = well.within(cell)[0]
        # criteria_met = cell.contains(well)[0]

        # Check if criteria has been met (True)
        if criteria_met:
            # If True, increase counter by 1 for the cell
            count += 1

            # Add index of counted point to the list
            counted_points.append(i_2)

        # Otherwise, criteria is not met (False)
        else:
            pass

    # Add total count for that cell to the list of counts
    counts_list.append(count)

# print(counts_list)

# Add a new column to the grid GeoDataFrame with the list of counts for each cell
sc_county_grid["Count"] = pd.Series(counts_list)

# Display grid attribute table
display(sc_county_grid)

# %%
# Create subplots
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plot data
sc_county.plot(ax=ax, color="none", edgecolor="dimgray")
sc_county_wells.plot(ax=ax, marker="o", color="dimgray", markersize=3)
sc_county_grid.plot(
    ax=ax,
    column="Count",
    cmap="RdPu",
    edgecolor="lightseagreen",
    linewidth=0.5,
    alpha=0.70,
    legend=True,
)

# Set title
ax.set_title(
    "Santa Clara County - Binning Well Points",
    fontdict={"fontsize": "15", "fontweight": "3"},
)
# %%
# Set projection to WGS 84 and reproject data
proj_wgs = 4326
counties_wgs = counties.to_crs(proj_wgs)
wells_wgs = wells.to_crs(proj_wgs)

# Create subplots
fig, ax = plt.subplots(1, 1, figsize=(10, 10))

# Plot data
counties_wgs.plot(ax=ax, color="none", edgecolor="dimgray")
wells_wgs.plot(ax=ax, marker="o", color="dimgray", markersize=3)
gplt.kdeplot(
    wells_wgs, ax=ax, shade=True, cmap="RdPu", alpha=0.5
)  # , ,  clip = counties_wgs, thresh = 0, ax = ax, )

# Set title
ax.set_title(
    "San Francisco Bay Area - Kernel Density Estimation for Wells",
    fontdict={"fontsize": "15", "fontweight": "3"},
)
# %%
c = os.environ.get("census_api_key")


# %%
import geowombat as gw
from geowombat.data import l8_224078_20200518, l8_224078_20200518_polygons
from geowombat.ml import fit, predict, fit_predict
import geopandas as gpd
from sklearn_xarray.preprocessing import Featurizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB

le = LabelEncoder()

# The labels are string names, so here we convert them to integers
labels = gpd.read_file(l8_224078_20200518_polygons)
labels["lc"] = le.fit(labels.name).transform(labels.name)
print(labels)
# %%
# Import GeoWombat
import geowombat as gw

# import plotting
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

# load data
from geowombat.data import l8_224077_20200518_B2, l8_224078_20200518_B2

fig, ax = plt.subplots(dpi=200)
filenames = [l8_224077_20200518_B2, l8_224078_20200518_B2]
with gw.open(
    filenames, band_names=["blue"], mosaic=True, overlap="mean", bounds_by="union"
) as src:
    src.where(src != 0).sel(band="blue").plot.imshow(robust=True, ax=ax)
plt.tight_layout(pad=1)
# %%
fig, ax = plt.subplots(dpi=200)
filenames = [l8_224077_20200518_B2, l8_224078_20200518_B2]
with gw.open(
    filenames,
    band_names=["blue"],
    mosaic=True,
    overlap="mean",
    bounds_by="intersection",
) as src:
    src.where(src != 0).sel(band="blue").plot.imshow(robust=True, ax=ax)
plt.tight_layout(pad=1)
# %%
from geowombat.data import l8_224077_20200518_B4, l8_224078_20200518_B4


def plot(bounds_by, ref_image=None, cmap="viridis"):
    fig, ax = plt.subplots(dpi=200)
    with gw.config.update(ref_image=ref_image):
        with gw.open(
            [l8_224077_20200518_B4, l8_224078_20200518_B4],
            band_names=["nir"],
            chunks=256,
            mosaic=True,
            bounds_by=bounds_by,
        ) as srca:
            # Plot the NIR band
            srca.where(srca != 0).sel(band="nir").plot.imshow(
                robust=True, cbar_kwargs={"label": "DN"}, ax=ax
            )
            # Plot the image chunks
            srca.gw.chunk_grid.plot(color="none", edgecolor="k", ls="-", lw=0.5, ax=ax)
            # Plot the image footprints
            # Label the image footprints
            for row in srca.gw.footprint_grid.itertuples(index=False):
                ax.scatter(
                    row.geometry.centroid.x,
                    row.geometry.centroid.y,
                    s=50,
                    color="red",
                    edgecolor="white",
                    lw=1,
                )
                ax.annotate(
                    row.footprint.replace(".TIF", ""),
                    (row.geometry.centroid.x, row.geometry.centroid.y),
                    color="black",
                    size=8,
                    ha="center",
                    va="center",
                    path_effects=[pe.withStroke(linewidth=1, foreground="white")],
                )
            # Set the display bounds
            ax.set_ylim(
                srca.gw.footprint_grid.total_bounds[1] - 10,
                srca.gw.footprint_grid.total_bounds[3] + 10,
            )
            ax.set_xlim(
                srca.gw.footprint_grid.total_bounds[0] - 10,
                srca.gw.footprint_grid.total_bounds[2] + 10,
            )
    title = (
        f"Image {bounds_by}"
        if bounds_by
        else str(Path(ref_image).name.split(".")[0]) + " as reference"
    )
    size = 12 if bounds_by else 8
    ax.set_title(title, size=size)
    plt.tight_layout(pad=1)

# %%
plot("union")
filenames
# %%
$$
   \begin{eqnarray}
      \begin{bmatrix} -2 \\ -2 \\ 1 \end{bmatrix}   \begin{bmatrix} 1 & 0 & 2 \\  0 & 1 & 2 \\ 0 & 0 & 1 \end{bmatrix}  =
      \begin{bmatrix} -2 \times 1 + -2 \times 0 + 1 \times 2  \\  -2 \times 0 + -2 \times 1 + 1 \times 2 \\ -2 \times 0 + -2 \times 0 + 1 \times 1  \end{bmatrix} = 
      \begin{bmatrix} 0  \\  0 \\ 1  \end{bmatrix}
   \end{eqnarray}
$$
# %%
place_name = "Edgewood Washington, DC, USA"
# import osmnx
import osmnx as ox
import geopandas as gpd

# Get place boundary related to the place name as a geodataframe
area = ox.geocode_to_gdf(place_name)
# %%
from geowombat.data import l8_224077_20200518_B4, l8_224078_20200518_B4

def plot(bounds_by, ref_image=None, cmap='viridis'):
    fig, ax = plt.subplots(dpi=200)
    with gw.config.update(ref_image=ref_image):
        with gw.open([l8_224077_20200518_B4, l8_224078_20200518_B4],
                        band_names=['nir'],
                        chunks=256,
                        mosaic=True,
                        bounds_by=bounds_by) as srca:
            # Plot the NIR band
            srca.where(srca != 0).sel(band='nir').plot.imshow(robust=True, cbar_kwargs={'label': 'DN'}, ax=ax)
            # Plot the image chunks
            srca.gw.chunk_grid.plot(color='none', edgecolor='k', ls='-', lw=0.5, ax=ax)
            title = f'Image {bounds_by}' if bounds_by else str(Path(ref_image).name.split('.')[0]) + ' as reference'
    size = 12 if bounds_by else 8
    ax.set_title(title, size=size)
    plt.tight_layout(pad=1)
# %%
# Import GeoWombat
import geowombat as gw

# import plotting
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

# load data
from geowombat.data import l8_224077_20200518_B2, l8_224078_20200518_B2

fig, ax = plt.subplots(dpi=200)
plot('union')

# %%

import geowombat as gw
from geowombat.data import rgbn
import matplotlib.pyplot as plt

fig, ax = plt.subplots(dpi=150)

# with gw.config.update(sensor='rgbn'):
with gw.open(rgbn, band_names=['red','green','blue','nir']) as ds:
    add_nir_red = ds.sel(band='nir') + ds.sel(band='red')
    add_nir_red.plot(robust=True, ax=ax)
    print(add_nir_red)
plt.tight_layout(pad=1)
# %%
fig, (ax1, ax2) = plt.subplots(dpi=150, ncols=2)

with gw.config.update(sensor='rgbn', scale_factor=0.0001):
    with gw.open(rgbn) as ds:
        ds.sel(band=['blue', 'green', 'red']).plot.imshow(robust=True, ax=ax1)
        evi = ds.gw.evi()
        evi.plot(robust=True, ax=ax2)

# Remove the legend from ax2
ax2.legend().set_visible(False)

plt.tight_layout(pad=1)
plt.show()

 fig, ax = plt.subplots(dpi=150)

with gw.config.update(sensor='rgbn', scale_factor=0.0001):
    with gw.open(rgbn) as ds:
        ds.sel(band=['blue', 'green', 'red']).plot.imshow(robust=True)
plt.tight_layout(pad=1)

# %%
fig, ax = plt.subplots(dpi=150)

with gw.config.update(sensor='qb', scale_factor=0.0001):
    with gw.open(rgbn) as ds:
        tcap = ds.gw.tasseled_cap()
        print('bands', tcap.band.values)
        tcap.sel(band='wetness').plot(robust=True, ax=ax)
        print(tcap)
plt.tight_layout(pad=1)
# %%

import geowombat as gw
from geowombat.data import rgbn
import matplotlib.pyplot as plt
# two figures with shared axes
fig, (ax1, ax2) = plt.subplots(dpi=150, ncols=2, sharey=True)

with gw.config.update(ref_crs=32618):
    with gw.open(rgbn, nodata=0) as src:
        # replace 0 with nan
        src = src.gw.mask_nodata()
        print(src.transform)
        print(src.crs)
        print(src.resampling)
        print(src.res)
        src.sel(band=[3,2,1]).plot.imshow( ax=ax1)
plt.tight_layout(pad=1)

proj4 = "+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

with gw.config.update(ref_crs=proj4):
    with gw.open(rgbn) as src:
        print(src.transform)
        print(src.crs)
        print(src.resampling)
        print(src.res)
        src.sel(band=[3,2,1]).plot.imshow( ax=ax2)

plt.tight_layout(pad=1)

# %%
import matplotlib.pyplot as plt
import geowombat as gw
from geowombat.data import l8_224077_20200518_B2, l8_224078_20200518_B2
fig, ax = plt.subplots(dpi=200)

filenames = [l8_224077_20200518_B2, l8_224078_20200518_B2]

with gw.open(
     filenames,
     band_names=['blue'],
     mosaic=True,
     bounds_by='union'
 ) as src:
     src.where(src != 0).sel(band='blue').gw.imshow(robust=True, ax=ax)
 

plt.tight_layout(pad=1)
# %%

import geowombat as gw
from geowombat.data import l8_224078_20200518, l8_224078_20200518_polygons
from geowombat.ml import fit, predict, fit_predict
import geopandas as gpd
from sklearn_xarray.preprocessing import Featurizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB
import matplotlib.pyplot as plt

le = LabelEncoder()

# The labels are string names, so here we convert them to integers
labels = gpd.read_file(l8_224078_20200518_polygons)
labels['lc'] = le.fit(labels.name).transform(labels.name)
print(labels)

pl = Pipeline([('scaler', StandardScaler()),
               ('pca', PCA()),
               ('clf', GaussianNB())])

param_grid={"scaler__with_std":[True,False],
            "pca__n_components": [1, 2, 3]
            }
fig, ax = plt.subplots(dpi=200,figsize=(5,5))

with gw.config.update(ref_res=150):
   with gw.open([l8_224078_20200518, l8_224078_20200518], 
                # time_names=['t1', 't2'], 
                stack_dim='band', 
                nodata=0) as src:
        y = fit_predict(src, pl, labels, col='lc')
        print(y)
        # plot one time period prediction
        y.plot(robust=True, ax=ax)
# %%
