#!/usr/bin/env python
# coding: utf-8

# (conda_started2)=
# 
# ----------------
# 
# ```{admonition} Learning Objectives
# - Understand the role and significance of package managers in the context of software development and geospatial data science.
# - Install `miniconda` and `mamba` package managers to manage your Python packages.
# - Create and activate a new `conda` environment.
# - Use `conda` and `mamba` to install geospatial packages from the `conda-forge` channel.
# - Recognize key geospatial packages  
# ```
# 
# ```{admonition} Review
# - [A normal intro to python environments](b_getting_started)
# ```
# ----------------
# 
# 
# # Geospatial Environment Installation Guide
# 
# In the world of software development, package managers have become a fundamental tool for simplifying the installation of software packages and their dependencies. They automate the process of installing, upgrading, configuring, and removing software packages in a consistent manner. In the field of geospatial data science, where several packages need to be installed, package managers ensure a smooth and efficient setup of your environment.
# 
# In this guide, we'll talk about `conda` and `mamba`. `Conda` is a powerful package manager and environment manager that you use with command line commands at the Anaconda Prompt for Windows, or in a terminal window for macOS or Linux. `Mamba` is a reimplementation of the `conda` package manager in C++. It's designed to be faster and more robust to network issues or packages with tricky dependencies. When working with complex geospatial packages, `mamba` can often be a more efficient choice.
# 
# This page provides a guide on how to install `miniconda` or `mamba`, and various geospatial packages including `geowombat` and `geowombat-ml`.
# 
# ## Installing Miniconda
# 
# Firstly, you will need to **choose between** Miniconda & Mamba. Miniconda is a free minimal installer for conda. Please follow the instructions from the [Miniconda page](https://docs.conda.io/en/latest/miniconda.html) to install it on your system.
# 
# ## Installing Mamba
# 
# To install `mamba` (prefered), please follow the instructions from the [Mamba page](https://mamba.readthedocs.io/en/latest/).
# 
# ## Creating and Activating a New Environment
# 
# You can create a new environment in `conda` or `mamba` using the following command:
# 
# ```{code-block} console
# conda create --name myenv
# ```
# or with `mamba`:
# 
# ```{code-block} console
# mamba create --name myenv
# ```
# Replace `myenv` with the name of your environment.
# 
# :::{note}
# For the remainder of this tutorial we will use `mamba`, but `conda` can be exchanged for `mamba` in all commands.
# :::
# 
# 
# To activate this environment, use:
# 
# ```{code-block} console
# mamba activate myenv
# ```
# 
# Now, any package you install will be installed in this environment, keeping it isolated from other environments.
# 
# ## Installing Geospatial Packages
# 
# Before we install the packages, we need to add `conda-forge` to your channels:
# 
# ```{code-block} console
# mamba config --add channels conda-forge
# mamba config --set channel_priority strict
# ```
# 
# Then, we can install `geowombat` and `geowombat-ml` using `conda` or `mamba`. For `mamba`:
# 
# ```{code-block} console
# mamba install geowombat geowombat-ml
# ```
#  
# 
# Following this, we need to install the following packages: `pyproj`, `geopandas`, `contextily`, `earthpy`, `census`, `geoplot`, `osmnx`, `pykrige`, and `us`.  We will start with the packages available through `conda-forge`:
# 
# 
# ```{code-block} console
# mamba install pyproj geopandas       
# ```
# 
# Finally install those packages that aren't available through `conda-forge`:
# 
# ```{code-block} console
# pip install census contextily earthpy geoplot osmnx us pykrige
# ``
# 
# Now you have all the packages installed and ready to be used in your new environment!
