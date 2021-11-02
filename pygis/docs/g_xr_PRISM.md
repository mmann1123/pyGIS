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

#https://xray.readthedocs.io/en/v0.3.1/io.html
remote_data = xray.open_dataset(
    'http://iridl.ldeo.columbia.edu/SOURCES/.OSU/.PRISM/.monthly/dods',
    decode_times=False)
print(remote_data)

# Time (time)	grid: /T (months since 1960-01-01) ordered (Jan 1895) to (Apr 2013) by 1.0 N= 1420 pts :grid
#Longitude (longitude)	grid: /X (degree_east) ordered (125W) to (66.5W) by 0.04166667 N= 1405 pts :grid
#Latitude (latitude)	grid: /Y (degree_north) ordered (49.91667N) to (24.08333N) by 0.04166667 N= 621 pts :grid
```

