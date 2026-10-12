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
    "description lang=en": "Learn how to search, stream, and composite satellite imagery from STAC catalogs (Element 84, Microsoft Planetary Computer, NASA) using GeoWombat. Includes Sentinel-2, Landsat, and Harmonized Landsat Sentinel-2 (HLS) examples with cloud masking and temporal composites."
    "description lang=fr": "Apprenez à rechercher, diffuser et composer des images satellites à partir de catalogues STAC (Element 84, Microsoft Planetary Computer, NASA) en utilisant GeoWombat."
    "description lang=es": "Aprenda a buscar, transmitir y componer imágenes satelitales de catálogos STAC (Element 84, Microsoft Planetary Computer, NASA) usando GeoWombat."
    "keywords": "spatial, remote sensing, STAC, SpatioTemporal Asset Catalog, Sentinel-2, Landsat, HLS, geowombat, planetary computer, element 84, cloud masking, temporal composite"
    "property=og:locale": "en_US"
---

(f_rs_stac)=

----------------

```{admonition} Learning Objectives
- Understand what a STAC catalog is and why it matters for remote sensing
- Stream Sentinel-2, Landsat, and HLS imagery directly into Python without downloading
- Apply automatic cloud masking to STAC queries
- Build cloud-free temporal composites (monthly, quarterly, etc.)
- Merge imagery from multiple sensors into a single time series
```
```{admonition} Review
* [Raster Data](c_rasters.md)
* [Reading/Writing Remote Sensed Images](f_rs_io.md)
* [Configuration Manager](f_rs_config.md)
```
----------------

# Accessing STAC Imagery with GeoWombat

Not long ago, working with satellite imagery meant downloading enormous files, wrestling with sensor-specific folder structures, and hoping your hard drive could keep up. For a single Landsat scene that might be several gigabytes; for a year of Sentinel-2 over a small study area, easily hundreds. Most of those bytes were pixels you never actually needed.

The **SpatioTemporal Asset Catalog (STAC)** specification changes the workflow. A STAC catalog is a standardized, queryable index of spatial-temporal data hosted in the cloud. Instead of downloading whole scenes, you describe the imagery you want — by bounding box, date range, and cloud cover — and stream just the bytes that overlap your study area directly into an `xarray.DataArray`. The data stay in the cloud; only the pixels you request cross the wire.

GeoWombat wraps this process in a single function, `open_stac`, so you can go from "I want Sentinel-2 over Washington, D.C. last summer" to an analysis-ready, lazily-loaded DataArray in a handful of lines.

```{note}
STAC access in GeoWombat requires a few extra dependencies. Install them with:

`pip install "geowombat[stac]"`

This pulls in `pystac`, `pystac_client`, `stackstac`, and `planetary_computer`.
```

## What is a STAC catalog?

Think of a STAC catalog as a library card catalog for satellite imagery. Every "book" (called an **item**) is a scene with standardized metadata: when and where it was captured, which sensor produced it, how cloudy it is, and where each band lives as a separate Cloud-Optimized GeoTIFF (COG). Because the metadata is standardized, you can query many catalogs the same way.

Several public STAC catalogs are supported out of the box:

| Catalog           | What it hosts                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------------- |
| `element84_v1`    | `sentinel_s2_l2a`, `sentinel_s2_l1c`, `sentinel_s1_l1c`, `landsat_c2_l2`, `cop_dem_glo_30`, `naip`                  |
| `microsoft_v1`    | `landsat_c2_l2`, `sentinel_s2_l2a`, `sentinel_s1_l1c`, `io_lulc`, `usda_cdl`, `esa_worldcover`, `cop_dem_glo_30`    |
| `nasa_lp_cloud`   | `hls_l30` (HLS Landsat 30m), `hls_s30` (HLS Sentinel-2 30m)                                                         |
| `element84_v0`    | `sentinel_s2_l2a_cogs` (legacy)                                                                                     |

Each catalog has slightly different coverage, latency, and rate limits, but the GeoWombat API is the same across all of them.

## Your first STAC query: streaming Sentinel-2

Let's start with the workhorse of open-access optical imagery: Sentinel-2 Level 2A (atmospherically corrected surface reflectance), served by Element 84. The live query below grabs the blue, green, and red bands over a small window around Washington, D.C., for June–July 2023, keeping only scenes with less than 10% cloud cover.

The only bit of bookkeeping worth highlighting is `epsg`. STAC scenes may be stored in many UTM zones; `open_stac` reprojects everything to the EPSG code you pass in so the returned DataArray has a single, consistent CRS. For D.C., UTM Zone 18N (`EPSG:32618`) is the natural choice.

```{code-cell} ipython3
from geowombat.core.stac import open_stac

data, df = open_stac(
    stac_catalog="element84_v1",
    collection="sentinel_s2_l2a",
    bounds=(-77.05, 38.88, -77.00, 38.92),   # small DC window (lon/lat)
    epsg=32618,                               # UTM Zone 18N
    bands=["blue", "green", "red"],
    cloud_cover_perc=10,
    start_date="2023-06-01",
    end_date="2023-07-31",
    resolution=10.0,
    chunksize=1024,
    max_items=1,
)

print(data)
```

Two things come back: `data` is a lazy, dask-backed `xarray.DataArray` with dimensions `(time, band, y, x)`, and `df` is a `GeoDataFrame` describing the individual scenes that went into it (footprints, timestamps, cloud cover, asset URLs). No pixels have actually been downloaded yet — they will be pulled on demand the moment you call `.compute()`, `.plot()`, or write to disk.

```{note}
The `bounds` argument is always in **geographic (lon/lat) coordinates**, regardless of the `epsg` you request for the output. This keeps the query language consistent whether you are working in D.C., Darfur, or Darwin.
```

Plotting the first timestamp as an RGB composite triggers the actual download and renders the scene:

```{code-cell} ipython3
import matplotlib.pyplot as plt

fig, ax = plt.subplots(dpi=200, figsize=(7, 7))
data.sel(time=data.time[0], band=["red", "green", "blue"]).plot.imshow(
    robust=True, ax=ax
)
ax.set_title("Sentinel-2 RGB — Washington, D.C.")
plt.tight_layout(pad=1)
plt.show()
```

That image came straight off the Element 84 catalog over the network — no scene was ever downloaded to disk. The rest of the examples in this chapter use the same pattern, just with different catalogs, bands, or time windows. They're shown as plain code blocks so the page builds quickly; swap them to `{code-cell} ipython3` if you want to execute them yourself.

## Switching catalogs: Landsat from Microsoft Planetary Computer

Need Landsat instead? Change two arguments. The query pattern is identical because GeoWombat hides the catalog-specific details (asset names, endpoint URLs, sign-in tokens) behind a consistent interface.

``` python
from geowombat.core.stac import open_stac

data_l, df_l = open_stac(
    stac_catalog="microsoft_v1",
    collection="landsat_c2_l2",
    bounds=(-77.1, 38.85, -76.95, 38.95),
    epsg=32618,
    bands=["red", "green", "blue"],
    start_date="2023-06-01",
    end_date="2023-07-31",
    resolution=30.0,
    chunksize=512,
    max_items=5,
)

print(data_l)
```

`max_items` caps how many scenes the query returns — useful when you're exploring a new area and don't want to wait for a full year of Landsat to materialize.

## Harmonized Landsat Sentinel-2 (HLS)

Combining Landsat and Sentinel-2 sounds tidy in theory but is painful in practice: different spatial resolutions, different band centers, different BRDF characteristics. NASA's **Harmonized Landsat Sentinel-2** product does the hard work for you, producing BRDF-normalized surface reflectance from both sensors resampled to a common 30 m MGRS grid.

Two collections are available through the `nasa_lp_cloud` catalog:

- `hls_l30` — Landsat OLI (30 m, ~8-day revisit)
- `hls_s30` — Sentinel-2 MSI (30 m, ~5-day revisit)

GeoWombat maps the friendly band names you already know (`red`, `green`, `blue`, `nir`, etc.) onto the correct HLS asset keys automatically, so the call looks just like the ones above:

``` python
data_hls, df_hls = open_stac(
    stac_catalog="nasa_lp_cloud",
    collection="hls_l30",
    bounds=(-77.1, 38.85, -76.95, 38.95),
    epsg=32618,
    bands=["red", "green", "blue", "nir"],
    start_date="2023-06-01",
    end_date="2023-07-31",
    resolution=30.0,
    max_items=5,
)
```

## Cloud masking — the easy way

Optical imagery without cloud masking is a trap. A beautifully green summer pixel may actually be cloud top, and a "dark" pixel may be cloud shadow. Every sensor ships its own quality band, and every quality band has its own bitmask conventions. Rather than ask you to memorize them, GeoWombat exposes a single switch: `mask_data=True`.

With `mask_data=True`, the appropriate QA band is injected into the query automatically, the mask is applied, and then the QA band is dropped from the returned DataArray. You do **not** need to add `qa_pixel` or `scl` to your `bands` list — in fact, you shouldn't.

Under the hood, the defaults are sensible for each sensor:

- **Sentinel-2** — uses the SCL (Scene Classification Layer) and masks `no_data`, `saturated_defective`, `cloud_shadow`, `cloud_medium_prob`, `cloud_high_prob`, and `thin_cirrus`.
- **Landsat** — uses `qa_pixel` and masks `fill`, `dilated cloud`, `cirrus`, `cloud`, `cloud shadow`, and `snow`.
- **HLS** — uses `Fmask` and masks `cirrus`, `cloud`, `adjacent_cloud`, `cloud_shadow`, and `snow_ice`.

``` python
# Sentinel-2 with cloud masking
data_s2, df = open_stac(
    stac_catalog="element84_v1",
    collection="sentinel_s2_l2a",
    bounds=(-77.1, 38.85, -76.95, 38.95),
    epsg=32618,
    bands=["blue", "green", "red", "nir"],
    start_date="2023-06-01",
    end_date="2023-07-31",
    cloud_cover_perc=50,
    resolution=100.0,
    max_items=5,
    mask_data=True,
)
```

If the defaults are too aggressive (or too permissive) for your use case, override them with `mask_items`:

``` python
# Mask only clouds and cloud shadow; keep cirrus and saturated pixels
data, df = open_stac(
    stac_catalog="element84_v1",
    collection="sentinel_s2_l2a",
    bounds=(-77.1, 38.85, -76.95, 38.95),
    epsg=32618,
    bands=["blue", "green", "red", "nir"],
    start_date="2023-06-01",
    end_date="2023-07-31",
    resolution=100.0,
    mask_data=True,
    mask_items=["cloud_shadow", "cloud_high_prob"],
)
```

## Temporal composites — cloud-free mosaics over time

A single Sentinel-2 scene is a snapshot; what you usually want is a **composite** — a summary of many scenes over a time window that smooths out clouds, shadows, and sensor artifacts. The classic recipe is "take the median of all clear observations within each month." GeoWombat's `composite_stac` wraps `open_stac` with automatic cloud masking and temporal aggregation so you can do this in one call.

``` python
from geowombat.core.stac import composite_stac

# Monthly Sentinel-2 median composite
comp_s2, df = composite_stac(
    stac_catalog="element84_v1",
    collection="sentinel_s2_l2a",
    bounds=(-77.1, 38.85, -76.95, 38.95),
    epsg=32618,
    bands=["blue", "green", "red", "nir"],
    start_date="2023-06-01",
    end_date="2023-08-31",
    cloud_cover_perc=50,
    resolution=100.0,
    max_items=20,
    frequency="MS",   # "month start" — one composite per calendar month
)

print(comp_s2.shape)   # (time=3, band=4, y, x) — one per month
```

### Choosing a time frequency

`frequency` accepts any [pandas offset alias](https://pandas.pydata.org/docs/user_guide/timeseries.html#offset-aliases). A few common ones:

| Alias  | Description                          |
| ------ | ------------------------------------ |
| `'D'`  | Daily                                |
| `'W'`  | Weekly                               |
| `'2W'` | Biweekly                             |
| `'MS'` | Monthly (month start) — **default**  |
| `'QS'` | Quarterly (quarter start)            |
| `'YS'` | Yearly (year start)                  |

Multiplied forms such as `'15D'` (every 15 days) or `'2MS'` (every two months) work too.

### Choosing an aggregation

`agg` controls how observations within each time period are combined. The default is `median`, which is robust to residual clouds the mask may have missed.

| Value      | Description                                |
| ---------- | ------------------------------------------ |
| `'median'` | Median (default) — robust to outliers      |
| `'mean'`   | Mean — sensitive to outliers               |
| `'min'`    | Per-pixel minimum                          |
| `'max'`    | Per-pixel maximum                          |

``` python
# Biweekly mean composite
comp, df = composite_stac(
    stac_catalog="element84_v1",
    collection="sentinel_s2_l2a",
    bounds=(-77.1, 38.85, -76.95, 38.95),
    epsg=32618,
    bands=["blue", "green", "red", "nir"],
    start_date="2023-06-01",
    end_date="2023-08-31",
    resolution=10.0,
    frequency="2W",
    agg="mean",
)
```

Because HLS blends both Landsat and Sentinel-2 observations, it is particularly powerful for composites — you get a denser time series with fewer gaps. Pass `collection="hls"` and `composite_stac` will query both `hls_l30` and `hls_s30` and combine them:

``` python
comp_hls, df = composite_stac(
    stac_catalog="nasa_lp_cloud",
    collection="hls",                    # queries both hls_l30 and hls_s30
    bounds=(-77.1, 38.85, -76.95, 38.95),
    epsg=32618,
    bands=["blue", "green", "red", "nir"],
    start_date="2023-06-01",
    end_date="2023-08-31",
    resolution=30.0,
    frequency="MS",
    max_items=20,
)

print(comp_hls.shape)   # more observations per period from two sensors
```

```{note}
Composites preserve all spatial attributes (`crs`, `res`, `transform`), so you can save the output straight to disk with `gw.save(comp, "composite.tif")`. Time periods where every pixel is cloudy are dropped from the output automatically.
```

## Merging collections into a single time series

Finally, if you need to hand-combine sensors rather than rely on HLS — for example, Landsat (30 m) back to the 1980s combined with Sentinel-2 (10 m) from 2015 on — use `merge_stac`. Each call to `open_stac` is independent, so you can set resampling and CRS per sensor and then concatenate:

``` python
from geowombat.core.stac import open_stac, merge_stac
from rasterio.enums import Resampling

data_l, df_l = open_stac(
    stac_catalog="microsoft_v1",
    collection="landsat_c2_l2",
    bounds=(-77.1, 38.85, -76.95, 38.95),
    epsg=32618,
    bands=["red", "green", "blue"],
    mask_data=True,
    start_date="2023-01-01",
    end_date="2023-12-31",
    resolution=30.0,
)

data_s2, df_s2 = open_stac(
    stac_catalog="element84_v1",
    collection="sentinel_s2_l2a",
    bounds=(-77.1, 38.85, -76.95, 38.95),
    epsg=32618,
    bands=["blue", "green", "red"],
    resampling=Resampling.cubic,
    mask_data=True,
    start_date="2023-01-01",
    end_date="2023-12-31",
    resolution=30.0,                   # resample Sentinel-2 to match Landsat
)

stack = merge_stac(data_l, data_s2)
print(stack)
```

The result is a single DataArray sorted in time, ready for band math, extraction, or machine-learning pipelines covered in the rest of this section.

## Wrapping up

STAC turns the question "how do I get imagery?" into "what do I want?" Combined with GeoWombat's consistent interface, cloud masking, and compositing, you can go from a bounding box on a map to a clean, analysis-ready time series in a single cell of code — no downloads, no sensor-specific boilerplate, and no hand-rolled QA bitmasks.

```{admonition} Next Steps
With a DataArray in hand, everything you've already learned about GeoWombat applies: [band math](f_rs_band_math.md), [extraction](f_rs_extraction.md), and [machine-learning prediction](f_rs_ml_predict.md) all work exactly the same whether the pixels came from disk or from a STAC query.
```
