import rasterio

path = "data/34855_vadnerbhairav_chandavad_nashik/boundaries.tif"

with rasterio.open(path) as src:
    print("CRS:", src.crs)
    print("Width:", src.width)
    print("Height:", src.height)
    print("Bounds:", src.bounds)

    print("\nTransform:")
    print(src.transform)