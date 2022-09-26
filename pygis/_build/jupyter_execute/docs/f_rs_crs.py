#!/usr/bin/env python
# coding: utf-8

# (f_rs_crs)=
# 
# 
# ----------------
# 
# ```{admonition} Learning Objectives
# - Reproject remotely sensed data (change CRS)
# - Reproject on-the-fly
# - Understand resampling options
# ```
# ```{admonition} Review
# * [What is a CRS](d_crs_what_is_it.md)
# * [Understanding CRS codes](d_understand_crs_codes.md)
# * [Raster CRS](d_raster_crs_intro.md)
# ```
# ----------------
# 
# 
# # Remote Sensing Coordinate Reference Systems
# 
# Image projections can be transformed in GeoWombat using the configuration manager (see [Config Manager](f_rs_config.md)). With the configuration manager, the CRS is transformed using [rasterio CRS](https://rasterio.readthedocs.io/en/latest/api/rasterio.crs.html) and [virtual warping](https://rasterio.readthedocs.io/en/latest/topics/virtual-warping.html). For references, see [Spatial Reference](https://spatialreference.org/) and [epsg.io](http://epsg.io/).
# 
# ## View Image Coordinate Reference System & Properties
# In the following we will print out the properties relevant to CRS for the red, green blue image. The CRS can be accessed from the [xarray.DataArray](http://xarray.pydata.org/en/stable/generated/xarray.DataArray.html) attributes.

# In[1]:


import geowombat as gw
from geowombat.data import rgbn

with gw.open(rgbn) as src:
    print(src.transform)
    print(src.gw.transform)
    print(src.crs)
    print(src.resampling)
    print(src.res)
    print(src.gw.cellx, src.gw.celly)


# ## Transforming a CRS On-The-Fly
# 
# To transform the CRS, use the context manager. In this example, an proj4 code is used. See [understanding CRS codes](d_understand_crs_codes.md) for more details. Also note the use the `nodata` in this case the file `rgbn` doesn't have the missing data value set in its profile, so we can set it manually when opened.

# In[2]:


import matplotlib.pyplot as plt
fig, ax = plt.subplots(dpi=200)

proj4 = "+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

with gw.config.update(ref_crs=proj4):
    with gw.open(rgbn, nodata=0) as src:
        # replace 0 with nan
        src = src.gw.mask_nodata()
        print(src.transform)
        print(src.crs)
        print(src.resampling)
        print(src.res)
        src.sel(band=[3,2,1]).plot.imshow(robust=True, ax=ax)

plt.tight_layout(pad=1)


# Other formats supported by rasterio, (e.g., PROJ4 strings) can be used.

# In[3]:


with gw.config.update(ref_crs=proj4):
    with gw.open(rgbn) as src:
        print(src.transform)
        print(src.crs)
        print(src.resampling)
        print(src.res)


# ## Resampling the Cell Size
# 
# The resampling algorithm can be specified in the `geowombat.open` function. Here, we use cubic convolution resampling to warp the data to EPSG code 31972 (a UTM projection).

# In[4]:


with gw.config.update(ref_crs=31972):
    with gw.open(rgbn, resampling='cubic') as src:
        print(src.transform)
        print(src.crs)
        print(src.resampling)
        print(src.res)


# The transformed cell resolution can be added in the context manager. Here, we resample the data to 10m x 10m spatial resolution.

# In[5]:


with gw.config.update(ref_crs=31972, ref_res=(10, 10)):
    with gw.open(rgbn, resampling='cubic') as src:
        print(src.transform)
        print(src.crs)
        print(src.resampling)
        print(src.res)


# ## Transformations Outside Context Manager
# 
# To transform an `xarray.DataArray` outside of a configuration context, use the `geowombat.transform_crs` function.

# In[6]:


with gw.open(rgbn) as src:
    print(src.transform)
    print(src.crs)
    print(src.resampling)
    print(src.res)
    print('')
    src_tr = src.gw.transform_crs(proj4, dst_res=(10, 10), resampling='bilinear')
    print(src_tr.transform)
    print(src_tr.crs)
    print(src_tr.resampling)
    print(src_tr.res)


# For more help we can read through the docs a bit.

# In[7]:


with gw.open(rgbn, resampling='cubic') as src:
    print(help(src.gw.transform_crs))

