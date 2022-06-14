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
    driver="GTiff",
    height=Z.shape[0],
    width=Z.shape[1],
    count=1,
    dtype=Z.dtype,
    crs="+proj=latlong",
    transform=transform,
) as dst:

    # check for multiband
    if len(Z.shape) == 3:
        # write each band individually
        for band in range(len(Z)):
            # write data, band # (starting from 1)
            dst.write(Z[band], band + 1)
    # write single band
    else:
        dst.write(Z, 1)
# %%
