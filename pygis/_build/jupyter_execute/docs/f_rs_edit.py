#!/usr/bin/env python
# coding: utf-8

# (f_rs_edit)=
# 
# 
# ----------------
# 
# ```{admonition} Learning Objectives
# - Handle missing values
# - Setting missing values
# - Replacing values
# 
# ```
# ```{admonition} Review
# * [Opening remotely sensed data](f_rs_io.md)
# ```
# ----------------
# 
# # Editing Rasters and Remotely Sensed Data
# 
# 
# ## Setting 'no data' Values
# 
# The `xarray.DataArray.where` function masks data by setting nans, as demonstrated by the example below.

# In[1]:


import geowombat as gw
from geowombat.data import l8_224078_20200518

# Zeros are replaced with nans
with gw.open(l8_224078_20200518) as src:
    data = src.where(src != 0)


# ## Setting 'no data' Values with Scaling
# 
# In GeoWombat, we use `xarray.where` and `xarray.DataArray.where` along with optional scaling in the `set_nodata` function. In this example, we set zeros as 65535 and scale all other values from a [0,10000] range to [0,1].

# In[ ]:


import geowombat as gw
from geowombat.data import l8_224078_20200518

# Set the 'no data' value and scale all other values
with gw.open(l8_224078_20200518) as src:
    data = src.gw.set_nodata(0, 65535, (0, 1), 'float64', scale_factor=0.0001)


# ## Replace values
# 
# The GeoWombat `replace` function mimics `pandas.DataFrame.replace`.

# In[ ]:


import geowombat as gw
from geowombat.data import l8_224078_20200518

# Replace 1 with 10
with gw.open(l8_224078_20200518) as src:
    data = src.gw.replace({1: 10})


# ```{note}    
# The `replace` function is typically used with categorical data.
# ```
