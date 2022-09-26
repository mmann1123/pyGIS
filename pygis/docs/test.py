#%%
import geowombat as gw
from geowombat.data import l8_224078_20200518, l8_224078_20200518_polygons
from geowombat.ml import fit, predict, fit_predict
import geopandas as gpd
from sklearn_xarray.preprocessing import Featurizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB

le = LabelEncoder()

# The labels are string names, so here we convert them to integers
labels = gpd.read_file(l8_224078_20200518_polygons)
labels["lc"] = le.fit(labels.name).transform(labels.name)
print(labels)
#%%


import matplotlib.pyplot as plt

# Use a data pipeline
pl = Pipeline([("scaler", StandardScaler()), ("pca", PCA()), ("clf", GaussianNB())])

fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

# Fit the classifier
with gw.config.update(ref_res=100):
    with gw.open(l8_224078_20200518) as src:
        X, Xy, clf = fit(src, pl, labels, col="lc")
        y = predict(src, X, clf)
        y.plot(robust=True, ax=ax)
plt.tight_layout(pad=1)


#%%
from geowombat.ml import fit_predict

fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

with gw.config.update(ref_res=300):
    with gw.open(l8_224078_20200518) as src:
        y = fit_predict(src, pl, labels, col="lc")
        y.plot(robust=True, ax=ax)
plt.tight_layout(pad=1)

#%%
from sklearn.cluster import KMeans

cl = Pipeline([("clf", KMeans(n_clusters=6, random_state=0))])

fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

# Fit_predict unsupervised classifier
with gw.config.update(ref_res=300):
    with gw.open(l8_224078_20200518) as src:
        y = fit_predict(src, cl)
        y.plot(robust=True, ax=ax)
plt.tight_layout(pad=1)
#%%
fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

with gw.config.update(ref_res=100):
    with gw.open(
        [l8_224078_20200518, l8_224078_20200518],
        time_names=["t1", "t2"],
        stack_dim="time",
    ) as src:
        y = fit_predict(src, pl, labels, col="lc")
        print(y)
        # plot one time period prediction
        y.sel(time="t1").plot(robust=True, ax=ax)
#%%
fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

with gw.config.update(ref_res=100):
    with gw.open(l8_224078_20200518) as src:
        X, Xy, clf = fit(src, pl, labels, col="lc")
        y = predict(src, X, clf)
        y.plot(robust=True, ax=ax)
#%%
pl = Pipeline([("scaler", StandardScaler()), ("pca", PCA()), ("clf", GaussianNB())])

param_grid = {"scaler__with_std": [True, False], "pca__n_components": [1, 2, 3]}
#%%
from sklearn.model_selection import GridSearchCV, KFold
from sklearn_xarray.model_selection import CrossValidatorWrapper

pl = Pipeline([("scaler", StandardScaler()), ("pca", PCA()), ("clf", GaussianNB())])

cv = CrossValidatorWrapper(KFold())
gridsearch = GridSearchCV(
    pl,
    cv=cv,
    scoring="balanced_accuracy",
    param_grid={"scaler__with_std": [True, False], "pca__n_components": [1, 2, 3]},
)

fig, ax = plt.subplots(dpi=200, figsize=(5, 5))

with gw.config.update(ref_res=300):
    with gw.open(l8_224078_20200518) as src:
        # fit a model to get Xy used to train model
        X, Xy, pipe = fit(src, pl, labels, col="lc")
        gridsearch.fit(*Xy)
        print(gridsearch.cv_results_)
        print(gridsearch.best_score_)
        print(gridsearch.best_params_)
        pipe.set_params(**gridsearch.best_params_)
        y = predict(src, X, pipe)
        y.plot(robust=True, ax=ax)
plt.tight_layout(pad=1)
#%%
import numpy as np

x = np.linspace(-90, 90, 6)
y = np.linspace(90, -90, 6)
X, Y = np.meshgrid(x, y)
X
# %%
import matplotlib.pyplot as plt

Z1 = np.abs(((X - 10) ** 2 + (Y - 10) ** 2) / 1 ** 2)
Z2 = np.abs(((X + 10) ** 2 + (Y + 10) ** 2) / 2.5 ** 2)
Z = Z1 - Z2

plt.imshow(Z)
plt.title("Temperature")
plt.show()
# %%
from rasterio.transform import Affine
import rasterio as rio

res = (x[-1] - x[0]) / 240.0
transform = Affine.translation(x[0] - res / 2, y[0] - res / 2) * Affine.scale(res, res)

# open in 'write' mode, unpack profile info to dst
with rio.open(
    "../temp/new_raster.tif",
    "w",
    driver="GTiff",  # output file type
    height=Z.shape[0],  # shape of array
    width=Z.shape[1],
    count=1,  # number of bands
    dtype=Z.dtype,  # output datatype
    crs="+proj=latlong",  # CRS
    transform=transform,  # location and resolution of upper left cell
) as dst:
    # check for number of bands
    if dst.count == 1:
        # write single band
        dst.write(Z, 1)
    else:
        # write each band individually
        for band in range(len(Z)):
            # write data, band # (starting from 1)
            dst.write(Z[band], band + 1)
# %%
import geowombat as gw
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.patheffects as pe
from geowombat.data import l8_224077_20200518_B4, l8_224078_20200518_B4
from os.path  import basename

def plot(bounds_by, ref_image=None, cmap='viridis'):
    fig, ax = plt.subplots(dpi=200)
    with gw.config.update(ref_image=ref_image):
        with gw.open([l8_224077_20200518_B4, l8_224078_20200518_B4],
                        band_names=['nir'],
                        chunks=256,
                        mosaic=True,
                        bounds_by=bounds_by,
                        persist_filenames=True) as srca:
            # Plot the NIR band
            srca.where(srca != 0).sel(band='nir').plot.imshow(robust=True, cbar_kwargs={'label': 'DN'}, ax=ax)
            # Plot the image chunks
            srca.gw.chunk_grid.plot(color='none', edgecolor='k', ls='-', lw=0.5, ax=ax)
            # Plot the image footprints
            srca.gw.footprint_grid.plot(color='none', edgecolor='orange', lw=2, ax=ax)
            # Label the image footprints
            for row in srca.gw.footprint_grid.itertuples(index=False):
                ax.scatter(row.geometry.centroid.x, row.geometry.centroid.y,
                            s=50, color='red', edgecolor='white', lw=1)
                ax.annotate(basename(row.footprint).replace('.TIF', ''),
                            (row.geometry.centroid.x, row.geometry.centroid.y),
                            color='black',
                            size=8,
                            ha='center',
                            va='center',
                            path_effects=[pe.withStroke(linewidth=1, foreground='white')])
            # Set the display bounds
            ax.set_ylim(srca.gw.footprint_grid.total_bounds[1]-10, srca.gw.footprint_grid.total_bounds[3]+10)
            ax.set_xlim(srca.gw.footprint_grid.total_bounds[0]-10, srca.gw.footprint_grid.total_bounds[2]+10)
    title = f'Image {bounds_by}' if bounds_by else str(Path(ref_image).name.split('.')[0]) + ' as reference'
    size = 12 if bounds_by else 8
    ax.set_title(title, size=size)
    plt.tight_layout(pad=1)
# %%
from geowombat.data import l8_224078_20200518
import rasterio
fig, ax = plt.subplots(dpi=200)
with gw.open(l8_224078_20200518, nodata=0) as src:
    src = src.gw.mask_nodata()
    src.sel(band=[3, 2, 1]).plot.imshow(robust=True, ax=ax)
plt.tight_layout(pad=1)
# %%
with rasterio.open("../data/LC08_L2SP_016040_20210317_20210328_02_T1_clip.tif", mode = "r", nodata = 0) as src:

    # Get red band
    band_red = src.read(3)

    # Get NIR band
    band_nir = src.read(4)

    # Allow division by zero
    np.seterr(divide = "ignore", invalid = "ignore")

    # Calculate NDVI
    ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)

# Set pixels whose values are outside the NDVI range (-1, 1) to NaN
# Likely due to errors in the Landsat imagery
ndvi[ndvi > 1] = np.nan
ndvi[ndvi < -1] = np.nan

# Plot raster
plt.imshow(ndvi)
plt.title("NDVI")
plt.show()

# Show raster values
print("Raster values:\n", ndvi)
# %%
import geowombat as gw
import matplotlib.pyplot as plt
fig, ax = plt.subplots(dpi=200)


LS = "../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF"
precip = "../data/precipitation_20200601_500m.tif"

with gw.config.update(ref_image=LS):
    with gw.open(precip, resampling="bilinear", nodata=-9999) as src:
        print(src)
        ax.imshow(src.data[0])
        
# %%
import matplotlib.pyplot as plt
fig, ax = plt.subplots(dpi=200)
from geowombat.data import rgbn

proj4 = "+proj=aea +lat_1=20 +lat_2=60 +lat_0=40 +lon_0=-96 +x_0=0 +y_0=0 +datum=NAD83 +units=m +no_defs"

with gw.config.update(ref_crs=proj4):
    with gw.open(rgbn, nodata=0) as src:
        # replace nodata with nan
        src = src.gw.mask_nodata()
        print(src.transform)
        print(src.crs)
        print(src.resampling)
        print(src.res)
        src.sel(band=[3,2,1]).plot.imshow(robust=True, ax=ax)

plt.tight_layout(pad=1)

# %%
from geowombat.data import l8_224078_20200518
 
with gw.config.update(scale_factor=0.0001):
  with gw.open(l8_224078_20200518) as src:
    print(src.values[0])
    print(src.scales)
    print(src.gw.scale_factor)

# %%
