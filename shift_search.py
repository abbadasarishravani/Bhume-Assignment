import geopandas as gpd
import rasterio
import numpy as np
from rasterio.features import rasterize
from shapely.affinity import translate

# Load raster
raster_path = "data/34855_vadnerbhairav_chandavad_nashik/boundaries.tif"

with rasterio.open(raster_path) as src:
    img = src.read(1)
    transform = src.transform
    crs = src.crs

binary = (img > 0).astype(np.uint8)

# Load polygon
geo_path = "data/34855_vadnerbhairav_chandavad_nashik/example_truths.geojson"
gdf = gpd.read_file(geo_path).to_crs(crs)

geom = gdf.iloc[0].geometry

best_iou = 0
best_dx = 0
best_dy = 0

# small search window (IMPORTANT)
for dx in range(-30, 31, 5):
    for dy in range(-30, 31, 5):

        shifted = translate(geom, xoff=dx, yoff=dy)

        poly_mask = rasterize(
            [(shifted, 1)],
            out_shape=binary.shape,
            transform=transform,
            fill=0,
            dtype=np.uint8
        )

        intersection = np.sum((poly_mask == 1) & (binary == 1))
        union = np.sum((poly_mask == 1) | (binary == 1))

        iou = intersection / union if union != 0 else 0

        if iou > best_iou:
            best_iou = iou
            best_dx = dx
            best_dy = dy

print("Best IoU:", best_iou)
print("Best dx:", best_dx)
print("Best dy:", best_dy)