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
    "description lang=en": "Learn to create new vector objects, assign projections or CRS, and write them to a shapefile or geojson. We also cover creating basic maps with points, lines and polygons."
    "description lang=fr": "Apprenez à créer de nouveaux objets vectoriels, à attribuer des projections ou à des CRS et à les écrire dans un fichier de formes ou un geojson. Nous couvrons également la création de cartes de base avec des points, des lignes et des polygones."
    "description lang=es": "Aprenda a crear nuevos objetos vectoriales, asigne proyecciones o CRS y escríbalos en un shapefile o geojson. También cubrimos la creación de mapas básicos con puntos, líneas y polígonos."
    "keywords": " spatial, shapefile, geopandas"
    "property=og:locale": "en_US"
---

(c_vectors)=

---
```{admonition} Learning Objectives
* Understand the role of GeoPandas in manipulating spatial data in Python.
* Learn how to create and use Geopandas GeoSeries and GeoDataFrame.
* Visualize spatial vector data using basic plotting.
```
```{admonition} Review
* [Fundamentals of Spatial Data Structures](c_features.md)
```
---

# Spatial Vector Data using GeoPandas 

Previously, we explored the fundamentals of spatial data structures [here](c_features.md). Now, we will delve deeper into the manipulation of spatial vector data, using the GeoPandas library. GeoPandas serves as an essential tool for working with geospatial data in Python, seamlessly blending the data manipulation capabilities of pandas with the geometric data analysis power of shapely. As a result, GeoPandas provides a high-level interface for intricate geospatial operations, effectively bypassing the need for a specialized spatial database like PostGIS.

## Data Structures in GeoPandas

GeoPandas introduces two primary data structures, namely, `GeoSeries` and `GeoDataFrame`. These structures are subclasses of the pandas Series and DataFrame respectively.

### GeoSeries

A `GeoSeries` is akin to a vector where each entry represents a set of geometric shapes corresponding to a single observation. This could be a single shape (like a single polygon), or it could involve multiple shapes that form one observation (for instance, the numerous islands that compose the State of Hawaii or a country like Indonesia).

GeoPandas supports three basic types of geometric objects, all of which are shapely objects:

* Points / Multi-Points
* Lines / Multi-Lines
* Polygons / Multi-Polygons

Here are examples of each type:

The first example creates a GeoSeries of Points. This might be used to represent individual locations on a map. For instance, you could use a Point for each location where a sample was collected, or to mark the location of cities or other points of interest.

```{code-cell} ipython3
# Point GeoSeries
import geopandas
from shapely.geometry import Point
s = geopandas.GeoSeries([Point(1, 1), Point(2, 2), Point(3, 3)])
s
```

The next example creates a GeoSeries of Lines. Lines could be used to represent the path of a moving object, the route of a road or river, or the border between different regions. The example creates a single line that connects three points.

```{code-cell} ipython3
# Line GeoSeries
from shapely.geometry import LineString
l = geopandas.GeoSeries([LineString([Point(-77.036873,38.907192), Point(-76.612190,39.290386,), Point(-77.408456,39.412006)])])
l
```

The last example creates a GeoSeries of Polygons. A Polygon might represent a bounded area, such as the outline of a lake, the footprint of a building, or the boundaries of a country. In this example, the polygon represents an area defined by three points (a triangle).

```{code-cell} ipython3
# Polygon GeoSeries
from shapely.geometry import Polygon
p = geopandas.GeoSeries([Polygon([Point(-77.036873,38.907192), Point(-76.612190,39.290386,), Point(-77.408456,39.412006)])])
p
```

While a `GeoSeries` can contain different types of geometric objects, not all operations will be possible if the GeoSeries is mixed. Certain methods require all objects in the GeoSeries to be of the same geometric type.

### GeoDataFrame

A `GeoDataFrame` is a table-like data structure that holds a `GeoSeries`. 

One `GeoSeries` column in a `GeoDataFrame` holds a special status and is referred to as the `GeoDataFrame’s` "geometry". Any spatial method applied to a `GeoDataFrame`, or when a spatial attribute like the area is called, they will act on this "geometry" column. 

Regardless of its actual column name, the "geometry" column can be accessed via the geometry attribute (gdf.geometry), and the name of the geometry column can be retrieved by calling gdf.geometry.name.

```{note}
While a `GeoDataFrame` may contain multiple columns with geometric (shapely) objects, only one column can be considered the active geometry at a time. To switch the active geometry column, you can use the `GeoDataFrame.set_geometry()` method.
```

Here is an example of a `GeoDataFrame` using the 'naturalearth_lowres' dataset. This dataset represents a simplified global country boundary map, which can be useful for global scale visualizations:

```{code-cell} ipython3
# Load a GeoDataFrame
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

# Preview the data
world.head()
```

And now let's create a simple plot from this `GeoDataFrame`:

```{code-cell} ipython3
# Plot the GeoDataFrame
world.plot()
```

The resulting plot shows the geographic locations of all countries in the 'naturalearth_lowres' dataset.

## Reprojecting GeoDataFrames

Geopandas makes it straightforward to reproject your data. In this section, we will reproject the world dataset to a projection that's suitable for Europe.

First, let's identify the current projection of our data.

```{code-cell} ipython3
print(world.crs)
```

To reproject the dataset, you can use the `to_crs` function. We will use the EPSG code 3035, which is suitable for Europe.

```{code-cell} ipython3
# Reproject to EPSG 3035 (ETRS89 / LAEA Europe)
world = world.to_crs(epsg=3035)
```

You can confirm that the dataset's CRS has been updated:

```{code-cell} ipython3
print(world.crs)
```

That's it! Now, your world dataset is in a projection that is appropriate for visualizing Europe.

## Subsetting a Region from the World Dataset

In many cases, you may only be interested in a specific region rather than the entire world dataset. Subsetting or clipping the data to your region of interest makes the dataset easier to manage and speeds up processing time.

### Example: Extracting European Countries

Here's how you can subset the data to include only European countries.

```{code-cell} ipython3
# Filter the dataset to include only European countries
europe = world[world['continent'] == 'Europe']

# Plot the data
europe.plot()
```

This will produce a plot of all countries in Europe, based on the world dataset.

### Note:

- Make sure to always check the Coordinate Reference System (CRS) when subsetting geographical data to ensure that the data is compatible.


