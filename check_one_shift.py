import geopandas as gpd
import matplotlib.pyplot as plt

path = "data/34855_vadnerbhairav_chandavad_nashik/example_truths.geojson"

gdf = gpd.read_file(path)

geom = gdf.iloc[0].geometry

plt.figure(figsize=(6,6))

if geom.geom_type == "MultiPolygon":
    for poly in geom.geoms:
        x, y = poly.exterior.xy
        plt.plot(x, y)

plt.title("Official Polygon (Lat/Lon Space)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

# 🔥 SAVE instead of show
output_path = "polygon_debug.png"
plt.savefig(output_path, dpi=200)
print("Saved plot to:", output_path)