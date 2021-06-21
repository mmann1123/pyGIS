#!/usr/bin/env python
# coding: utf-8

#  
# 
# 
# PyGIS - Open Source Geospatial Programming & Remote Sensing 
# ============================
# 
# The globe is now digital. Everything from monitoring deforestation, predicting wildfires, to training autonomous vehicles and tracking uprisings on social media requires you to understand how to leverage location data. This book will introduce you to the methods required for geospatial programming. We focus on building your core programming techniques while helping you: leverage spatial data from OSM and the US Census, use satellite imagery, track land-use change, and track social distance during a pandemic, amongst others. We will leverage open source Python packages such as GeoPandas, Rasterio, Sklearn, and Geowombat to better understand our world and help predict its future. Some Python programming experience is required, however the material will be presented in a student-friendly manner and will focus on real-world application. 
# 
# ```{tableofcontents}
# ```
#  
# <!-- -----------------------
# 
# https://autogis-site.readthedocs.io/en/latest/index.html
# 
# # A: Data Types
# - Vector Data
#   - Geojson
#   - Shp
#   - Geopkg
# 
# - Raster Data
#   - Arrays 
#   - Spatial Arrays
#  
# - Materials
#   - https://mgimond.github.io/Spatial/chp02-0.html
# 
# 
# -----------------------------
# # B: Nature of Coordinate Systems
# - Geographic Coordinates
# - Projected Coordinates
# - CRS and Proj4Strings
# - Use mostly https://mgimond.github.io/Spatial/chp09-0.html  and https://automating-gis-processes.github.io/CSC18/lessons/L2/projections.html
# 
# ## Reproject vs Warp
# - Example reproject (might be example in book)
# - Example of warp focus on affine transform
# 
# ## Exercises: 
# - Plot dots for distortion
# - What's in a proj4string?
# - Create your own projection
# 
# ## Materials
# - https://automating-gis-processes.github.io/site/notebooks/L2/projections.html
# - https://mgimond.github.io/Spatial/chp09-0.html
# - Turtle draw excercise in "mastering geospatil analysis with python"
# - https://autogis-site.readthedocs.io/en/latest/notebooks/L2/02-projections.html
#  -https://docs.geotools.org/stable/userguide/tutorial/affinetransform.html
#  - https://people.cs.clemson.edu/~dhouse/courses/401/notes/affines-matrices.pdf
# ----------------------
# # C: Basics with Spatial Data
# ## Vector
# - read/write geopandas
# - plots
# - Basic operations
#   - Subset rows
#   - Create new data from lat lon
#   - reproject
#   - Non-spatial left join new data into shapefile
# - Geoprocessing
#   - Unions
#   - Intersect
#   - etc
#   
# - Merge & Aggregate Attributes
# 
# ## Raster
# - read/write rasterio
# - plots
# - Basic operations
#   - band math
#   - clip
# - Vector Raster Operations
#   - Extract by feature
#   - Summarize by feature
# 
# 
# ----------------------
# # D: Remote Sensing with Geowombat
# 
# - Common Operations
#   - Mosaic
#   - Band Math and NDVI
#   - Cloud masking
#   - Landcover classfication
#   - Others?
# 
# -----------------------
# # Deep Learning Feature Classification
# - Common Operations
#   - Simple label transfer learning
#   - Object detection
#   - Others?
# 
# # Visualization
# - https://handsondataviz.org/geojsonio.html
# 
# ## Book rendering options
# - https://executablebooks.github.io/quantecon-mini-example/docs/python_by_example.html
# - https://jupyterbook.org/intro.html
# - https://www.sphinx-doc.org/en/master/ -->
# 
# 
# 
# ```{toctree}
# :hidden:
# :titlesonly:
# :caption: Get Started
# 
# b_intro_py
# b_about_py
# b_getting_started
# b_python_by_example
# b_learn_more
# ```
# 
# 
# ```{toctree}
# :hidden:
# :titlesonly:
# :caption: Data Types
# 
# c_features
# c_store_features
# c_vectors
# c_rasters
# ```
# 
# 
# ```{toctree}
# :hidden:
# :titlesonly:
# :caption: Nature of Coordinate Systems
# 
# d_crs_what_is_it
# d_understand_crs_codes
# d_affine
# d_vector_crs_intro
# d_raster_crs_intro
# ```
# 
# 
# ```{toctree}
# :hidden:
# :titlesonly:
# :caption: Basic Operations
# 
# e_vector_op_intro
# e_raster_op_intro
# ```
# 
# 
# ```{toctree}
# :hidden:
# :titlesonly:
# :caption: Remote Sensing
# 
# f_rs_intro
# ```
