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

(c_store_features)=
 
# Data Storage Formats
 
## Vector Data File Formats

### GeoJSON
GeoJSON is an open standard format designed for representing simple geographical features, along with their non-spatial attributes. It is based on the JSON format. The features include points, line strings, polygons, and multi-part collections of these types. One of it's primary advantages is that it is human readible and stores all the relevant data in a single text file. As result however, these files can get very large when storing complex geometries.

### GeoPackage

This is a relatively new data format that follows [open format standards](https://en.wikipedia.org/wiki/Open_format) (i.e. it is non-proprietary). It's built on top of SQLite (a self-contained relational database). Its one big advantage over many other vector formats is its compactness--coordinate value, metadata, attribute table, projection information, etc..., are all stored in a *single* file which facilitates portability. Its filename usually ends in `.gpkg`. Applications such as QGIS (2.12 and up), R and ArcGIS will recognize this format (ArcGIS version 10.2.2 and above will read the file from ArcCatalog but requires a script to create a GeoPackage).


### Shapefile

A **shapefile** is a file-based data format native to ArcView 3.x software (a much older version of ArcMap). Conceptually, a shapefile is a feature class--it stores a collection of features that have the same geometry type (point, line, or polygon), the same attributes, and a common spatial extent. 

Despite what its name may imply, a "single" shapefile is actually composed of at least three files, and as many as eight. Each file that makes up a "shapefile" has a common filename but different extension type. 

The list of files that define a "shapefile" are shown in the following table. Note that each file has a specific role in defining a shapefile. 

File extension |	Content
---------------|------------
.dbf |	Attribute information
.shp |	Feature geometry
.shx |	Feature geometry index
.aih |	Attribute index
.ain |	Attribute index
.prj |	Coordinate system information
.sbn |	Spatial index file
.sbx |	Spatial index file



### File Geodatabase

A **file geodatabase** is a relational database storage format. It's a far more complex data structure than the shapefile and consists of a **.gdb** folder housing dozens of files. Its complexity renders it more versatile allowing it to store multiple feature classes and enabling topological definitions (i.e. allowing the user to define rules that govern the way different feature classes relate to one another). An example of the contents of a geodatabase is shown in the following figure.
 

```{figure} ../_static/img/geodatabase.jpg
:name: geodatabase

```

## Raster Data File Formats

Rasters are in part defined by their pixel depth. Pixel depth defines the range of distinct values the raster can store. For example, a 1-bit raster can only store 2 distinct values: 0 and 1.


```{figure} ../_static/c_data_types/raster_storage.png
:name: pixel depth
Pixel depth allows for a wider range of values but also take up more space
```
There is a wide range of raster file formats used in the GIS world. Some of the most popular ones are listed below.

### Imagine

The **Imagine** file format was originally created by an image processing software company called ERDAS. This file format consists of a single **.img** file. This is a simpler file format than the shapefile. It is sometimes accompanied by an .xml file which usually stores metadata information about the raster layer.

### GeoTiff

A popular public domain raster data format is the **GeoTIFF** format. If maximum portability and platform independence is important, this file format may be a good choice.

### File Geodatabase

A raster file can also be stored in a file geodatabase alongside vector files. Geodatabases have the benefit of defining image mosaic structures thus allowing the user to create “stitched” images from multiple image files stored in the geodatabase. Also, processing very large raster files can be computationally more efficient when stored in a file geodatabase as opposed to an Imagine or GeoTiff file format.


