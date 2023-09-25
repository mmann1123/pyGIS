---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
myst:
  html_meta:
    "description lang=en": "Learn how to perform mathematical operations on raster bands using rasterio."
    "keywords": "spatial, python, rasterio, raster, band, math"
    "property=og:locale": "en_US"
---

# Band Math w. Rasterio

----------------

```{admonition} Learning Objectives
* Conduct mathematical operations on raster bands with rasterio
* Understand the requirements for successful mathematical operations
```
```{admonition} Review
* [Reproject Rasters w. Rasterio and Geowombat](e_raster_reproject.md)
* [Resampling Rasters w. Rasterio and Geowombat](e_raster_resample.md)
```

----------------

Band math is useful when you want to perform a mathematical operation to each pixel value in a raster. You might find band math helpful for calculating NDVI or multiplying all values by a constant.

## Setup

To begin, we will import our modules (click the + below to show code cell).

```{code-cell} ipython3
:tags: ["hide-cell"]

# Import modules
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import Affine
```

## Band Math with rasterio with multiple images

`Rasterio` makes band math relatively straightforward since the rasters are essentially read in as numpy arrays, so you can perform math on the raster arrays just like any numpy array.

```{attention}
Mathematical operations on rasters using `rasterio` are not spatially aware. Any mathematical operation with multiple rasters will work even if the rasters are not representing the same geographical extent. Consequently, you need to ensure that the cell size and extent represented in all rasters are the same. In other words, if you are using two rasters in a mathematical operation, they must have the same shape (same number of rows and columns).
```

In this example we will write two raster files to the disk: `math_raster_a.tif` and `math_raster_b.tif`. We will then read then back in and do math on them. Let's generate some rasters (click the + below to show code cell).

```{code-cell} ipython3
:tags: ["hide-cell"]

# Generate mesh grid for rasters
x = np.linspace(-90, 90, 6)
y = np.linspace(90, -90, 6)
X, Y = np.meshgrid(x, y)

# Generate values for mesh grid
Z1 = np.abs(((X - 10) ** 2 + (Y - 10) ** 2) / 1 ** 2)
Z2 = np.abs(((X + 10) ** 2 + (Y + 10) ** 2) / 2.5 ** 2)
Z3 = np.abs(((X + 3) + (Y - 8) ** 2) / 3 ** 2)

# Generate raster values for two rasters
Z_a = (Z1 - Z2)
Z_b = (Z2 - Z3)

# Set transform
xres = (x[-1] - x[0]) / len(x)
yres = (y[-1] - y[0]) / len(y)
transform = Affine.translation(x[0] - xres / 2, y[0] - yres / 2) * Affine.scale(xres, yres)

# Save first raster
with rasterio.open(
        "../temp/math_raster_a.tif",
        mode="w",
        driver="GTiff",
        height=Z_a.shape[0],
        width=Z_a.shape[1],
        count=1,
        dtype=Z_a.dtype,
        crs="+proj=latlong",
        transform=transform,
) as new_dataset:
        new_dataset.write(Z_a, 1)

# Save second raster
with rasterio.open(
        "../temp/math_raster_b.tif",
        mode="w",
        driver="GTiff",
        height=Z_b.shape[0],
        width=Z_b.shape[1],
        count=1,
        dtype=Z_b.dtype,
        crs="+proj=latlong",
        transform=transform,
) as new_dataset:
        new_dataset.write(Z_b, 1)
```

Next, we'll view the raster values.

```{code-cell} ipython3
# Open raster and plot
raster_a = rasterio.open("../temp/math_raster_a.tif").read(1)
plt.imshow(raster_a, cmap = "BrBG")
plt.title("Raster A")
plt.show()

# View raster values
print(raster_a)
```

```{code-cell} ipython3
# Open raster and plot
raster_b = rasterio.open("../temp/math_raster_b.tif").read(1)
plt.imshow(raster_b, cmap = "BrBG")
plt.title("Raster B")
plt.show()

# View raster values
print(raster_b)
```

### Example band math operations

We can get the difference between the two rasters.

```{code-cell} ipython3
# Get difference
difference_a_b = raster_a - raster_b

# Plot raster
plt.imshow(difference_a_b, cmap = "BrBG")
plt.title("Difference between Raster A & Raster B")
plt.show()

# Show raster values
print("Raster values:\n", difference_a_b)
```

We can multiply a raster by a constant.

```{code-cell} ipython3
# Get product
product_a = raster_a * 2

# Plot raster
plt.imshow(product_a, cmap = "BrBG")
plt.title("Product of Raster A and 2")
plt.show()

# Show raster values
print("Raster values:\n", product_a)
```

### Band math with NoData values

If a pixel has a value of `nan`, `None`, or `NoData` value, those pixels will automatically be ignored in any band math. The output raster will maintain the `nan`, `None`, or `NoData` value at that pixel location.

Not all rasters, however, use those values to signify that a pixel has no value. Some rasters might use 0 or another number to indicate no value. In that case, we have to explicitly mark that pixel to be skipped.

```{code-cell} ipython3
# Create a copy of first raster
raster_0 = raster_a.copy()

# Set a pixel value to 0 as an example, which will signify NoData
# (top right pixel)
raster_0[0, 5] = 0

# Mask out any NoData (0) values
raster_0_masked = np.ma.masked_array(raster_0, mask = (raster_0 == 0))

# Get difference between masked raster and second raster
difference_0_b = raster_0_masked - raster_b

# Plot raster
plt.imshow(difference_0_b, cmap = "BrBG")
plt.title("Difference between Raster A with NoData values & Raster B")
plt.show()

# Show raster values
print("Raster values:\n", difference_0_b)
```

### Example: Calculating NDVI

In the example below, we will read in a clipped Landsat 8, Collection 2 Level-2 image and use the band math concepts to calculate the normalized difference vegetation index (NDVI) for the image. As you may recall, NDVI is a spectral approach used to assess vegetation. The formula for NDVI is:

$$
  NDVI = \frac{NIR - Red}{NIR + Red}
$$

where `NIR` is the near-infrared band and `Red` is the red band.

High NDVI values (towards 1) reflect a higher density of green vegetation, and low values (towards -1) reflect a lower density.

```{code-cell} ipython3
# Open raster (Landsat 8, Collection 2 Level-2)
# Band 1 - Blue, Band 2 - Green, Band 3 - Red, Band 4 - Near Infrared
# Source: https://www.usgs.gov/centers/eros/science/usgs-eros-archive-landsat-archives-landsat-8-9-olitirs-collection-2-level-2
with rasterio.open("../data/LC08_L2SP_016040_20210317_20210328_02_T1_clip.tif", mode = "r", nodata = 0) as src:

    # Get red band
    band_red = src.read(3)

    # Get NIR band
    band_nir = src.read(4)

    # Allow division by zero
    np.seterr(divide = "ignore", invalid = "ignore")

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
```

## Band Math with GeoWombat

For band math with `GeoWombat`, see the chapter on [Band Math & Vegetation Indices](f_rs_band_math.md).
