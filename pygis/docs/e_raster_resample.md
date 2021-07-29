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
  "description lang=en": "Learn how to resample single and multi-band rasters using rasterio and geowombat. This includes creating using a 'snap raster' as well as seperately matching extent and or resolution of another raster. We demonstrate these using LandSat imagery as examples."
  "description lang=fr": "Apprenez à rééchantillonner des rasters mono et multicanaux à l'aide de rasterio et geowombat. Cela inclut la création à l'aide d'un « raster d'accrochage » ainsi que la correspondance séparée de l'étendue et/ou de la résolution d'un autre raster. Nous les démontrons en utilisant les images LandSat comme exemples."
  "description lang=es": "Aprenda a volver a muestrear rásteres de una o varias bandas mediante rasterio y geowombat. Esto incluye la creación mediante un 'ráster de ajuste', así como la extensión y / o resolución coincidentes por separado de otro ráster. Demostramos esto usando imágenes de LandSat como ejemplos."
  "property=og:locale": "en_US"
---

(e_raster_reproject)=

----------------

```{admonition} Learning Objectives
- Resample a raster with rasterio & geowombat
- Learn how to match the extent
```
```{admonition} Review
* [Affine transformation](d_affine.md)
* [Raster Coordinate Reference Systems](d_raster_crs_intro.md)
* [Reprojecting Rasters](e_raster_reproject.md)
* [Interpolation Methods Explained](d_raster_crs_intro_interpolation_options.md)
```
----------------

# Resampling Rasters w. Rasterio and Geowombat

## Why is Resampling Important?
*Before you begin* any analysis using rater data it is critical that you have rasters that are "co-registered". Co-registration requires that any two rasters have the same resolution, and orientation - the origins can differ but they much align. *In other words, co-registration requires that cell centroids align perfectly for all intersecting areas.* Resampling is also extremely common during reprojection operations as it often requires changing the orientation, scale or resolution of an image. 

**Examples of data that is *not* co-registered**
```{figure} ../_static/e_raster/Raster_ diff-orientation.jpg
:name: Resampling rasters - different orientation
:width: 400px
Resampling rasters - different orientation
```

```{figure} ../_static/e_raster/Raster_ diff-orientation-origin.jpg
:name: Resampling rasters - different orientation and origin
:width: 400px
Resampling rasters - different orientation and origin
```
```{figure} ../_static/e_raster/Raster_ diff-res.jpg
:name: Resampling rasters - different resolution
:width: 400px
Resampling rasters - different resolution
```
## Methods for Resampling Explained
Upsampling refers to cases where we are converting to higher resolution/smaller cells. Downsampling is resampling to lower resolution/larger cell sizes.

There are [a number of methods](https://rasterio.readthedocs.io/en/latest/api/rasterio.enums.html#rasterio.enums.Resampling) to resample data, but they often take the form of "nearest neighbor", "bilinear", and "cubic convolusion" - these interpolation methods [are explained here in some detail](d_raster_crs_intro_interpolation_options.md). 

## Simple Up/Downsampling in Rasterio
Occationally you will need to resample your data by some factor, for instance you might want data upsampled to a courser resolution due to memory constraints. 


Here's an example of how to generate the `data` array and the `transform` needed to write it out. We will start by simply reading in the data and coersing a higher resolution, by adding more rows and columns. To understand the `transform`, let's review [affine transformations](d_affine). Here we will update the scale values with the new resolution using $S_{y}$ and $S_{x}$ show below

$$
   \begin{eqnarray}
   \mbox{Scale transform: }  \begin{bmatrix} S_{x} & 0 & 0 \\ 0 & S_{y} & 0 \\ 0 & 0 & 1 \end{bmatrix} 
   \end{eqnarray}
$$

```{code-cell} ipython3
import rasterio
from rasterio.enums import Resampling

image = "../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF"

upscale_factor = 2

with rasterio.open(image) as dataset:

    # resample data to target shape using upscale_factor
    data = dataset.read(
        out_shape=(
            dataset.count,
            int(dataset.height * upscale_factor),
            int(dataset.width * upscale_factor)
        ),
        resampling=Resampling.bilinear
    )

    print('Shape before resample:', dataset.shape)
    print('Shape after resample:', data.shape[1:])

    # scale image transform
    dst_transform = dataset.transform * dataset.transform.scale(
        (dataset.width / data.shape[-1]),
        (dataset.height / data.shape[-2])
    )

    print('Transform before resample:\n', dataset.transform, '\n')
    print('Transform after resample:\n', dst_transform)

    ## Write outputs
    # set properties for output
    dst_kwargs = src.meta.copy()
    dst_kwargs.update(
        {
            "crs": dst_crs,
            "transform": dst_transform,
            "width": data.shape[-1],
            "height": data.shape[-2],
            "nodata": 0,  
        }
    )

    with rasterio.open("../temp/LC08_20200518_15m.tif", "w", **dst_kwargs) as dst:
        # iterate through bands
        for i in range(data.shape[0]):
              dst.write(data[i].astype(rasterio.uint32), i+1)
```

```{admonition} Reminder
Read up on [affine transformations](d_affine_transform_matrix) to help you understand the `transform.scale` function above. 
```

## Resampling a Raster with Geowombat
As always the easiest way to deal with resampling is by deploying geowombat. It's like a swiss army knife for kicking raster butt. Here we just need to set the desired resolution with `ref_res`, and the `resampling` method in the open statement. Writing a file is a bit more intuitive too. 

```{code-cell} ipython3
:tags: ["hide-output"]

import geowombat as gw
 
image = "../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF"

with gw.config.update(ref_res=15):
    with gw.open(image, resampling="bilinear") as src:
        print(src.data)
        
        # to write out simply:
        # src.gw.to_raster(
        #     "../temp/LC08_20200518_15m.tif",
        #     overwrite=True,
        # ) 
```
Much.... easier.... 


