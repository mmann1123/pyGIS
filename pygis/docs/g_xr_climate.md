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

(f_rs_plot)=


---------------
```{admonition} Learning Objectives
  - 
```
```{admonition} Review
* [Data Structures](c_features.md)
```
--------------


# Plot Remote Sensed Images
Import required modules and data.

```{code-cell} ipython3
from pydap.client import open_url
import xarray as xr

os.chdir('../temp')
!wget "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/surface/air.mon.mean.nc"
#%%

ds = xr.open_dataset('air.mon.mean.nc')
#%%

ds_clim = ds.groupby('time.month').mean(dim='time')
ds_clim.air.sel(month=1).plot()

#%%
ds_anom = ds.groupby('time.month') - ds_clim
ds_anom.air[2].plot()

```

