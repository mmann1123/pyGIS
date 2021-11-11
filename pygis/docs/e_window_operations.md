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
  "description lang=en": "Learn how to conduct moving window operations over rasters."
  "keywords": "geospatial, raster, moving window, window operations, filter"
  "property=og:locale": "en_US"
---

# Window Operations w. Rasterio and GeoWombat

----------------

```{admonition} Learning Objectives
* Conduct and understand window operations with `rasterio`
* Conduct window operations with `GeoWombat`
```
```{admonition} Review
* [Geospatial Raster Data](c_rasters.md)
```

----------------

## Background

Moving windows or filters are often used in raster analysis. For example, they can be used to obtain the maximum value within a certain neighborhood, to smooth out values, or detect holes or edges (i.e., where pixel values that are near each other change abruptly).

These moving windows can also be called filters or kernels. They can be of many different sizes and shapes (the most common is 3-cell-by-3-cell rectangular window) and can have different or the same values for each cell. The center of the filter can be called the target cell or the center pixel, and the surrounding cells are referred to as the neighbors.

The filter passes through each non-edge cell in the raster. For a pass, each cell in the filter is matched with a cell from the input raster based on their location relative to the center pixel (e.g., a cell that is 1 to the left of the center pixel on the input raster is matched with the cell that is 1 to the left of the center pixel on the filter). The filter then pulls the values from the neighboring cells and the center pixel itself, performs a calculation based on the filter values, reports that resulting value back to the identical location of the original pixel, moves to the next pixel, and repeats the process.

For more information on moving windows, see the ["Neighborhood Operations" section in this chapter on raster geoprocessing](https://saylordotorg.github.io/text_essentials-of-geographic-information-systems/s12-02-scale-of-analysis.html).

```{attention}
With window operations, the edge pixels will generally be cut out from the output because those edge pixels do not have neighboring pixels all around it. As window operations generally require a pixel to be surrounded on all four sides, we cannot perform calculations on these edge pixels. The pixels that constitute the "edge" depends on the shape of the kernel. For example, a `3x3` kernel only requires 1 neighboring pixel in each direction, so only the outer ring of pixels will be cut out from the output. A `5x5` kernel requires 2 neighboring pixels in each direction, so the two outer rings of pixels will be cut out.
```

### Python implementation

The most intuitive way to perform window operations in Python is to use a `for` loop. With this method, we would iterate through each non-edge pixel, obtain the surrounding pixel values and the center pixel value, perform some sort of calculation, report that resulting value back to the identical location of the original pixel, move to the next pixel, and repeat the process. Iterating through each pixel, however, has the potential to be extremely time and computationally intensive (there could be many, many pixels).

To mitigate this limitation, instead of using a `for` loop, we can get each neighbor value simultaneously for all non-edge pixels. Another way to think of it is that instead of using a `for` loop to iterate through each pixel to get neighboring values, we can iterate through each kernel position to get the neighboring value corresponding to a certain kernel position for all non-edge pixels at once. This is what a vectorized sliding window does.

The vectorized sliding window is grounded in the concept that each position in the kernel has a certain relative position or offset (e.g., one pixel to the left) from the center pixel of the kernel. This method works because each pixel in a raster is in essence a neighbor to at least one other pixel. The vectorized sliding window simply offsets itself within the raster array extent so that each pixel that falls within the vectorized sliding window is the neighbor of the same relative position (e.g., one pixel to the left) to its center pixel.

A vectorized sliding window is created for each position in the kernel. The vectorized sliding window of a certain kernel position is applied over the raster and obtains--all at once--the neighboring pixel value corresponding to that kernel position for all non-edge pixels. The size of vectorized sliding window is dependent on the size of the raster and kernel but will always fall between the two.

For more conceptual information on vectorized sliding windows and how they compare to iterating through each pixel, see [this article](https://opensourceoptions.com/blog/vectorize-moving-window-grid-operations-on-numpy-arrays/).

## Setup

We'll explore two methods, one using `rasterio` and another using `GeoWombat`.

First, we'll import our modules.

```{code-cell} ipython3
:tags: ["hide-cell"]

# Import modules
import geowombat as gw
import numpy as np
from itertools import product
import rasterio
from rasterio.transform import Affine
import matplotlib.pyplot as plt
```

## Window operations with `rasterio`

Let's create a raster.

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

# Generate raster values
Z = (Z1 - Z2)

# Set transform
xres = (x[-1] - x[0]) / len(x)
yres = (y[-1] - y[0]) / len(y)
transform = Affine.translation(x[0] - xres / 2, y[0] - yres / 2) * Affine.scale(xres, yres)

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
```

## Create kernel

Second, we can generate a kernel array. The array can consist of a single value or multiple values.

```{important} The kernel should have an odd number of rows and columns and should not have more rows and columns than the input raster.
```

```{tip}
To create a non-rectangular shape, simply add `0`s in the kernel positions to be ignored.
```

```{code-cell} ipython3
# Create a kernel
# Example kernel A
kernel = np.array([[2, 2, 2, 2, 2],
       [2, 2, 2, 2, 2],
       [2, 2, 2, 2, 2],
       [2, 2, 2, 2, 2],
       [2, 2, 2, 2, 2]])

# Example kernel B
kernel = np.full((3, 3), 1)

# Get kernel shape
kernel_shape = kernel.shape

# Convert the kernel to a flattened array
kernel_array = np.ravel(kernel)
```

## Create output arrays

Next, we will create two arrays that will store our calculations.

The first array is the output array, which has the same shape as that of the input raster. We will initially fill the array with placeholder values. This array will be the final result that is exported and saved.

```{code-cell} ipython3
# Create raster array with placeholder values in shape of raster
output_rio = np.full((raster.shape[0], raster.shape[1]), -9999)

# Set array data type
output_rio = output_rio.astype(np.float64) ###

# Display raster array with placeholder values
print(output_rio)
```

The second array, initially filled with `0`s, will hold the running aggregate for the calculated values from each vectorized sliding window. Since we are not performing calculations on any edge pixels, the shape of this array is slightly smaller than that of the input raster and also dependent on the shape of the kernel. This array will be inserted into and replace the non-edge placeholder values in the output array (which we just created).

```{code-cell} ipython3
# Create raster array used to store window operation calculations for each pixel (excluding boundary pixels)
aggregate = np.full((raster.shape[0] - kernel_shape[0] + 1, raster.shape[1] - kernel_shape[1] + 1), 0)

# Set array data type
aggregate = aggregate.astype(np.float64)

# Display raster array
print(aggregate)
```

## Create and implement vectorized sliding window

The next step is to generate the vectorized sliding windows. The shape of the vectorized sliding windows depends on the kernel shape, so we utilize indices and slicing to obtain the extent of a vectorized sliding window for each position in the kernel.

```{code-cell} ipython3
# Generate row index pairs for slicing
pairs_x = list(zip([None] + list(np.arange(1, kernel_shape[0])), list(np.arange(-kernel_shape[0] + 1, 0)) + [None]))

# Generate column index pairs for slicing
pairs_y = list(zip([None] + list(np.arange(1, kernel_shape[1])), list(np.arange(-kernel_shape[1] + 1, 0)) + [None]))

# Combine row and column index pairs together to get the extent for each vectorized sliding window
combos = list(product(pairs_x, pairs_y))

# Display combined pairs
print(combos)
```

Once the vectorized sliding windows are specified, we can apply them to the raster. The vectorized sliding window will get a subset of the raster array, and we can multiply all the pixel values in that subset by the corresponding value in the kernel, which is based on window's specific kernel position.

The product is then added to the array that keeps track of the running total.

```{code-cell} ipython3
# Create empty list to store each window operation calculation
sub_array_list = []

# Iterate through the combined pairs (which give extent of a sliding window)
for p in range(len(combos)):

    # Get the sub-array via slicing and multiply all the values by corresponding value in kernel (based on location)
    sub_array = raster[combos[p][0][0]:combos[p][0][1], combos[p][1][0]:combos[p][1][1]] * kernel_array[p]

    # Add sub-array values to array storing window operation calculations
    aggregate += sub_array

    # Add sub-array to list
    sub_array_list.append(sub_array)

# View array storing window operation calculations
print(aggregate)
```

Once we get the aggregate of all windows, we can perform additional computations. In this case, we calculate the average pixel value.

```{code-cell} ipython3
# Get average value
aggregate = aggregate / len(kernel_array)

# View array storing window operation calculations
print(aggregate)
```

### Non-mathematical window operations

We can also perform non-mathematical window operations, such as getting the maximum value of a pixel and its surrounding pixels. We simply take the calculations from each vectorized sliding window and get the maximum value from those calculations.

```{tip}
To get the maximum or minimum value of a pixel and its surrounding neighbors, the kernel should be filled with values of `1` so that the pixel values don't change.
```

```{code-cell} ipython3
# Get maximum value
window_maximum = np.maximum.reduce(sub_array_list)
print(window_maximum)
```

## Save output

We can insert the processed aggregate array into the output array, with each value replacing the placeholder value at its corresponding original position in the array. Recall that because edge pixels are ignored, the edge pixels of the output array will still keep their placeholder values.

In this example, each non-edge output pixel value is the average pixel value--with pixel values drawn from the input raster--of the 8 pixels surrounding that pixel and the pixel itself.

```{code-cell} ipython3
# Use kernel shape to determine the row and column index extent of the calculated array
n = int((kernel_shape[0] - 1) / 2)
m = int((kernel_shape[1] - 1) / 2)

# Replace placeholder values in the output array with the corresponding values (based on location) from the calculated array
output_rio[n:-n, m:-m] = aggregate

# Display output array
print(output_rio)
```

Finally, we can export the raster.

```{code-cell} ipython3
:tags: ["hide-cell"]

# Export raster
with rasterio.open(
        "../temp/raster_window_3x3_average.tif", "w",
        driver="GTiff",
        transform = src.transform,
        dtype=rasterio.float64,
        count=1,
        width=src.width,
        height=src.height) as dst:
    dst.write(output_rio, indexes=1)
```

## Window operations with `GeoWombat`

We can use `GeoWombat` for window operations if we're only interested in calculating a statistic. The code to do this with `GeoWombat` is less complex and much shorter than with `rasterio`--we can simply use the `geowombat.moving()` function.

The `geowombat.moving()` function provides us with a few parameters that we can change:

| Parameter | Description |
| :------------ | ----------------------------------: |
| `stat` | statistic calculated (options: mean, standard deviation, variance, minimum, maximum, percentile) |
| `perc` | percentile used for window operation if `stat = perc`
| `w` | moving window size in pixels
| `nodata` | value that will be ignored in calculations |

For more information this function, see the [function documentation](https://geowombat.readthedocs.io/en/latest/moving.html).

```{code-cell} ipython3
# Open file
with gw.open("../temp/window_raster.tif") as src:

    # Create plot
    fig, ax = plt.subplots(dpi = 200)

    # Calculate local average
    output_gw = src.gw.moving(stat = 'mean', w = 5, n_jobs = 4, nodata = 0)

    # Plot raster
    output_gw.gw.imshow(robust = True, ax = ax)
    plt.tight_layout(pad = 1)
```
