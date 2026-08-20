#!/usr/bin/env bash
#
# Creates a working conda environment named "pygis" with everything needed to
# run the code in the PyGIS book.
#
# Requirements: conda (Miniforge recommended -- see docs/b_getting_started).
#
# Everything is installed from conda-forge in a single solve. Installing all of
# the geospatial packages from one channel -- rather than mixing conda and pip --
# is what the GeoPandas developers recommend, and avoids hard-to-debug import
# errors. Using --override-channels keeps us off Anaconda's "defaults" channel
# (which now carries licensing restrictions for larger organizations).
#
# Note: `conda create` will refuse to run if an environment named "pygis"
# already exists; it will not overwrite it. Remove the old one first with
# `conda env remove -n pygis` if you want a clean rebuild.

set -e

conda create --name pygis --yes \
    --channel conda-forge --override-channels \
    python=3.11 \
    "numpy<2" \
    geowombat \
    geowombat-ml \
    geowombat-stac \
    geopandas \
    rasterio \
    pyproj \
    contextily \
    earthpy \
    census \
    geoplot \
    osmnx \
    pykrige \
    us \
    pandas \
    matplotlib \
    scikit-learn \
    libstdcxx-ng

# pytidycensus (used in the census chapter) is not published on conda-forge,
# so install this one package from PyPI into the same environment.
conda run -n pygis pip install pytidycensus

# Verify the install by importing the book's key packages.
conda run -n pygis python -c "\
import geowombat as gw; \
from geowombat.ml import fit, predict, fit_predict; \
import geopandas, rasterio, geoplot; \
print('geowombat', gw.__version__); \
print('geopandas', geopandas.__version__); \
print('rasterio', rasterio.__version__); \
print('environment \"pygis\" is ready')"
