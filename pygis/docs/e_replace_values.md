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
  "description lang=en": "Learn how to replace values in a raster using rasterio and GeoWombat."
  "keywords": "geospatial, raster, replace, interpolation"
  "property=og:locale": "en_US"
---

# Replacing Values w. Rasterio

----------------

```{admonition} Learning Objectives
* Replace and interpolate values in a raster with `rasterio`
```
```{admonition} Review
* [Geospatial Raster Data](c_rasters.md)
```

----------------

Imagery may sometimes have errors due to factors such as noise, distortion, or sensor errors. Some pixels may have extremely high or low values or no value at all. One way to resolve this issue is to manually replace a pixel value with another pixel value. Another option is to interpolate the pixel value based on the values of the pixel's neighbors.

We'll explore how to replace raster values with `rasterio`.

## Setup

First, we will import our modules.

```{code-cell} ipython3
:tags: ["hide-cell"]

# Import modules
import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.transform import Affine
from rasterio.fill import fillnodata
```

Next, we will generate a sample raster to be used.

```{code-cell} ipython3
:tags: ["hide-cell"]

# Generate mesh grid for rasters
x = np.linspace(-90, 90, 200)
y = np.linspace(90, -90, 200)
X, Y = np.meshgrid(x, y)

# Generate values for mesh grid
Z1 = np.abs(((X - 10) ** 2 + (Y - 10) ** 2) / 1 ** 2)
Z2 = np.abs(((X + 10) ** 2 + (Y + 10) ** 2) / 2.5 ** 2)

# Generate raster values
Z = (Z1 - Z2)

# Set transform
xres = (x[-1] - x[0]) / len(x)
yres = (y[-1] - y[0]) / len(y)
transform = Affine.translation(x[0] - xres / 2, y[0] - yres / 2) * Affine.scale(xres, yres)

# Save raster
with rasterio.open(
        "../temp/replace_values_raster.tif",
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
```

## Replace values with `rasterio`

```{code-cell} ipython3
# Open raster and plot
raster_file = rasterio.open("../temp/replace_values_raster.tif")
raster = raster_file.read(1)
plt.imshow(raster, cmap="BrBG")
plt.title("Raster")
plt.show()
```

### Replace values with a specified number

Let's say that we want to change the pixel value at row 150, column 100 because it's wrong. We can simply call that pixel value by its row index and column index.

```{code-cell} ipython3
# Replace value with 0 at one location
raster[150, 100] = 0
raster[150, 100]
```

We can also change multiple pixel values by slicing.

```{code-cell} ipython3
# Replace values with 0 at multiple locations
raster[99:102, 6:9] = 0
raster[99:102, 6:9]
```

Finally, we can change any pixel values that are of a certain value.

```{code-cell} ipython3
# Replace values with 0 if they equal a certain number (in this case, 13776)
raster[raster == 13776] = 0
raster
```

### Replace values through interpolation

Sometimes, we don't know or have an exact value to replace pixel values with. We can "fill in" those pixel values through interpolation. Recall that interpolation uses the pixel values surrounding a certain pixel to determine the value for that certain pixel.

`Rasterio` provides a function `fillnodata()` that does this for us. In addition to specifying a raster, we also need to provide a mask, which tells the function which pixel values need to be filled in. The mask can either be an array of Boolean values (`True` or `False`, where `False` indicates pixels to be filled in) or numbers (where values equal to `0` indicate pixels to be filled in).

For more information this function, see the [function documentation](https://rasterio.readthedocs.io/en/latest/api/rasterio.fill.html).

```{important} Mask must be in the same shape (number of rows and columns) as the input raster.
```

Below, we will interpolate the pixels whose values are equal to 0.

```{code-cell} ipython3
# Create a Boolean mask (True/False), with a value of False for pixels that equal 0
mask_boolean = (raster != 0)
mask_boolean
```

```{code-cell} ipython3
# Create a value mask, with a value of 0 for pixels that equal 0
mask_numbers = np.zeros_like(raster)
mask_numbers[raster > 0] = 255
mask_numbers
```

```{code-cell} ipython3
# Fill in missing values with interpolation
# Can use either a Boolean mask or a value mask
fillnodata(raster, mask = mask_boolean, max_search_distance = 1000)
```

Finally, we can check the raster values to see the interpolated values.

```{code-cell} ipython3
# Print raster array
raster
```

```{code-cell} ipython3
# Print subset of raster around row 150, column 100
raster[148:153, 98:103]
```

```{code-cell} ipython3
# Print subset of raster around rows 99-101, columns 6-8]
raster[97:104, 4:11]
```

## Replace values with `GeoWombat`

For replacing raster values with `GeoWombat`, see the chapter on [Editing Rasters and Remotely Sensed Data](f_rs_edit.md).
