# Python GIS Textbook

-----------------------
## Data Structures & Basic Operations
- Vector Data
  - Geojson
  - Shp
  - Geopkg

- Raster Data
  - Arrays 
  - Spatial Arrays
 
- Materials
  - https://mgimond.github.io/Spatial/chp02-0.html


-----------------------------
## Nature of Coordinate Systems
- Geographic Coordinates
- Projected Coordinates
- CRS and Proj4Strings
- Use mostly https://mgimond.github.io/Spatial/chp09-0.html  and https://automating-gis-processes.github.io/CSC18/lessons/L2/projections.html

### Reproject vs Warp
- Example reproject (might be example in book)
- Example of warp focus on affine transform

### Exercises: 
- Plot dots for distortion
- What's in a proj4string?
- Create your own projection

### Materials
- https://automating-gis-processes.github.io/site/notebooks/L2/projections.html
- https://mgimond.github.io/Spatial/chp09-0.html
- Turtle draw excercise in "mastering geospatil analysis with python"


----------------------
## Opening and Ploting Spatial Data
### Vector
- read/write geopandas
- plots
- Basic operations
  - Subset rows
  - Create new data
  - reproject
  - Non-spatial left join new data into shapefile

### Raster
- read/write rasterio
- plots
- Basic operations
  - band math
  - clip

-----------------------
## Geoprocessing & Vector Raster Operations
- Geoprocessing
  - Unions
  - Intersect
  - etc
- Vector Raster Operations
  - Extract by feature
  - Summarize by feature

----------------------
## Remote Sensing with Geowombat

- Common Operations
  - Mosaic
  - Band Math and NDVI
  - Cloud masking
  - Landcover classfication
  - Others?

-----------------------
## Deep Learning Feature Classification
- Common Operations
  - Simple label transfer learning
  - Object detection
  - Others?



# Book rendering options
- https://executablebooks.github.io/quantecon-mini-example/docs/python_by_example.html
- https://jupyterbook.org/intro.html
- https://www.sphinx-doc.org/en/master/
