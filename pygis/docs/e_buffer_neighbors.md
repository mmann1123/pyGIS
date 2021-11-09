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
  "description lang=en": " "
  "keywords": " "
  "property=og:locale": "en_US"
---

----------------

```{admonition} Learning Objectives
* Do distance/proximity based analysis for points, lines, polygons
* Create buffers
* Get nearest neighbors
* Calculate adjacency for polygons
```
```{admonition} Review
* [Geospatial Vector Data](c_vectors.md)
* [Attributes & Indexing for Vector Data](e_attributes.md)
* [Creating Geospatial Vector Data](e_new_vectors.md)
```
----------------

# Proximity Analysis - Buffers, Nearest Neighbor, Adjacency 
In this chater we are going to dig into some of the most common geospatial operations. After this section you will be able to answer simple questions like "where is the nearest wendy's?", "Are there any homes within 50 yards of a highway?".
 

## Buffer Analysis
First, we will import the necessary modules and create two lines (click the + below to show code cell). 

```{code-cell} ipython3
:tags: [hide-cell]
# Import modules
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from io import StringIO 

data = """
ID,X,Y
1,  -87.789,  41.976
1,  -87.482,  41.677
2,  -87.599,  41.908
2,  -87.598,  41.708
2,  -87.643,  41.675
"""
# use StringIO to read in text chunk
df = pd.read_table(StringIO(data), sep=',')

#zip the coordinates into a point object and convert to a GeoData Frame
points = [Point(xy) for xy in zip(df.X, df.Y)]
points = gpd.GeoDataFrame(df, geometry=points, crs = 'EPSG:4326')
# create line for each ID 
lines = points.groupby(['ID'])['geometry'].apply(lambda x:  LineString(x.tolist()))
lines = gpd.GeoDataFrame(lines, geometry='geometry', crs="EPSG:4326") 
lines.reset_index(inplace=True)

```
Let's take a look at the data. 

```{code-cell} ipython3
# plot county outline and add wells to axis (ax)
lines.plot(column='ID')
```

```{important} NEVER do distance analysis with unprojeted data (e.g. lat lon). Distances are best not measured in degrees! Instead use .to_crs() to convert it to a projected coordinate system with a linear unit in feet or meters etc.
```

Although it is not clearly stated the `distance` parameter is measured in the linear unit of the projection. So before we get started we need to make sure to use `to_crs()` to convert to a projected coordinate system. 

```{code-cell} ipython3
# plot county outline and add wells to axis (ax)
lines = lines.to_crs(3857)
# check the linear unit name in `unit_name`.
print(lines.crs.axis_info)
```

Starting from two lines we can start playing around with the buffer function. You can read the docs for the buffer function, unfortunately is split between two docs [geopandas](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.buffer.html) and [shapely](https://shapely.readthedocs.io/en/latest/manual.html#object.buffer). 

```{code-cell} ipython3
buf = lines.buffer(distance = 1000)
bp = buf.plot()
lines.plot(ax=bp, color='red')
print(buf)
```
Notice that we now have to polygon GEOMETRIES. This no longer has the line attributes associated with it. If we want to add back the attribute data we need to replace the original geometry column with new buffer geometry values. 

```{code-cell} ipython3
line_buffer = lines.copy()
line_buffer['geometry'] = buf
print(line_buffer)
```

There are a number of other parameters available to use, namely `cap_style`, and `single_sided`. 

```{code-cell} ipython3
buf = lines.buffer(distance = 3000, cap_style = 2)
bp = buf.plot()
lines.plot(ax=bp, color='red')
```

```{table} Buffer caps can be different shapes
:name: cap_style

| attribute | value |
|---|---|
| round | 1 |
| flat  | 2 |
| square | 3 |
```

We can also create left or right side buffers. Use negative distances for left, and positive values for right. 

```{code-cell} ipython3
buf_right = lines.buffer(distance = 3000, single_sided = True)
bp = buf_right.plot(color='green')

buf_left = lines.buffer(distance = -1500, single_sided = True)
buf_left.plot(ax=bp, color='purple')
lines.plot(ax=bp, color='white')
```
 
## Nearest Neighbor Analysis

One commonly used GIS task is to be able to find the nearest neighbor. For instance, you might have a single Point object representing your home location, and then another set of locations representing e.g. public transport stops. Then, quite typical question is *"which of the stops is closest one to my home?"* This is a typical nearest neighbor analysis, where the aim is to find the closest geometry to another geometry. [^gpd_clip]

In Python this kind of analysis can be done with shapely function called ``nearest_points()`` that returns a tuple of the [nearest points](https://shapely.readthedocs.io/en/latest/manual.html#shapely.ops.nearest_points) in the input geometries.

### Nearest point using Shapely

Let's start by testing how we can find the nearest Point using the ``nearest_points()`` function of Shapely.

Let's create an origin Point and a few destination Points and find out the closest destination.

```{code-cell} ipython3
from shapely.geometry import Point, MultiPoint
from shapely.ops import nearest_points

orig = Point(1, 1.67)
dest1, dest2, dest3 = Point(0, 1.45), Point(2, 2), Point(0, 2.5)
```

To be able to find out the closest destination point from the origin, we need to create a MultiPoint object from the destination points.

```{code-cell} ipython3

destinations = MultiPoint([dest1, dest2, dest3])
print(destinations)
```

Okey, now we can see that all the destination points are represented as a single MultiPoint object.

- Now we can find out the nearest destination point by using ``nearest_points()`` function.

```{code-cell} ipython3
nearest_geoms = nearest_points(orig, destinations)
near_idx0 = nearest_geoms[0]
near_idx1 = nearest_geoms[1]
print(nearest_geoms)
print(near_idx0)
print(near_idx1)
```

As you can see the ``nearest_points()`` function returns a tuple of geometries where the first item is the geometry
of our origin point and the second item (at index 1) is the actual nearest geometry from the destination points.
Hence, the closest destination point seems to be the one located at coordinates (0, 1.45).

This is the basic logic how we can find the nearest point from a set of points.

### Nearest points using Geopandas

Of course, the previous example is not really useful yet. Hence, next I show, how it is possible to find nearest points
from a set of origin points to a set of destination points using GeoDataFrames. If you don't already have the addresses and PKS_suuralueet.kml datasets,
you can find and download them from :doc:`geocoding <geocoding>` and :doc:`Point in Polygon <point-in-polygon>` tutorials.

- First we need to create a function that takes advantage of the previous function but is tailored to work with two GeoDataFrames.

```{code-cell} ipython3
def nearest(row, geom_union, df1, df2, geom1_col='geometry', geom2_col='geometry', src_column=None):
    """Find the nearest point and return the corresponding value from specified column."""
    # Find the geometry that is closest
    nearest = df2[geom2_col] == nearest_points(row[geom1_col], geom_union)[1]
    # Get the corresponding value from df2 (matching is based on the geometry)
    value = df2[nearest][src_column].get_values()[0]
    return value
```
<!--  
def nearest(row, geom_union, df1, df2, geom1_col='geometry', geom2_col='geometry', src_column=None):
    nearest = df2[geom2_col] == nearest_points(row[geom1_col], geom_union)[1]
    valsue = df2[nearest][src_column].get_values()[0]
    return value
-->
Next we read the address data and the Helsinki districts data and find out the closest address to the centroid of each district.

.. ipython:: python
    :suppress:

        import geopandas as gpd
        fp1 = r"C:\HY-DATA\HENTENKA\KOODIT\Opetus\Automating-GIS-processes\2017\data\PKS_suuralue.kml"
        fp2 = r"C:\HY-DATA\HENTENKA\KOODIT\Opetus\Automating-GIS-processes\2017\data\addresses.shp"
        gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

        df1 = gpd.read_file(fp1, driver='KML')
        df2 = gpd.read_file(fp2)

.. code:: python

    In [7]: import geopandas as gpd

    In [8]: fp1 = "/home/geo/PKS_suuralue.kml"
    In [9]: fp2 = "/home/geo/addresses.shp"
    In [10]: gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

    In [11]: df1 = gpd.read_file(fp1, driver='KML')
    In [12]: df2 = gpd.read_file(fp2)

Create unary union from Points, which basically creates a MultiPoint object from the Point geometries.

.. ipython:: python

    unary_union = df2.unary_union
    print(unary_union)

Calculate the centroids for each district area.

.. ipython:: python

    df1['centroid'] = df1.centroid
    df1.head()

Okey now we are ready to use our function and find closest Points (taking the value from id column) from df2 to df1 centroids

.. ipython:: python

    df1['nearest_id'] = df1.apply(nearest, geom_union=unary_union, df1=df1, df2=df2, geom1_col='centroid', src_column='id', axis=1)
    df1.head(20)

That's it! Now we found the closest point for each centroid and got the ``id`` value from our addresses into the ``df1`` GeoDataFrame.

Sources
[^gpd_clip]: [automating-gis-processes](https://automating-gis-processes.github.io/2017/lessons/L3/nearest-neighbour.html)


