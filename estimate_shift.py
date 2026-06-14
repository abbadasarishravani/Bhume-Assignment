import geopandas as gpd
import rasterio
import numpy as np
from rasterio.features import rasterize

# Load raster
raster_path = "data/34855_vadnerbhairav_chandavad_nashik/boundaries.tif"

with rasterio.open(raster_path) as src:
    img = src.read(1)
    transform = src.transform
    raster_crs = src.crs

binary = (img > 0).astype(np.uint8)

# Load polygon
geo_path = "data/34855_vadnerbhairav_chandavad_nashik/example_truths.geojson"
gdf = gpd.read_file(geo_path)

# 🔥 FIX: reproject polygon to raster CRS
gdf = gdf.to_crs(raster_crs)

geom = gdf.iloc[0].geometry

# Rasterize polygon correctly
poly_mask = rasterize(
    [(geom, 1)],
    out_shape=binary.shape,
    transform=transform,
    fill=0,
    dtype=np.uint8
)

# Compute IoU
intersection = np.sum((poly_mask == 1) & (binary == 1))
union = np.sum((poly_mask == 1) | (binary == 1))

iou = intersection / union if union != 0 else 0

print("IoU after CRS fix:", iou)