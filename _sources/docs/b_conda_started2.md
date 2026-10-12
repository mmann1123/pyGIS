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
    "description lang=en": "Learn how install a working python environment for spatial data and remote sensing. Here we utilize Docker to make the process replicable and at least somewhat easy to understand."
    "description lang=fr": "Découvrez comment installer un environnement python fonctionnel pour les données spatiales et la télédétection. Ici, nous utilisons Docker pour rendre le processus reproductible et au moins quelque peu facile à comprendre."
    "description lang=es": "Aprenda a instalar un entorno Python que funcione para datos espaciales y detección remota. Aquí utilizamos Docker para hacer que el proceso sea replicable y al menos algo fácil de entender."
    "keywords": "python environment, Docker, spatial, raster, shapefile, remote sensing"
    "property=og:locale": "en_US"
---

(conda_started2)=

----------------

```{admonition} Learning Objectives
- Understand the role and significance of package managers in the context of software development and geospatial data science.
- Create and activate a new `conda` environment.
- Use `conda` to install geospatial packages from the `conda-forge` channel.
- Recognize key geospatial packages  
```

```{admonition} Review
- [A normal intro to python environments](b_getting_started)
```
----------------


# Geospatial Environment Installation Guide

In the world of software development, package managers have become a fundamental tool for simplifying the installation of software packages and their dependencies. They automate the process of installing, upgrading, configuring, and removing software packages in a consistent manner. In the field of geospatial data science, where several packages need to be installed, package managers ensure a smooth and efficient setup of your environment.

[Follow the instructions to install conda here](b_getting_started)


## Creating and Activating a New Environment
Each project or workflow may require different versions of packages or even different packages altogether. To manage these variations, it is best practice to create isolated environments for each project. This prevents conflicts between package versions and ensures that your projects remain reproducible.

You can create a new environment in `conda` using the following command:

```{code-block} console
conda create --name myenv
```

Replace `myenv` with the name of your environment.


To activate this environment, use:

```{code-block} console
conda activate myenv
```

Now, any package you install will be installed in this environment, keeping it isolated from other environments.

## Installing Geospatial Packages

Before we install anything, we need to tell `conda` to use the `conda-forge` channel, which carries the most up-to-date geospatial packages. If you installed Miniforge this is already the default, but setting it explicitly does no harm:

```{code-block} console
conda config --add channels conda-forge
conda config --set channel_priority strict
```

Nearly all of the packages we need are available on `conda-forge`, so we can install them in a single command. Installing them from one channel — rather than mixing `conda` and `pip` — is the approach the GeoPandas developers recommend, since pulling geospatial dependencies from different sources can lead to hard-to-debug import errors.

```{code-block} console
conda install -c conda-forge geowombat geowombat-ml geowombat-stac pyproj geopandas contextily earthpy census geoplot osmnx pykrige us
```

One package, `pytidycensus` (used in the census chapter), is not published on `conda-forge`, so we install that single package from PyPI into the same environment:

```{code-block} console
pip install pytidycensus
```

```{note}
Prefer `pip` for everything? You can instead install the whole stack into a virtual environment with
`pip install "geowombat[ml,stac]" pyproj geopandas contextily earthpy census pytidycensus geoplot osmnx pykrige us` —
just don't mix `pip` and `conda` for the *geospatial* packages within one environment. Installing the pure-Python `pytidycensus` with `pip` on top of a conda environment, as above, is fine.
```

Now you have all the packages installed and ready to be used in your new environment!

## Verifying the Installation
Next we need to activate the environment and verify that the packages are installed correctly.

First activate the environment you created earlier:

```{code-block} console
conda activate myenv
```

Then enter a Python session by typing:

```{code-block} console
python
```

You should now see `>>>` in your terminal, indicating that you are in a Python interpreter session.

To verify that the packages are installed correctly, you can run the following commands in a Python interpreter:

```python
import geowombat as gw
from geowombat.ml import fit, predict, fit_predict
import pyproj
import geopandas
import contextily
import earthpy
import census
``` 

Now you can exit the Python interpreter by typing:

```python
exit()
```

```{note}
If you encounter any errors during the import, it means that the package is not installed correctly. You can try reinstalling the package or checking for any dependencies that may be missing.
```