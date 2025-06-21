# %%

import geopandas as gpd
import numpy as np
#shapefile_path = "./data/bus_kasugai.shp"
shapefile_path = "../data/bus.geojson"

def read_shapefile(file_path):
    gdf = gpd.read_file(file_path, encoding='UTF-8', errors="replace")
    gdf['normal_dist'] = np.random.normal(loc=0, scale=1, size=len(gdf))    
    new_gdf = gdf[gdf["normal_dist"] > 0]
    print(f"Read {len(gdf)} features from {file_path}")
    print(f"CRS: {gdf.crs}")
    print("columns: ",gdf.columns.tolist())

    print("somethng new")
    #gdf['normal_dist'].hist(bins=30, edgecolor='black')
    gdf.plot(figsize=(10, 10), edgecolor='black', column=None)
    print(gdf.head)
read_shapefile(shapefile_path) 


# %%
