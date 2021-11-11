#!/usr/bin/env bash

# generates a working environment for all book depedencies in linux

sudo echo '
name: pygisbookgw
channels:
- conda-forge
- defaults

dependencies:
- python=3.7
- wheel
- cython
- scipy
- zarr
- requests
- libspatialindex
- gdal
- census
- geoplot
- pip
- netcdf4
- osmnx
- pip:
  - pip-tools
  - opencv-python
  - git+https://github.com/jgrss/geowombat.git
  - jupyter-book
  - matplotlib
  - ghp-import
  - pyproj
  - geopandas
  - contextily
  - us
  - pydap
  '> pygisbookgw.yml

conda env create -f pygisbookgw.yml  
conda activate pygisbookgw
python -c "import geowombat as gw;print(gw.__version__)"
python -c "import rasterio;from rasterio.crs import CRS; cc = CRS.from_epsg(4326); print(cc)"
conda deactivate
 


