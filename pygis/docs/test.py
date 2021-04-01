# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

plt.style.use("bmh")  # better for plotting geometries vs general plots.


d = {
    "name": [
        "Washington\n(38.90, -77.03)",
        "Baltimore\n(39.29, -76.61)",
        "Fredrick\n(39.41,-77.40)",
    ],
    "geometry": [
        Point(-77.036873, 38.907192),
        Point(-76.612190, 39.290386,),
        Point(-77.408456, 39.412006),
    ],
}

gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")

fig, ax = plt.subplots(figsize=(12, 6))
gdf.plot(ax=ax)
plt.ylim([38.8, 39.6])
plt.xlim([-77.5, -76.2])

for x, y, label in zip(gdf.geometry.x, gdf.geometry.y, gdf.name):
    ax.annotate(label, xy=(x, y), xytext=(3, 3), textcoords="offset points")


# %%


# %%

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString

plt.style.use("bmh")  # better for plotting geometries vs general plots.

d = {
    "name": ["Washington\n(38.90, -77.03)"],
    "geometry": [
        LineString(
            [
                Point(-77.036873, 38.907192),
                Point(-76.612190, 39.290386,),
                Point(-77.408456, 39.412006),
            ]
        )
    ],
}
gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")

fig, ax = plt.subplots(figsize=(12, 6))
gdf.plot(ax=ax)


# %%
from shapely.geometry import Polygon

d = {
    "name": ["Washington\n(38.90, -77.03)"],
    "geometry": [
        Polygon(
            [
                Point(-77.036873, 38.907192),
                Point(-76.612190, 39.290386,),
                Point(-77.408456, 39.412006),
            ]
        )
    ],
}
gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")

fig, ax = plt.subplots(figsize=(12, 6))
gdf.plot(ax=ax)


# %%
import numpy as np

X = np.random.randint(256, size=(10, 10))

fig = plt.figure(figsize=(8, 6))
plt.imshow(X)
plt.title("Plot 2D array")
plt.show()


# %%
import geopandas

l = geopandas.GeoSeries(
    [
        LineString(
            [
                Point(-77.036873, 38.907192),
                Point(-76.612190, 39.290386,),
                Point(-77.408456, 39.412006),
            ]
        )
    ]
)
l


# %%
from shapely.geometry import Polygon

p = geopandas.GeoSeries(
    [
        Polygon(
            [
                Point(-77.036873, 38.907192),
                Point(-76.612190, 39.290386,),
                Point(-77.408456, 39.412006),
            ]
        )
    ]
)
p


# %%
geopandas.datasets.available


# %%
cities = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
cities.head()


# %%
world = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))

world.cx


# %%
import pandas

name = "fudge"
name[0:3]


# %%
world = geopandas.read_file(geopandas.datasets.get_path("naturalearth_cities"))
northern_world = world.iloc[0:4]
northern_world.plot(figsize=(10, 3))


# %%


# %%


# %%
import geopandas
import contextily as ctx

cities = geopandas.read_file(geopandas.datasets.get_path("naturalearth_cities"))
cities = cities[cities.name == "Washington, D.C."]
cities = cities.to_crs(epsg=3857)  # project to webmercator

ax = cities.plot(figsize=(10, 10), alpha=0.5, edgecolor="k")
ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=6, reset_extent=True)
# ctx.add_basemap(ax, url=ctx.providers.Stamen.Toner,zoom = 6, reset_extent = True)


# %%
import matplotlib.pyplot as plt

ghent_img, ghent_ext = ctx.bounds2img(
    w=-8.8, s=4.5, e=-8.4, n=4.9, ll=True, source=ctx.providers.Stamen.Toner, zoom=10,
)
plt.imshow(ghent_img, extent=ghent_ext)


# %%
# Import necessary modules first
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import fiona

# Create an empty geopandas GeoDataFrame
newdata = gpd.GeoDataFrame()
# Create a new column called 'geometry' to the GeoDataFrame
newdata["geometry"] = None

print(newdata)


# Coordinates of the Helsinki Senate square in Decimal Degrees
coordinates = (-77.04639494419096, 38.89934963421794)

# Create a Shapely polygon from the coordinate-tuple list
point = Point(coordinates)

# Let's see what we have
point


# %%
import pandas as pd
import geopandas

points = {
    "lon": [
        -77.0412826538086,
        -77.11681365966797,
        -77.01896667480469,
        -77.0412826538086,
    ],
    "lat": [
        38.99570671505043,
        38.936713143230044,
        38.807610542357594,
        38.99570671505043,
    ],
}
points = pd.DataFrame.from_dict(points)
points.to_csv("~/temp/points.csv")


# %%
path_to_csv = "~/temp/points.csv"
from fiona.crs import from_epsg

from geopandas import GeoDataFrame as gdf

df = pd.read_csv(path_to_csv)

# Create a geodataframe from the data using from_epsg to assign WGS84 coordinate reference system
points = gdf(
    df,
    geometry=geopandas.points_from_xy(x=points.lon, y=points.lat),
    crs=from_epsg(4326),
)
points


# %%
# Import necessary modules first
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import fiona

# Create an empty geopandas GeoDataFrame
newdata = gpd.GeoDataFrame()
# Create a new column called 'geometry' to the GeoDataFrame
newdata["geometry"] = None

print(newdata)

# Coordinates of the Helsinki Senate square in Decimal Degrees
coordinates = (-77.04639494419096, 38.89934963421794)

# Create a Shapely polygon from the coordinate-tuple list
point = Point(coordinates)

# Let's see what we have
point

# Insert the polygon into 'geometry' -column at index 0
newdata.loc[0, "geometry"] = point

# Let's see what we have now
newdata

# Add a new column and insert data
newdata.loc[0, "Location"] = "GWU Geography"

# Let's check the data
newdata

# Import specific function 'from_epsg' from fiona module
from fiona.crs import from_epsg

# Set the GeoDataFrame's coordinate system to WGS84
newdata.crs = from_epsg(code=4326)

# Let's see how the crs definition looks like
newdata.crs

# Determine the output path for the Shapefile
outfp = r"../temp/gwu_geog.shp"

# Write the data into that Shapefile
newdata.to_file(outfp)


# %%
for x, y in [
    [-77.0412826538086, 38.99570671505043],
    [-77.11681365966797, 38.936713143230044],
    [-77.01896667480469, 38.807610542357594],
    [-76.90910339355469, 38.892636142310295],
]:
    print(x, y)


# %%
coord_list = [
    [-77.0412826538086, 38.99570671505043],
    [-77.11681365966797, 38.936713143230044],
    [-77.01896667480469, 38.807610542357594],
    [-76.90910339355469, 38.892636142310295],
]
[(x, y) for x, y in coord_list]


# %%
from io import StringIO

data = """
ID,X,Y,Speed
1,  -87.78976,  41.97658,   16
1,  -87.48234,  41.677342,  17
2,  -87.73956,  41.876827,  16
2,  -87.68161,  41.79886,   16
2,  -87.5999,   41.7083,    16
3,  -87.59918,  41.908485,  17
3,  -87.59857,  41.708393,  17
3,  -87.64391,  41.675133,  17
"""

df = pd.read_table(StringIO(data), sep=",")
print(df.columns)
df


# %%


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, shape

import matplotlib.pyplot as plt

plt.style.use("bmh")  # better for plotting geometries vs general plots.

# zip the coordinates into a point object and convert to a GeoData Frame
geometry = [Point(xy) for xy in zip(df.X, df.Y)]
geo_df = gpd.GeoDataFrame(df, geometry=geometry)
geo_df.plot()


# %%

geo_df2 = geo_df.groupby(["ID"])["geometry"].apply(lambda x: LineString(x.tolist()))
geo_df2 = gpd.GeoDataFrame(geo_df2, geometry="geometry", crs="EPSG:4326")
geo_df2.reset_index(inplace=True)
geo_df2.plot(column="ID")


# %%


# %%
# list of coordindate pairs
coordinates = [
    [-77.0412826538086, 38.99570671505043],
    [-77.11681365966797, 38.936713143230044],
    [-77.01896667480469, 38.807610542357594],
    [-76.90910339355469, 38.892636142310295],
]

# Create a Shapely polygon from the coordinate-tuple list
poly = Polygon(coordinates)

# create a dataframe with needed attributes and required geometry column
df = {"GWU": ["name1"], "geometry": poly}

# Convert shapely object to a geodataframe
poly = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

# Let's see what we have
poly.plot()


# %%

# Coordinates of the GW department of geography in Decimal Degrees
coordinate = [-77.04639494419096, 38.89934963421794]

# Create a Shapely polygon from the coordinate-tuple list
point_coord = Point(coordinate)

# create a dataframe with needed attributes and required geometry column
df = {"GWU": ["Dept Geography"], "geometry": [point_coord]}

# Convert shapely object to a geodataframe
point = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

# Let's see what we have
point.plot()


# %%
points = [Point(xy) for xy in zip(df.X, df.Y)]
geo_df = gpd.GeoDataFrame(df, geometry=points, crs=from_epsg(4326))


# list of coordindate pairs
coordinates = [
    [-77.0412826538086, 38.99570671505043],
    [-77.11681365966797, 38.936713143230044],
    [-77.01896667480469, 38.807610542357594],
    [-76.90910339355469, 38.892636142310295],
]

# Create a Shapely polygon from the coordinate-tuple list
ply_coord = Polygon(coordinates)

# create a dataframe with needed attributes and required geometry column
df = {"Attribute": ["name1"], "geometry": ply_coord}

# Convert shapely object to a geodataframe
poly = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

# Let's see what we have
poly.plot()


# %%
newdata = gpd.GeoDataFrame()
print(newdata)


# %%
import numpy as np

x = np.linspace(-90, 90, 6)
y = np.linspace(90, -90, 6)
X, Y = np.meshgrid(x, y)
X


# %%
Y


# %%
Z1 = np.abs(((X - 10) ** 2 + (Y - 10) ** 2) / 1 ** 2)
Z2 = np.abs(((X + 10) ** 2 + (Y + 10) ** 2) / 2.5 ** 2)
Z = Z1 - Z2
Z


# %%
X = np.random.randint(256, size=(10, 10))
plt.imshow(Z)
plt.title("Plot 2D array")
plt.show()


# %%
from rasterio.transform import Affine

xres = (x[-1] - x[0]) / len(x)
yres = (y[-1] - y[0]) / len(y)
print(Affine.translation(x[0] - xres / 2, y[0] - yres / 2))
transform = Affine.translation(x[0] - xres / 2, y[0] - yres / 2) * Affine.scale(
    xres, yres
)
print("--------------")
print(Affine.scale(xres, yres))
print("--------------")
print(transform)


# %%
xres


# %%
transform * (0, 0)


# %%
transform * (3, 3)


# %%
import numpy as np

x = np.linspace(-90, 90, 6)
y = np.linspace(90, -90, 6)
X, Y = np.meshgrid(x, y)
X

Y

import matplotlib.pyplot as plt

Z1 = np.abs(((X - 10) ** 2 + (Y - 10) ** 2) / 1 ** 2)
Z2 = np.abs(((X + 10) ** 2 + (Y + 10) ** 2) / 2.5 ** 2)
Z = Z1 - Z2

plt.imshow(Z)
plt.title("Temperature")
plt.show()


# %%
from rasterio.transform import Affine

xres = (x[-1] - x[0]) / len(x)
yres = (y[-1] - y[0]) / len(y)

transform = Affine.translation(x[0] - xres / 2, y[0] - yres / 2) * Affine.scale(
    xres, yres
)


# %%
import rasterio

#%%

with rasterio.open(
    "../temp/temperature.tif",
    mode="w",
    driver="GTiff",
    height=Z.shape[0],
    width=Z.shape[1],
    count=1,
    dtype=Z.dtype,
    crs="+proj=latlong",
    transform=transform,
) as new_dataset:
    new_dataset.write(Z, 1)

# %% [markdown]

import matplotlib.pyplot as plt

data = rasterio.open("../temp/temperature.tif")

plt.imshow(data.read(1), cmap="BrBG")
plt.title("Temperature")
plt.show()

# %%
data = rasterio.open(
    "../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF", nodata=0, mask=True
)
data.nodatevals = (0, 0, 0)

from rasterio.plot import show

show(data)

#%%
import rasterio

with rasterio.open(
    "../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF", mode="r", nodata=0
) as src:
    profile = src.profile
    print(src.read([1]))
    arr = src.read([3, 2, 1])
    # print("Array shape:", arr.shape)
    # print(profile)

# %%
from rasterio.plot import show

show(arr)

from scipy import stats

print(stats.describe(arr.ravel()))

#%%
scaled_arr = arr / 100
scaled_arr.dtype

# %%
profile = src.profile
profile.update(nodata=0, compress="lzw", dtype=scaled_arr.dtype)

with rasterio.open(
    "../temp/LS_scaled_20200518.tif", mode="w", **profile,
) as new_dataset:

    new_dataset.write(scaled_arr, [1, 2, 3])

#%%
import matplotlib.pyplot as plt

with rasterio.open("../temp/LS_scaled_20200518.tif", mode="r") as src:
    show(src, adjust=None)


# %%
import geowombat as gw
import matplotlib.pyplot as plt

fig, ax = plt.subplots(dpi=200)

with gw.config.update(sensor="bgr"):
    with gw.open("../data/LC08_L1TP_224078_20200518_20200518_01_RT.TIF") as src:
        print(src.band)
        temp = src.where(src != 0).sel(band=["red", "green", "blue"])
        temp.gw.imshow(robust=True, ax=ax)
        temp.gw.to_raster(
            "../temp/LS_scaled_20200518.tif", verbose=0, n_workers=4, overwrite=True
        )


# %%

