# %%

import geopandas as gpd
import numpy as np
shapefile_path = "./data/bus_kasugai.shp"
def read_shapefile(file_path):
    gdf = gpd.read_file(file_path, encoding='shift_jis')
    gdf['normal_dist'] = np.random.normal(loc=0, scale=1, size=len(gdf))    
    new_gdf = gdf[gdf["normal_dist"] > 0]
    print(f"Read {len(gdf)} features from {file_path}")
    print(f"CRS: {gdf.crs}")
    print("columns: ",gdf.columns.tolist())


read_shapefile(shapefile_path) 
test add2

# %%
