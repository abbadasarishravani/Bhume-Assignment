#!/usr/bin/env python3
"""
Simple visualization of a plot and its satellite image.
Run: python visualize_plot.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import PatchCollection
import numpy as np
from pathlib import Path

# Since uv is not available, we'll use direct imports with the assumption
# that the dependencies are installed or we'll need to install them
try:
    from bhume import load, patch_for_plot
    from bhume.geo import open_imagery
except ImportError:
    print("Dependencies not installed. This script requires the bhume package.")
    print("Please install dependencies first using: uv sync")
    exit(1)

def visualize_plot(village_dir, plot_number=None, pad_m=50):
    """
    Visualize a plot overlaid on its satellite imagery.
    
    Args:
        village_dir: Path to the village data directory
        plot_number: Specific plot to visualize (if None, uses first plot)
        pad_m: Padding in meters around the plot
    """
    # Load village data
    village = load(village_dir)
    
    # Get plot number (first plot if not specified)
    if plot_number is None:
        plot_number = village.plots.index[0]
    
    print(f"Visualizing plot {plot_number}")
    
    # Get the plot geometry
    plot_geom = village.plot(plot_number)
    
    # Open imagery and extract patch
    with open_imagery(village.imagery_path) as src:
        patch = patch_for_plot(src, plot_geom, pad_m=pad_m)
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # Display the satellite image
    ax.imshow(patch.image)
    ax.set_title(f'Plot {plot_number} - Satellite Imagery with Official Boundary')
    ax.axis('off')
    
    # Convert plot geometry to pixel coordinates for overlay
    from bhume.geo import geom_to_imagery_crs
    geom_imagery = geom_to_imagery_crs(src, plot_geom)
    
    # Get the bounds in imagery CRS
    minx, miny, maxx, maxy = geom_imagery.bounds
    
    # Convert to pixel coordinates
    # The patch transform maps pixel (col, row) to imagery (x, y)
    # We need the inverse: imagery (x, y) to pixel (col, row)
    transform = patch.transform
    col_min, row_max = transform * (minx, maxy)  # Top-left
    col_max, row_min = transform * (maxx, miny)  # Bottom-right
    
    # Create a polygon patch for the plot boundary
    # Get the actual polygon coordinates in pixel space
    if geom_imagery.geom_type == 'Polygon':
        coords = list(geom_imagery.exterior.coords)
        pixel_coords = []
        for x, y in coords:
            col, row = transform * (x, y)
            pixel_coords.append([col, row])
        pixel_coords = np.array(pixel_coords)
        
        # Draw the polygon
        polygon = patches.Polygon(pixel_coords, 
                                 linewidth=2, 
                                 edgecolor='red', 
                                 facecolor='none',
                                 label='Official Boundary')
        ax.add_patch(polygon)
    
    elif geom_imagery.geom_type == 'MultiPolygon':
        for poly in geom_imagery.geoms:
            coords = list(poly.exterior.coords)
            pixel_coords = []
            for x, y in coords:
                col, row = transform * (x, y)
                pixel_coords.append([col, row])
            pixel_coords = np.array(pixel_coords)
            
            polygon = patches.Polygon(pixel_coords, 
                                     linewidth=2, 
                                     edgecolor='red', 
                                     facecolor='none')
            ax.add_patch(polygon)
    
    ax.legend()
    plt.tight_layout()
    
    # Save the figure
    output_path = Path(village_dir) / f'plot_{plot_number}_visualization.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved visualization to {output_path}")
    
    # Also show it
    plt.show()
    
    return output_path


if __name__ == '__main__':
    import sys
    
    village_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    plot_num = sys.argv[2] if len(sys.argv) > 2 else None
    
    visualize_plot(village_dir, plot_num)
