---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

(f_rs_io)=


---------------
```{admonition} Learning Objectives
  - How to open multiple common remotely sensed image types
  - Handle RGB, BGR, LandSat, PlanetScope images and other sensor types
  - Mosaic multiple remotely sensed images
  - Create a time series stack
```
```{admonition} Review
* [Data Structures](c_features)
* [Raster Data ](c_rasters)
```
--------------


# Opening Remote Sensed Images

GeoWombat's file opening is meant to mimic Xarray and Rasterio. That is, rasters are typically opened with a context manager using the function `geowombat.open`. GeoWombat uses `xarray.open_rasterio` to load data into an `xarray.DataArray`. In GeoWombat, the data are always chunked, meaning the data are always loaded as Dask arrays. As with `xarray.open_rasterio`, the opened DataArrays always have at least 1 band.

## Opening a single image

Opening an image with default settings looks similar to `xarray.open_rasterio` and `rasterio.open`. `geowombat.open` expects a file name (`str` or `pathlib.Path`).

```{code-cell} ipython3
import geowombat as gw
from geowombat.data import l8_224078_20200518
import matplotlib.pyplot as plt

with gw.open(l8_224078_20200518) as src:
    print(src)
```
In the example above, `src` is an `xarray.DataArray`. Thus, printing the object will display the underlying Dask array dimensions and chunks, the DataArray named coordinates, and the DataArray attributes.

It automatically converts the coordinates stored in `x` and `y`, and the different bands are stored in `band`. To select a single band we can simply select it with `src.sel(band=1)`.  

Let's plot out what we have while removing missing values, stored at `0`, and switch the band order around to be RGB.

```{code-cell} ipython3
fig, ax = plt.subplots(dpi=200)
with gw.open(l8_224078_20200518) as src:
    src.where(src != 0).sel(band=[3, 2, 1]).gw.imshow(robust=True, ax=ax)
plt.tight_layout(pad=1)
```

## Opening multiple bands as a stack

Often, satellite bands will be stored in separate raster files. To open the files as one DataArray, specify a list instead of a file name.

```{code-cell} ipython3
from geowombat.data import l8_224078_20200518_B2, l8_224078_20200518_B3, l8_224078_20200518_B4

with gw.open([l8_224078_20200518_B2, l8_224078_20200518_B3, l8_224078_20200518_B4]) as src:
    print(src)
```

By default, GeoWombat will stack multiple files by time. So, to stack multiple bands with the same timestamp, change the `stack_dim` keyword.

Also note the use of `band_names` parameter. Here we can set it to anything we want for instance `['blue','green','red']`.

```{code-cell} ipython3
from geowombat.data import l8_224078_20200518_B2, l8_224078_20200518_B3, l8_224078_20200518_B4

with gw.open(
    [l8_224078_20200518_B2, l8_224078_20200518_B3, l8_224078_20200518_B4],
    stack_dim="band",
    band_names=[1, 2, 3],
) as src:
    print(src)
```
You will see this looks the same as the multiband raster:


```{code-cell} ipython3
fig, ax = plt.subplots(dpi=200)
with gw.open(
    [l8_224078_20200518_B2, l8_224078_20200518_B3, l8_224078_20200518_B4],
    stack_dim="band",
    band_names=['blue','green','red'],
) as src:
    src.where(src != 0).sel(band=['red','blue','green']).gw.imshow(robust=True, ax=ax)
plt.tight_layout(pad=1)
```


```{note} 
If time names are not specified with ``stack_dim`` = 'time', GeoWombat will attempt to parse dates from the file names. This could incur significant overhead when the file list is long. Therefore, it is good practice to specify the time names.
```
Overhead required to parse file names

```python
with gw.open(long_file_list, stack_dim='time') as src:
      ...
```

No file parsing overhead

```python
with gw.open(long_file_list, time_names=my_time_names, stack_dim='time') as src:
    ...
```

## Opening multiple bands as a mosaic

When a list of files are given, GeoWombat will stack the data by default. To mosaic multiple files into the same band coordinate, use the **mosaic** keyword.

```{code-cell} ipython3
from geowombat.data import l8_224077_20200518_B2, l8_224078_20200518_B2

with gw.open([l8_224077_20200518_B2, l8_224078_20200518_B2],
              mosaic=True) as src:
    print(src)
```
Now let's take a look at the mosaiced band 2 image values. 

```{code-cell} ipython3
fig, ax = plt.subplots(dpi=200)
with gw.open([l8_224077_20200518_B2, l8_224078_20200518_B2],
              mosaic=True) as src:
    src.where(src != 0).sel(band=1).gw.imshow(robust=True, ax=ax)
plt.tight_layout(pad=1)
```

<!-- See :ref:`io` for more examples illustrating file opening. -->
