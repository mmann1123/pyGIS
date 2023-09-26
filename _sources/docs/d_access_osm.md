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
    "description lang=en": "Learn how to access OpenStreetMap (OSM) roads, buildings, and other data via python. "
    "description lang=fr": "Découvrez comment accéder aux routes, bâtiments et autres données OpenStreetMap (OSM) via python."
    "description lang=es": "Aprenda a acceder a carreteras, edificios y otros datos de OpenStreetMap (OSM) a través de Python."
    "keywords": "python open street map OSM"
    "property=og:locale": "en_US"
---

<!-- (d_access_osm)= -->

----------------
```{admonition} Learning Objectives
- Download and utilize OpenStreetMap data
```
```{admonition} Review
* [Understanding CRS codes](d_understand_crs_codes.md)
* [Creating Points, Lines, Polygons](c_new_vectors.md)
```
----------------

# Accessing OpenStreetMap Data in Python

OpenStreetMap (OSM) is an open collaborative project to create a free editable map of the world. In this tutorial, we will use the Python module OSMnx to access OSM data.

## OSMnx

This week we will explore a Python module called [OSMnx](https://github.com/gboeing/osmnx)
that can be used to retrieve, construct, analyze, and visualize street networks from OpenStreetMap, and also retrieve data about Points of Interest such as restaurants, schools, and lots of different kind of services. It is also easy to conduct network routing based on walking, cycling or driving by combining OSMnx functionalities with a package called [NetworkX](https://networkx.github.io/documentation/stable/).

To get an overview of the capabilities of the package, see an introductory video given by the lead developer of the package, Prof. Geoff Boeing: ["Meet the developer: Introduction to OSMnx package by Geoff Boeing"](https://www.youtube.com/watch?v=Q0uxu25ddc4&list=PLs9D4XVqc6dCAhhvhZB7aHGD8fCeCC_6N).

One the most useful features that OSMnx provides is an easy-to-use way of retrieving [OpenStreetMap](http://www.openstreetmap.org) data (using [OverPass API](http://wiki.openstreetmap.org/wiki/Overpass_API)).


## Import Modules

We import OSMnx, which provides functions to retrieve OSM data. We also import Geopandas to handle the geographic data frames we will create.

```{code-cell} ipython3
import osmnx as ox
import geopandas as gpd
```

## Define Study Area

We specify the place name string for the area we want to access data for - the Edgewood neighborhood in Washington DC.

```{code-cell} ipython3
place_name = "Edgewood, Washington, DC, USA"
```

## Geocode Place Boundary

Geocoding takes a place name and looks up its geographic boundary. OSMnx provides the `geocode_to_gdf()` function to geocode place names to GeoDataFrames.

When we pass our place name string to `geocode_to_gdf()`, it queries the Nominatim geocoder to find the OSM boundary for that location. The function returns a GeoDataFrame containing the boundary polygon coordinates.

```{code-cell} ipython3
area = ox.geocode_to_gdf(place_name)
```

We print the area GeoDataFrame to inspect it. We see it contains the polygon geometry along with some metadata.

```{code-cell} ipython3
print(area.head())
```

To visualize the neighborhood boundary, we plot the geocoded polygon.

```{code-cell} ipython3
area.plot()
```

## Download OSM Building Footprints

Now that we have the study area boundary, we can download building footprints within this region from OSM using OSMnx's `geometries_from_place()` function [docs](https://osmnx.readthedocs.io/en/stable/osmnx.html?highlight=geometries_from_place#osmnx.geometries.geometries_from_place) .

We pass the function our place name to get [all types of buildings](https://wiki.openstreetmap.org/wiki/Buildings) in that area. We also specify the tag `building=yes` so it only returns building polygon geometries.

```{code-cell} ipython3
tags = {'building': True}
buildings = ox.geometries_from_place(place_name, tags)
```

Printing the GeoDataFrame shows the building polygons and their OSM metadata.

```{code-cell} ipython3
print(buildings.head())
```

We can plot the retrieved buildings.

```{code-cell} ipython3
buildings.plot() 
```

## Save Buildings to Shapefile

Since these objects are already `geopandas.GeoDataFrame` it's easy to save them to disk. We simply use `gpd.to_file` [docs](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.to_file.html).

```{Important}
We can't write OSM GeoDataFrames directly to disk because they contain field types (like lists) that can't be saved in .shp or .geojsons etc. Instead lets isolate only the attributes we are interested in, **including geometry** which is required. 
```

We need to isolate just the attributes we are interested in:

```{code-cell} ipython3
buildings  = buildings.loc[:,buildings.columns.str.contains('addr:|geometry')]
```

```{Important}
OSM data often contains multiple feature types like mixing points with polygons. This is a problem when we try to write it to disk.
```
We also need to isolate the feature type we are looking for [e.g. Multipolygon, Polygon, Point]. Since here we want building footprints we are going to keep only polygons. 

```{code-cell} ipython3
buildings = buildings.loc[buildings.geometry.type=='Polygon']
```

```python
buildings.to_file('../temp/edgewood_buildings.shp')
```

The shapefile can now be opened in any GIS software.

## References

- [OpenStreetMap Overpass API](http://wiki.openstreetmap.org/wiki/Overpass_API)
- [OSMnx documentation](https://osmnx.readthedocs.io/en/stable/)
- [OSM building tags](https://wiki.openstreetmap.org/wiki/Buildings)

 