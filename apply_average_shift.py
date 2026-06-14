import geopandas as gpd
from shapely.affinity import translate

# -----------------------------
# Input file
# -----------------------------
input_file = "data/predictions_baseline.geojson"

output_file = "data/predictions_average_shift.geojson"

# -----------------------------
# Average shift from example truths
# -----------------------------
DX = -5.25   # meters
DY = 12.23   # meters

# -----------------------------
# Read GeoJSON
# -----------------------------
gdf = gpd.read_file(input_file)

print("Loaded", len(gdf), "plots")
print("Original CRS:", gdf.crs)

# Convert to meter-based CRS
gdf = gdf.to_crs("EPSG:3857")

# Apply shift
gdf["geometry"] = gdf["geometry"].apply(
    lambda geom: translate(
        geom,
        xoff=DX,
        yoff=DY
    )
)

# Convert back to lat/lon
gdf = gdf.to_crs("EPSG:4326")

# Update metadata
gdf["status"] = "corrected"

gdf["confidence"] = 0.6

gdf["method_note"] = (
    f"average shift dx={DX:.2f}m dy={DY:.2f}m"
)

# Save
gdf.to_file(
    output_file,
    driver="GeoJSON"
)

print("\nSaved:", output_file)
print("Done!")