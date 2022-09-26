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
  "description lang=en": "Learn how install a working python environment for spatial data and remote sensing. Here we utilize Docker to make the process replicable and at least somewhat easy to understand."
  "description lang=fr": "Découvrez comment installer un environnement python fonctionnel pour les données spatiales et la télédétection. Ici, nous utilisons Docker pour rendre le processus reproductible et au moins quelque peu facile à comprendre."
  "description lang=es": "Aprenda a instalar un entorno Python que funcione para datos espaciales y detección remota. Aquí utilizamos Docker para hacer que el proceso sea replicable y al menos algo fácil de entender."
  "keywords": "python environment, Docker, spatial, raster, shapefile, remote sensing"
  "property=og:locale": "en_US"
---



(conda_started2)=

----------------

```{admonition} Learning Objectives
- Learn basics of anaconda
- Set up a working environment for spatial modeling
```

```{admonition} Review
* [A normal intro to python environments](b_getting_started.md)
```
----------------

# Setting up Python for Spatial on Mac, Windows, and Linux
Spatial analysis requires a pretty broad set of python modules and with it, comes a lot of dependencies. And to be honest, the only thing Python doesn't do well with, is dependencies. Luckily we have a few tricks up our sleeves to help you get to work fast. 


## Anaconda 
### Install Anaconda
Anaconda is a package manager that makes handling dependencies much easier.  Before you begin install:

- [Anaconda](https://www.anaconda.com/products/distribution)

Alternatively, if you don't have much free space in your computer (or if think anaconda is bloated- which is ):

- [miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

Hit yes and make sure to run the `init` script if prompted. 

### Create an Environment Called Spatial
First thing we need to do is create a conda environment. Think of this as a sandbox for installing a new version of python with only a few chosen modules.

Open `terminal` on a mac/linux or open `anaconda command prompt` or `command prompt` in windows. Then run the following to create an environment called `spatial`:

``` bash
conda create -n spatial python=3.9
```
Now that we have created the environment, let's jump in it! After which you should see `(spatial)` on the left hand side of your terminal. 

``` bash
conda activate spatial
```
To avoid conflicting dependencies let's add the channel called `conda-forge` (a user maintained list of python modules) and set it to only search there, by setting priority to `strict`. 

``` bash
conda config --add channels conda-forge
conda config --set channel_priority strict
```

Now let's install most of the modules we will need in this book:

``` bash
conda install geowombat geopandas rasterio matplotlib pandas
```
Now install those that aren't available through conda's channels:

``` bash
pip install sklearn-xarray  pip-tools rtree ipykernel osmnx PyKrige census us
```
That's it! To learn more about managing environments in conda please refer to the [docs here](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

```{Important}
Note that every time you want to use your `spatial` environment. You will need to select it in your IDE or open a terminal window and type `conda activate spatial`, you can then launch your IDE via the command line. 
```