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

(c_attributes)=
 
# Manipulating Attributes  

```{figure} ../_static/c_data_types/dataframe.svg
:name: vector properties 
Structure of a `GeoDataFrame` extends the functionality of a Pandas `DataFrame`
```

Each `GeoSeries` can contain any geometry type (e.g. points, lines, polygon) and has a `GeoSeries.crs` attribute, which stores information on the projection (CRS stands for Coordinate Reference System). Therefore, each `GeoSeries` in a `GeoDataFrame` can be in a different projection, allowing you to have, for example, multiple versions of the same geometry, just in a different CRS.


```{tip}  Becuase GeoPandas are so intertwined spend the time to learn more about here [Pandas User Guide](https://pandas.pydata.org/pandas-docs/stable/user_guide/index.html)
```

## Create Attributes

One of the most basic operations is creating new attributes. Let's say for instance we want to look at the world population in millions. We can start with an existing column of data `pop_est`. Let's start by looking at the column names:

```{code-cell} ipython3
import geopandas
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
world.columns
```
We can then do basic operations on the basis of column names. Here we create a new column `m_pop_est`:

```{code-cell} ipython3
world['m_pop_est'] = world['pop_est'] / 1e6
world.head()
```

## Indexing and Selecting Data

GeoPandas inherits the standard pandas methods for indexing/selecting data. This includes label based indexing with .loc and integer position based indexing with .iloc, which apply to both GeoSeries and GeoDataFrame objects. For more information on indexing/selecting, see the pandas documentation.

In addition to the standard pandas methods, GeoPandas also provides coordinate based indexing with the cx indexer, which slices using a bounding box. Geometries in the GeoSeries or GeoDataFrame that intersect the bounding box will be returned.


### Coordinate Inding 
Using the world dataset, we can use this functionality to quickly select all cities in the northern and southern hemisphere using a `_CoordinateIndexer` using `.cx`.

```{code-cell} ipython3
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))
northern_world = world.cx[ : , 0: ]
northern_world.plot(figsize=(10, 3))
```

```{code-cell} ipython3
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))
southern_world = world.cx[ : , :0 ]
southern_world.plot(figsize=(10, 3))
```
