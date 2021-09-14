#!/usr/bin/env python
# coding: utf-8

# (e_raster_reproject)=
# 
# ----------------
# 
# ```{admonition} Learning Objectives
# - Resample a raster with rasterio & geowombat
# - Learn how to match the extent
# ```
# ```{admonition} Review
# * [Affine transformation](d_affine)
# * [Raster Coordinate Reference Systems](d_raster_crs_intro)
# * [Reprojecting Rasters](e_raster_reproject.md)
# * [Interpolation Methods Explained](d_raster_crs_intro_interpolation_options)
# ```
# ----------------
# 
# # Resampling Rasters w. Rasterio and Geowombat
# 
# ## Why is Resampling Important?
# *Before you begin* any analysis using rater data it is critical that you have rasters that are "co-registered". Co-registration requires that any two rasters have the same resolution, and orientation - the origins can differ but they much align. *In other words, co-registration requires that cell centroids align perfectly for all intersecting areas.* Resampling is also extremely common during reprojection operations as it often requires changing the orientation, scale or resolution of an image. 
# 
# **Examples of data that is *not* co-registered**
# 
# ```{figure} ../_static/e_raster/Raster_diff-orientation.jpg
# :name: Resampling rasters - different orientation
# :width: 400px
# Resampling rasters - different orientation
# ```
# 
# ```{figure} ../_static/e_raster/Raster_diff-orientation-origin.jpg
# :name: Resampling rasters - different orientation and origin
# :width: 400px
# Resampling rasters - different orientation and origin
# ```
# ```{figure} ../_static/e_raster/Raster_diff-res.jpg
# :name: Resampling rasters - different resolution
# :width: 400px
# Resampling rasters - different resolution
# ```
# ## Methods for Resampling Explained
# There are [a number of methods](https://rasterio.readthedocs.io/en/latest/api/rasterio.enums.html#rasterio.enums.Resampling) to resample data, but they often take the form of "nearest neighbor", "bilinear", and "cubic convolusion" - these interpolation methods [are explained here in some detail](d_raster_crs_intro_interpolation_options.md). 
# 
# **resampling direction**
# - Upsampling - converting to higher resolution/smaller cells. 
# - Downsampling - converting to lower resolution/larger cell sizes.
# 
# 
# ## Simple Up/Downsampling in Rasterio & Geowombat
# ### Rasterio Upsampling Example
# Occationally you will need to resample your data by some factor, for instance you might want data upsampled to a courser resolution due to memory constraints. 
# 
# 
# Here's an example of how to generate the `data` array and the `transform` needed to write it out. We will start by simply reading in the data and coersing a higher resolution, by adding more rows and columns. To understand the `transform`, let's review [affine transformations](d_affine). Here we will update the scale values with the new resolution using $S_{y}$ and $S_{x}$ show below
# 
# $$
#    \begin{eqnarray}
#    \mbox{Scale transform: }  \begin{bmatrix} S_{x} & 0 & 0 \\ 0 & S_{y} & 0 \\ 0 & 0 & 1 \end{bmatrix} 
#    \end{eqnarray}
# $$

# In[1]:


import rasterio
from rasterio.enums import Resampling

image = "../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF"

upscale_factor = 2

with rasterio.open(image) as dataset:

    # resample data to target shape using upscale_factor
    data = dataset.read(
        out_shape=(
            dataset.count,
            int(dataset.height * upscale_factor),
            int(dataset.width * upscale_factor)
        ),
        resampling=Resampling.bilinear
    )

    print('Shape before resample:', dataset.shape)
    print('Shape after resample:', data.shape[1:])

    # scale image transform
    dst_transform = dataset.transform * dataset.transform.scale(
        (dataset.width / data.shape[-1]),
        (dataset.height / data.shape[-2])
    )

    print('Transform before resample:\n', dataset.transform, '\n')
    print('Transform after resample:\n', dst_transform)

    ## Write outputs
    # set properties for output
    # dst_kwargs = src.meta.copy()
    # dst_kwargs.update(
    #     {
    #         "crs": dst_crs,
    #         "transform": dst_transform,
    #         "width": data.shape[-1],
    #         "height": data.shape[-2],
    #         "nodata": 0,  
    #     }
    # )

    # with rasterio.open("../temp/LC08_20200518_15m.tif", "w", **dst_kwargs) as dst:
    #     # iterate through bands
    #     for i in range(data.shape[0]):
    #           dst.write(data[i].astype(rasterio.uint32), i+1)


# ```{admonition} Reminder
# Read up on [affine transformations](d_affine_transform_matrix) to help you understand the `transform.scale` function above. 
# ```
# 
# ### Geowombat Upsampling Example
# As always the easiest way to deal with resampling is by deploying geowombat. It's like a swiss army knife for kicking raster butt. Here we just need to set the desired resolution with `ref_res`, and the `resampling` method in the open statement. Writing a file is a bit more intuitive too.

# In[2]:


import geowombat as gw
 
image = "../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF"

with gw.config.update(ref_res=15):
    with gw.open(image, resampling="bilinear") as src:
        print(src)
        
        # to write out simply:
        # src.gw.to_raster(
        #     "../temp/LC08_20200518_15m.tif",
        #     overwrite=True,
        # ) 


# Much.... easier.... 
# 
# 
# ## Co-registering Rasters (Aligning cells)
# One common problem is how to get raster data to align on a cell by cell basis so you can complete your analysis. We will walk through how to do this for both rasterio and geowombat. In the following example we will learn how to align rasters with different origins, resolutions, or orientations. 
# 
# Our example data will look at registering LandSat data with precipitation data from CHIRPS. 
# 
# ### Example of Co-registering Rasters with Geowombat
# Co-registering data is simple in geowombat, you simply need to choose an reference image to match the bounds, CRS, and cell size. 
# 
# The original input data `precip` is currently 500m but will be upsampled to 30m as seen in `print(src)`.  Also note the use of `nodata` to avoid missing values stored as -9999.

# In[3]:


import geowombat as gw
import matplotlib.pyplot as plt
fig, ax = plt.subplots(dpi=200)


LS = "../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF"
precip = "../data/precipitation_20200601_500m.tif"

with gw.config.update(ref_image=LS):
    with gw.open(precip, resampling="bilinear", nodata=-9999) as src:
        print(src)
        ax.imshow(src.data[0])
        
        # to write out simply:
        # src.gw.to_raster(
        #     "../temp/precip_20200601_30m.tif",
        #     overwrite=True,
        # ) 


# Although it's a bit hard to tell, the cell size is now 30m (see the slices of the larger original cells at the top of the image).
# 
# ```{admonition} Note
# Also note that geowombat's built in `.imshow` functionality doesn't currently work for single band images. To get an image we have to extract a `np.ndarray` that has the shape `(1, 1860, 2041)`. Where `(1,.,.)` is the band, so to get a 2d array we select `data[0]`. We also avoid missing values (-9999).
# ```
