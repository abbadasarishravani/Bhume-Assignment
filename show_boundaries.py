import rasterio
import numpy as np
import matplotlib.pyplot as plt

path = "data/34855_vadnerbhairav_chandavad_nashik/boundaries.tif"

with rasterio.open(path) as src:
    img = src.read(1)

binary = (img > 0).astype(int)

ys, xs = np.where(binary == 1)

print("Total boundary points:", len(xs))

# remove edge artifacts (important!)
mask = (xs > 10) & (ys > 10)

xs_clean = xs[mask]
ys_clean = ys[mask]

print("Cleaned points:", len(xs_clean))

print("Sample real coordinates:")
for i in range(10):
    print(xs_clean[i], ys_clean[i])

plt.figure(figsize=(6,6))
plt.scatter(xs_clean[::800], ys_clean[::800], s=1)
plt.title("Clean Boundary Points (Filtered)")
plt.gca().invert_yaxis()
plt.show()