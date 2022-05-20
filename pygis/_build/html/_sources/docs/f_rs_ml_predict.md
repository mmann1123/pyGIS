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
  "description lang=en": "Spatial classification and prediction models. Train and fit sklearn models on raster data including LandSat or other gridded data. "
  "description lang=fr": "Classification spatiale et modèles de prédiction. Entraînez et adaptez des modèles sklearn sur des données raster, y compris LandSat ou d'autres données maillées."
  "description lang=es": "Modelos de clasificación y predicción espacial. Entrene y ajuste modelos sklearn en datos ráster, incluido LandSat u otros datos cuadriculados."
  "keywords": "sklearn, spatial,raster, remote sensing, time series, landsat, sentinel"
  "property=og:locale": "en_US"
---

(f_rs_ml_predict)=


---------------
```{admonition} Learning Objectives
  - Fit and predict machine learning models to make spatial predictions
  - Predict landcover or continuous models 
  - Make predictions using timeseries data

```
```{admonition} Review
* [Geowombat IO](f_rs_io.md)
* [Geowombat Extraction](f_rs_extraction.md)
* [Sklearn_xarray](https://phausamann.github.io/sklearn-xarray/)
* [Sklearn pipelines](https://medium.com/vickdata/a-simple-guide-to-scikit-learn-pipelines-4ac0d974bdcf)
```
--------------


# Spatial Prediction using ML in Python
## Create Land Use Classification using Geowombat & Sklearn

The most common task for remotely sensed data is creating land cover classification. In this tutorial we will walk you through how to train a ML model using raster data. These methods are heavily dependent on the great package [sklearn_xarray](https://phausamann.github.io/sklearn-xarray/). To understand the pipeline commands please see their documentation. 

In the following example we will use Landsat data, some training data to train a sklearn model. In order to do this we first need  to have land classifications for a set of points of polygons. In this case we have three polygons with the classes ['water','crop','tree','developed']. The first step is to use `LabelEncoder` to convert these to integer based categories, which we store in a new column called 'lc'.

```{code-cell} ipython3

import geowombat as gw
from geowombat.data import l8_224078_20200518, l8_224078_20200518_polygons

from geowombat.ml import fit
import geopandas as gpd
from sklearn_xarray.preprocessing import Featurizer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.naive_bayes import GaussianNB

le = LabelEncoder()

# The labels are string names, so here we convert them to integers
labels = gpd.read_file(l8_224078_20200518_polygons)
labels['lc'] = le.fit(labels.name).transform(labels.name)
print(labels)
```
We are then going to generate our sklearn pipeline ([see simple tutorial here](https://medium.com/vickdata/a-simple-guide-to-scikit-learn-pipelines-4ac0d974bdcf)). A pipeline simply allows us to pass a numpy array through a defined set of operations. In this case the data is passed through the following operations:

 * `Featurizer`: [Stacks](https://phausamann.github.io/sklearn-xarray/content/api/preprocessing.html?highlight=featurizer#sklearn_xarray.preprocessing.Featurizer) a numpy array for use in sklearn
 * `StandardScaler`: [Normalizes](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html) all variables by removing the mean and scaling to unit variance
 * `PCA`: Calculates [Principal Components](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html?highlight=pca#sklearn.decomposition.PCA) to reduce dimensionality. 
 * `GaussianNB`: Fits a [Gaussian Naive Bayes](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html?highlight=gaussiannb#sklearn.naive_bayes.GaussianNB) model for a quick classification. 

 In this example we will just fit a model. The trained pipeline can be accessed with the returned `clf` object. 

```{code-cell} ipython3

# Use a data pipeline
pl = Pipeline([('featurizer', Featurizer()),
                ('scaler', StandardScaler()),
                ('pca', PCA()),
                ('clf', GaussianNB())])

# Fit the classifier
with gw.config.update(ref_res=100):
    with gw.open(l8_224078_20200518) as src:
        X, clf = fit(src, labels, pl, col='lc')

print(clf)
```
In order to fit and predict to our original data we simply use `fit_predict`. 

```{code-cell} ipython3
import matplotlib.pyplot as plt
plt.figure(figsize=(5, 5)) 
fig, ax = plt.subplots(dpi=200,figsize=(10,10))

from geowombat.ml import fit_predict

with gw.config.update(ref_res=100):
    with gw.open(l8_224078_20200518) as src:
        y = fit_predict(src, labels, pl, col='lc')
        print(y)
        y.plot(robust=True, ax=ax)
plt.tight_layout(pad=1)

```

## Spatial prediction with time series stack using Geowombat & Sklearn

If you have a stack of time series data it is simple to apply the same method as we described previously, except we need to open multiple images, set `stack_dim` to 'time' and set the `time_names`.  *Note* we are just pretending we have two dates of LandSat imagery here. 

```{code-cell} ipython3
with gw.config.update(ref_res=100):
   with gw.open([l8_224078_20200518, l8_224078_20200518], time_names=['t1', 't2'], stack_dim='time') as src:
        y = fit_predict(src, labels, pl, col='lc')
        print(y)
```