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
# ## Masking Out Certain Values
# 
# The `xarray.DataArray.where` function masks data by setting nans, as demonstrated by the example below.

# In[1]:


import geowombat as gw
from geowombat.data import l8_224078_20200518

# Zeros are replaced with nans
with gw.open(l8_224078_20200518) as src:
    data = src.where(src != 0)


# ## Setting 'no data' Values  
# Setting missing data values, when not available in the raster profile, can be done using the [configuration manager](f_rs_config.md) or as an argument in the `open` command.

# In[ ]:


import geowombat as gw
from geowombat.data import l8_224078_20200518

# Zeros are replaced with nans
with gw.open(l8_224078_20200518, nodata=0) as src:
    print('gw.open: ',src.attrs['nodatavals'])
    #  replace 0 with nan
    src=src.gw.mask_nodata() 


# Zeros are replaced with nans
with gw.config.update(nodata=0):
  with gw.open(l8_224078_20200518) as src:
    print('gw.config',src.attrs['nodatavals'])
    #  replace 0 with nan
    src=src.gw.mask_nodata() 


# ## Rescaling Values 
# Most remotely sensed data is stored as `int` to minimize space. We are often left to rescale the values back to floating point on the backend. This can be done in a few ways in geowombat. If the sensor you are using has a geowombat profile, please use that - refer to [configuration manager docs](f_rs_config.md). If it is not natively supported we can manually set the scaling factor using the `gw.config.update`

# In[ ]:


import geowombat as gw
from geowombat.data import l8_224078_20200518
 
# Zeros are replaced with nans
with gw.config.update(scale_factor=0.0001):
  with gw.open(l8_224078_20200518) as src:
    print(src.gw.scale_factor)


#  
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
# 
# ## Updating Values
# 
# Geowombat also accepts normal mathematical expressions such as multiplication and addition:

# In[ ]:


import geowombat as gw
from geowombat.data import l8_224078_20200518

# Replace 1 with 10
with gw.open(l8_224078_20200518) as src:
    data = src * 0.001 +80
    print(data[0].values)

