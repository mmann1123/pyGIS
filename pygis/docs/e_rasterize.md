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
  "description lang=en": "Learn how to convert vector shapefiles into raster files using rasterio."
  "keywords": "geospatial, raster, vector, shapefile, rasterize"
  "property=og:locale": "en_US"
---

# Rasterize Vectors w. Rasterio

----------------

```{admonition} Learning Objectives
* Convert vector data into raster format with `rasterio`
* Understand the requirements for successful conversion
```
```{admonition} Review
* [Reproject Rasters w. Rasterio and Geowombat](e_raster_reproject.md)
```

----------------

Rasterizing vectors can be helpful if you want to incorporate vector data (i.e., point, line, or polygon) in your raster analysis. The process is essentially what the name suggests: We take a vector and convert it into pixels. This can be done with `rasterio`.

## Setup

We'll begin by importing our modules.

```{code-cell} ipython3
:tags: ["hide-cell"]

# Import modules
import rasterio
from rasterio import features
import fiona
import matplotlib.pyplot as plt
from rasterio.plot import show
```

## Rasterize vectors with `rasterio`

We'll read in the vector file. We will also read in a raster file to get the raster's metadata (e.g., coordinate system) so that we can apply those parameters to the vector file. In other words, the raster will serve as a "model" for the the rasterization of the vector.

```{important} The vector and raster should be in the same coordinate system. If not, you'll need to re-project one of them so they are the same.
```

```{code-cell} ipython3
:tags: ["hide-cell"]

# Read in vector
vector = fiona.open(r"../_static/e_vector_shapefiles/sf_bay_counties/sf_bay_counties.shp")

# Get list of geometries for all features in vector file
geom = [shapes['geometry'] for shapes in vector]

# Open raster
raster = rasterio.open(r"../_static/e_raster/bay-area-wells_kde_sklearn.tif")
```

With our data loaded, we can rasterize the vector using the metadata from the raster using `rasterize()` in the `rasterio.features` module. For more information on this function, check out [the `rasterio` documentation](https://rasterio.readthedocs.io/en/latest/api/rasterio.features.html).

```{code-cell} ipython3
# Rasterize vector using the shape and coordinate system of the raster
rasterized = features.rasterize(geom, out_shape = raster.shape, transform = raster.transform)

# Plot raster
fig, ax = plt.subplots(1, figsize = (10, 10))
show(rasterized, ax = ax)
plt.gca().invert_yaxis()
```

Finally, we can save the rasterized vector out.

```{code-cell} ipython3
:tags: ["hide-cell"]

with rasterio.open(
        "../temp/rasterized_vector.tif", "w",
        driver = "GTiff",
        transform = raster.transform,
        dtype = rasterio.uint8,
        count = 1,
        width = raster.width,
        height = raster.height) as dst:
    dst.write(rasterized, indexes = 1)
```
