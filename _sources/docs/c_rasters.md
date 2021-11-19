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
  "description lang=en": "Learn to create new geospatial raster objects, assign projections or CRS."
  "description lang=fr": "Apprenez à créer de nouveaux objets raster, à attribuer des projections ou CRS."
  "description lang=es": "Aprenda a crear nuevos objetos ráster, asignar proyecciones o CRS."
  "keywords": "raster, geospatial, shapefile, rasterio, numpy"
  "property=og:locale": "en_US"
---

(c_rasters)=
 
----------------

```{admonition} Learning Objectives
* Create new raster objects 
* Assign the correct projection or CRS
```
```{admonition} Review
* [Please review Affine transformation](d_affine.md)
```
----------------

# Raster Data 
A raster data model uses an array of cells, or pixels, to represent real-world objects. Raster datasets are commonly used for representing and managing imagery, surface temperatures, digital elevation models, and numerous other entities. A raster can be thought of as a special case of an area object where the area is divided into a regular grid of cells. But a regularly spaced array of marked points may be a better analogy since rasters are stored as an array of values where each cell is defined by a single coordinate pair inside of most GIS environments. Implicit in a raster data model is a value associated with each cell or pixel. This is in contrast to a vector model that may or may not have a value associated with the geometric primitive.

In order to work with raster data we will be using `rasterio` and later `geowombat`. Behind the scenes a `numpy.ndarray` does all the heavy lifting. To understand how raster works it helps to construct one from scratch. 

Here we create two `ndarray` objects one `X` spans [-90&deg;,90&deg;] longitude, and `Y` covers [-90&deg;,90&deg;] latitude. 

 ```{code-cell} ipython3
import numpy as np
x = np.linspace(-90, 90, 6)
y = np.linspace(90, -90, 6)
X, Y = np.meshgrid(x, y)
X
```

```{code-cell} ipython3
Y
```
Let's generate some data representing temperature and store it an array `Z`

```{code-cell} ipython3
import matplotlib.pyplot as plt

Z1 =  np.abs(((X - 10) ** 2 + (Y - 10) ** 2) / 1 ** 2)
Z2 =  np.abs(((X + 10) ** 2 + (Y + 10) ** 2) / 2.5 ** 2)
Z =  (Z1 - Z2)

plt.imshow(Z)
plt.title("Temperature")
plt.show()
``` 
