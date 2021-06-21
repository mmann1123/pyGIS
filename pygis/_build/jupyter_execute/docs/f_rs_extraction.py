#!/usr/bin/env python
# coding: utf-8

# (f_rs_extraction)=
# 
# 
# ---------------
# ```{admonition} Learning Objectives
#   - Subset bands by index or name
#   - Extract raster data by row and column number
#   - Extract data by bounding window
#   - Extract raster data by coordinates
#   - Extract raster data by geometry (point, polygon)
# ```
# ```{admonition} Review
# * [Data Structures](c_features.md)
# * [Raster Data ](c_rasters.md)
# * [Reading and writing remotely sensed data ](f_rs_io.md)
# ```
# --------------
# 
# 
# # Raster Data Extraction
# Raster data is often of little use unless we can extract and summarize the data. For instance, extracting raster to points by coordinates allows us to pass data to machine learning models for land cover classification or cloud masking. 
# 
# ## Subsetting rasters
# We can subset sections of the data array in a number of ways. In this case we will create a slice based on row and column location to subset LandSat data using a `rasterio.window.Window`.
# 
# Either a `rasterio.window.Window` object or tuple can be used with `geowombat.open`.

# In[1]:


import geowombat as gw
from geowombat.data import rgbn

from rasterio.windows import Window
w = Window(row_off=0, col_off=0, height=100, width=100)

with gw.open(rgbn,
                band_names=['blue', 'green', 'red'],
                num_workers=8,
                indexes=[1, 2, 3],
                window=w,
                out_dtype='float32') as src:
    print(src)


# We can also slice a subset of data using a tuple of bounded coordinates.
# 
# ``` python
# bounds = (793475.76, 2049033.03, 794222.03, 2049527.24)
# 
# with gw.open(rgbn,
#                 band_names=['green', 'red', 'nir'],
#                 num_workers=8,
#                 indexes=[2, 3, 4],
#                 bounds=bounds,
#                 out_dtype='float32') as src:
#     print(src)
# ```
# 
# The configuration manager provides an alternative method to subset rasters. See `tutorial-config` for more details.
# 
# ``` python
# with gw.config.update(ref_bounds=bounds):
# 
#     with gw.open(rgbn) as src:
#         print(src)
# ```
# 
# By default, the subset will be returned by the upper left coordinates of the bounds, potentially shifting cell alignment with the reference raster. To subset a raster and align it to the same grid, use the **ref_tar** keyword. This is equivalent to a "snap raster" in ArcGIS. 
# 
# ``` python
# with gw.config.update(ref_bounds=bounds, ref_tar=rgbn):
# 
#     with gw.open(rgbn) as src:
#         print(src)
# ```
# 
# ## Extracting data by coordinates
#  
# To extract values at a coordinate pair, translate the coordinates into array indices. For extraction by geometry, for instance with a shapefile, see [extract by point geometry](f_rs_extraction_point).

# In[2]:


import geowombat as gw
from geowombat.data import l8_224078_20200518

# Coordinates in map projection units
y, x = -2823031.15, 761592.60

with gw.open(l8_224078_20200518) as src:
    # Transform the map coordinates to data indices
    j, i = gw.coords_to_indices(x, y, src)
    # Subset by index
    data = src[:, i, j].data.compute()

print(data.flatten())


# A latitude/longitude pair can be extracted after converting to the map projection.

# In[3]:


import geowombat as gw
from geowombat.data import l8_224078_20200518

# Coordinates in latitude/longitude
lat, lon = -25.50142964, -54.39756038

with gw.open(l8_224078_20200518) as src:
    # Transform the coordinates to map units
    x, y = gw.lonlat_to_xy(lon, lat, src)
    # Transform the map coordinates to data indices
    j, i = gw.coords_to_indices(x, y, src)
    data = src[:, i, j].data.compute()

print(data.flatten())


# (f_rs_extraction_point)=
# ## Extracting data with point geometry 
# 
# In the example below, 'l8_224078_20200518_points' is a [GeoPackage](https://www.geopackage.org/) of point locations, and the output `df` is a [GeoPandas GeoDataFrame](https://geopandas.org/docs/reference/api/geopandas.GeoDataFrame.html?highlight=geodataframe#geopandas.GeoDataFrame). To extract the raster values at the point locations, use `geowombat.extract`.

# In[4]:


import geowombat as gw
from geowombat.data import l8_224078_20200518, l8_224078_20200518_points

with gw.open(l8_224078_20200518) as src:
    df = src.gw.extract(l8_224078_20200518_points)

print(df)


# ```{note} 
# 
# The line `df = src.gw.extract(l8_224078_20200518_points)` could also have been written as `df = gw.extract(src, l8_224078_20200518_points)`.
# ```
# 
# In the previous example, the point vector had a CRS that matched the raster (i.e., EPSG=32621, or UTM zone 21N). If the CRS had not matched, the `geowombat.extract` function transforms the CRS on-the-fly.

# In[5]:


import geowombat as gw
from geowombat.data import l8_224078_20200518, l8_224078_20200518_points
import geopandas as gpd

point_df = gpd.read_file(l8_224078_20200518_points)
print(point_df.crs)

# Transform the CRS to WGS84 lat/lon
point_df = point_df.to_crs('epsg:4326')
print(point_df.crs)

with gw.open(l8_224078_20200518) as src:
    df = src.gw.extract(point_df)

print(df)


# Set the data band names using `sensor = 'bgr'`, which assigns the band names blue, green, red.

# In[6]:


import geowombat as gw
from geowombat.data import l8_224078_20200518, l8_224078_20200518_points

with gw.config.update(sensor='bgr'):
    with gw.open(l8_224078_20200518) as src:
        df = src.gw.extract(l8_224078_20200518_points,
                            band_names=src.band.values.tolist())

print(df)


# ## Extracting time series images by point geometry
# We can also easily extract a time series of raster images. Extracted pixel values are provided in 'wide' format with appropriate labels, for instance the column 't2_blue' would be the blue band for the second time period

# In[7]:


from geowombat.data import l8_224078_20200518, l8_224078_20200518_points

with gw.config.update(sensor='bgr'):
    with gw.open([l8_224078_20200518, l8_224078_20200518],
            time_names=['t1', 't2'],
            stack_dim='time') as src:

        # Extract and by point geometry
        df = src.gw.extract(l8_224078_20200518_points)

print(df)


# ## Extracting data by polygon geometry
# 
# To extract values within polygons, use the same `geowombat.extract` function.

# In[8]:


from geowombat.data import l8_224078_20200518, l8_224078_20200518_polygons

with gw.config.update(sensor='bgr'):
    with gw.open(l8_224078_20200518) as src:
        df = src.gw.extract(l8_224078_20200518_polygons,
                            band_names=src.band.values.tolist())

    print(df)


# ### Calculate mean pixel value by polygon
# It is simple then to calculate the mean value of pixels within each polygon by using the polygon `id` column and pandas groupby function. You can easily calculate other statistics like min, max, median etc.

# In[9]:


from geowombat.data import l8_224078_20200518, l8_224078_20200518_polygons

with gw.config.update(sensor='bgr'):
    with gw.open(l8_224078_20200518) as src:
        df = src.gw.extract(l8_224078_20200518_polygons,
                            band_names=src.band.values.tolist())
        # use pandas groupby to calc pixel mean  
        df = df.groupby('id').mean()
    print(df)

