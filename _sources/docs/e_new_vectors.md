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
  "description lang=en": "Learn how to create new vector data (shapefile), and assign a projection (CRS). This includes an example of plotting latitude longitude data stored in a .csv file."
  "description lang=fr": "Apprenez à modifier, sous-ensemble et tracer des données attributaires de données vectorielles (fichier de formes). Cela inclut un exemple de traçage des données de longitude de latitude ainsi que le sous-ensemble (indexation) par emplacement."
  "description lang=es": "Aprenda a cambiar, crear subconjuntos y trazar datos de atributos de datos vectoriales (shapefile). Esto incluye un ejemplo de trazado de datos de latitud y longitud, así como subconjuntos (indexación) por ubicación."
  "keywords": "spatial, attribute data, subset,  shapefile"
  "property=og:locale": "en_US"
---

(e_new_vectors)=
 
----------------

```{admonition} Learning Objectives
* Create new spatial objects (points, lines, polygons)
* Assign the correct projection or CRS
* Create points from a table or csv of lat and lon 
```
```{admonition} Review
* [CRS what is it?](d_crs_what_is_it.md)
* [Understand CRS codes](d_understand_crs_codes.md)
* [Vector data structures](c_vectors.md)
* [Find Lat Lon of your own points, lines, polygons](https://geojson.io/)
```
----------------


# Creating Spatial Vector Data
We often find ourselves in a situation where we need to generate new spatial data from scratch, or need to better understand how our data is constructed. This lesson will walk you through some of the most common forms of data generation. 
```{code-cell} ipython3
# Import necessary modules first
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import fiona
import matplotlib.pyplot as plt
plt.style.use('bmh') # better for plotting geometries vs general plots.
```


## Creating GeoDataFrame Geometries
A `GeoDataFrame` object is a `pandas.DataFrame` that has a column with geometry. An empty `GeoDataFrame` is just that, empty, essentially just like the pandas one. Let’s create an empty `GeoDataFrame` and create a new column called geometry that will contain our Shapely objects:

```{code-cell} ipython3
# Create an empty geopandas GeoDataFrame
newdata = gpd.GeoDataFrame()
print(newdata)
``` 

In order to have a working spatial dataframe we need define a few things:

### GeoDataFrame Components
- data: a pandas.DataFrame, dictionary, or empty list [] containing an desired attribute data. Use [] if no data is 
- crs:  Coordinate Reference System of the geometry objects. Can be anything accepted by `pyproj.CRS.from_user_input()`, such as an authority string (eg “EPSG:4326”) or a WKT string.
- geometry:  Column name in a DataFrame to use as geometry or Shapely point, line, or polygon object. 

Since geopandas takes advantage of Shapely geometric objects it is possible to create a Shapefile from a scratch by passing Shapely’s geometric objects into the GeoDataFrame. This is useful as it makes it easy to convert e.g. a text file that contains coordinates into a Shapefile.

 

Now we have a geometry column in our GeoDataFrame but we don’t have any data yet.

### Create Points from list of coordinates
Creating geopandas point objects is a snap! All we need is a coordinate pair from which we generate a Shapely point geometry object, we then create a dictionary that holds that geometry and any attributes we want, and a coordinate reference system. In this case we use a [ESPG code](d_understand_crs_codes.md).   
[Click here for a more detailed explanation of this process](e_points_the_long_way)

```{code-cell} ipython3
# Coordinates of the GW department of geography in Decimal Degrees
coordinate = [-77.04639494419096,  38.89934963421794]

# Create a Shapely polygon from the coordinate-tuple list
point_coord = Point(coordinate)

# create a dataframe with needed attributes and required geometry column
df = {'GWU': ['Dept Geography'], 'geometry': [point_coord]}

# Convert shapely object to a geodataframe 
point = gpd.GeoDataFrame(df, geometry='geometry', crs ="EPSG:4326")

# Let's see what we have
point.plot()
```
We can apply the same process to a set of points stored in a pandas dataframe. 

```{code-cell} ipython3
# list of attributes and coordinates
df = pd.DataFrame(
    {'City': ['Buenos Aires', 'Brasilia', 'Santiago', 'Bogota', 'Caracas'],
     'Country': ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Venezuela'],
     'lat': [-34.58, -15.78, -33.45, 4.60, 10.48],
     'lon': [-58.66, -47.91, -70.66, -74.08, -66.86]})

# Create a Shapely points from the coordinate-tuple list
ply_coord = [Point(x, y) for x, y in zip(df.lat, df.lon)]

# Convert shapely object to a geodataframe with a crs
poly = gpd.GeoDataFrame(df, geometry=ply_coord, crs ="EPSG:4326")

# Let's see what we have
poly.plot()
```
[adapted from geopandas](https://geopandas.org/gallery/create_geopandas_from_pandas.html)

### Creating Points from csv of latitude and longitude (lat, lon)

One of the most common data creation tasks is creating a shapefile from a list of points or a `.csv` file. Luckily getting this data into usable format is easy enough. 

First we have to create an example `.csv` dataset to work from:

```{code-cell} ipython3
import pandas as pd
# create an outline of Washington DC and write to csv
path_to_csv = r'../temp/points.csv'
points = {'Corner':['N','E','S','W'],
          'lon': [-77.0412826538086, -77.11681365966797, -77.01896667480469, -77.0412826538086], 
          'lat': [38.99570671505043, 38.936713143230044, 38.807610542357594, 38.99570671505043]}
points = pd.DataFrame.from_dict(points)
points.to_csv(path_to_csv)              
```
To create a `geodataframe` from our data you simply need to read it back in, an specify the geometry column values using `points_from_xy` pointing it to the correct columns of `df`, namely `df.lon` anf `df.lat`.

```{code-cell} ipython3
# read the point data in 
df = pd.read_csv(path_to_csv)

# Create a geodataframe from the data using and 'EPSG' code to assign WGS84 coordinate reference system
points= gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(x=df.lon, y=df.lat), crs = 'EPSG:4326')
points
```
In this case `points_from_xy()` was used to transform lat and lon into a list of `shapely.Point` objects. This then is used as the geometry for the GeoDataFrame. (`points_from_xy()` is simply an enhanced wrapper for `[Point(x, y) for x, y in zip(df.lon, df.lat)]`)

```{tip}  
- Although we say "lat lon" python uses "lon lat" instead, this follows the preference for using x,y for notation. 
- Typically, like the data above, these data are stored in WGS84 lat lon, but be sure to check this, another common format is UTM coordinates (look for values around 500,000 east to west and measured in meters)
```

### Creating Spatial lines

Following the examples above we can specify lines easily. In this case let's say we have lines tracking three people riding their bikes through town. We keep track of their unique id `ID`, their location `X,Y`, and their `Speed`, and read in the data below:

```{code-cell} ipython3
from io import StringIO 
data = """
ID,X,Y,Speed
1,  -87.789,  41.976,  16
1,  -87.482,  41.677,  17
2,  -87.739,  41.876,  16
2,  -87.681,  41.798,  16
2,  -87.599,  41.708,  16
3,  -87.599,  41.908,  17
3,  -87.598,  41.708,  17
3,  -87.643,  41.675,  17
"""
# use StringIO to read in text chunk
df = pd.read_table(StringIO(data), sep=',')
```

Let's convert these to points and take a look. Notice that points are not a good replacement for lines in the case, we have three individuals, and they need to be treated separately.


```{code-cell} ipython3
#zip the coordinates into a point object and convert to a GeoData Frame
points = [Point(xy) for xy in zip(df.X, df.Y)]
geo_df = gpd.GeoDataFrame(df, geometry=points, crs = 'EPSG:4326')
geo_df.plot()
```
Now let's tread these data as lines, we can take advantage of the column `ID` to `.groupby`. Luckily geopandas `.groupby` is consistent with the use in pandas. So here we `.groupby(['ID'])`, for each `ID` group we convert the values to a list, and store it in a Fiona `LineString` object. 

```{code-cell} ipython3
# treat each `ID` group of points as a line
lines = geo_df.groupby(['ID'])['geometry'].apply(lambda x:  LineString(x.tolist()))

# store as a GeodataFrame and add 'ID' as a column (currently stored as the 'index')
lines = gpd.GeoDataFrame(lines, geometry='geometry', crs="EPSG:4326") 
lines.reset_index(inplace=True)
lines.plot(column='ID')
```
Now we can see that each line is treated separately by `ID`, and plot them using `.plot(column='ID')`.


### Creating Spatial Polygons

Creating a polyon in geopandas is very similiar to the other exercises. First we create a Fiona geometry object from our coordinates, add that to a dataframe with any attributes and then create a `GeoDataFrame` with an assigned coordinate reference system (CRS).

```{code-cell} ipython3
# list of coordindate pairs
coordinates = [[ -77.0412826538086, 38.99570671505043 ], [ -77.11681365966797, 38.936713143230044 ], [ -77.01896667480469, 38.807610542357594],
               [-76.90910339355469,  38.892636142310295]]           

# Create a Shapely polygon from the coordinate-tuple list
ply_coord = Polygon(coordinates)

# create a dictionary with needed attributes and required geometry column
df = {'Attribute': ['name1'], 'geometry': ply_coord}

# Convert shapely object to a geodataframe 
poly = gpd.GeoDataFrame(df, geometry='geometry', crs ="EPSG:4326")

# Let's see what we have
poly.plot()
```



(e_points_the_long_way)=

### Creating Spatial Points (admittedly the long way)


Since geopandas takes advantage of Shapely geometric objects it is possible to create a Shapefile from a scratch by passing Shapely’s geometric objects into the GeoDataFrame. This is useful as it makes it easy to convert e.g. a text file that contains coordinates into a Shapefile.

Let’s create an empty `GeoDataFrame` and create a new column called geometry that will contain our Shapely objects:

```{code-cell} ipython3
# Create an empty geopandas GeoDataFrame
newdata = gpd.GeoDataFrame()
# Create a new column called 'geometry' to the GeoDataFrame
newdata['geometry'] = None

print(newdata)
```  

Let’s create a Shapely Point representing the GWU Department of Geography that we can insert to our GeoDataFrame:

```{code-cell} ipython3
# Coordinates of the GW department of geography in Decimal Degrees
coordinates = (-77.04639494419096,  38.89934963421794)

# Create a Shapely polygon from the coordinate-tuple list
point = Point(coordinates)

# Let's see what we have
point
```

Okay, so now we have appropriate Polygon -object.

Let’s insert the polygon into our ‘geometry’ column in our GeoDataFrame:

```{code-cell} ipython3
# Insert the polygon into 'geometry' -column at index 0
newdata.loc[0, 'geometry'] = point

# Let's see what we have now
newdata
```

Now we have a GeoDataFrame with Point that we can export to a Shapefile.

Let’s add another column to our GeoDataFrame called Location with text GWU Geography.

```{code-cell} ipython3
# Add a new column and insert data
newdata.loc[0, 'Location'] = 'GWU Geography'

# Let's check the data
newdata
```
Okay, now we have additional information that is useful to be able to recognize what the feature represents.

Before exporting the data it is useful to determine the coordinate reference system (CRS, 'projection') for the GeoDataFrame.

GeoDataFrame has a property called `.crs` that ([review here](d_understand_crs_codes.md)) shows the coordinate system of the data which is empty (None) in our case since we are creating the data from the scratch (e.g. `newdata.crs` returns `None`).

Let’s add a crs for our GeoDataFrame. A Python module called fiona has a nice function called from_epsg() for passing coordinate system for the GeoDataFrame. Next we will use that and determine the projection to WGS84 (epsg code: 4326) which is the most common choice for lat lon CRSs:

```{code-cell} ipython3
# Import specific function 'from_epsg' from fiona module
from fiona.crs import from_epsg

# Set the GeoDataFrame's coordinate system to WGS84
newdata.crs = from_epsg(code = 4326)

# Let's see how the crs definition looks like
newdata.crs
```
Finally, we can export the data using GeoDataFrames .to_file() -function. The function works similarly as numpy or pandas, but here we only need to provide the output path for the Shapefile. Easy isn’t it!:

```{code-cell} ipython3
# Determine the output path for the Shapefile
outfp = r"../temp/gwu_geog.shp"

# Write the data into that Shapefile
newdata.to_file(outfp)
```

```{tip}  Because GeoPandas are so intertwined spend the time to learn more about here [Pandas User Guide](https://pandas.pydata.org/pandas-docs/stable/user_guide/index.html)
```

-------------------

[Adapted from Intro to Python GIS](https://automating-gis-processes.github.io/CSC18/lessons/L2/geopandas-basics.html#creating-geometries-into-a-geodataframe)

