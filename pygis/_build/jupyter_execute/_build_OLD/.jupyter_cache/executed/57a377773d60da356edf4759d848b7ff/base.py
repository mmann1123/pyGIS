import geopandas
world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
world.columns

world['m_pop_est'] = world['pop_est'] / 1e6
world.head()

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))
southern_world = world.cx[ : , :0 ]
southern_world.plot(figsize=(10, 3))

world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_cities'))
northern_world = world.cx[ : , 0: ]
northern_world.plot(figsize=(10, 3))