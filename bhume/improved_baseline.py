"""Improved baseline using local shifts via spatial clustering.

This beats the global median shift by recognizing that the error varies
across the village. We cluster plots spatially and apply different shifts
to different clusters.
"""

from __future__ import annotations

import statistics
from typing import Dict, Tuple

import geopandas as gpd
import numpy as np
from shapely.affinity import translate
from sklearn.cluster import KMeans


def _utm_for(geom) -> str:
    """Get the UTM zone for a geometry."""
    lon = geom.centroid.x
    return f'EPSG:{32600 + int((lon + 180) // 6) + 1}'


def _calculate_shifts_by_cluster(
    official_u: gpd.GeoDataFrame,
    truth_u: gpd.GeoDataFrame,
    village
) -> Dict[int, Tuple[float, float]]:
    """Calculate median shift for each cluster.
    
    Args:
        official_u: Official plots in UTM coordinates
        truth_u: Example truths in UTM coordinates
        village: Village object
    
    Returns:
        Dictionary mapping cluster_id to (dx, dy) shift
    """
    # Get centroids of all plots for clustering
    centroids = np.array([[g.centroid.x, g.centroid.y] for g in official_u.geometry])
    
    # Cluster plots into groups (use 4 clusters as a simple split)
    n_clusters = min(4, len(centroids) // 10)  # At least 10 plots per cluster
    if n_clusters < 2:
        n_clusters = 2
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(centroids)
    
    # Calculate shift for each cluster using example truths
    cluster_shifts = {}
    cluster_counts = {}
    
    for pn in village.example_truths.index:
        if pn in official_u.index:
            o = official_u.loc[pn, 'geometry'].centroid
            t = truth_u.loc[pn, 'geometry'].centroid
            
            # Find which cluster this plot belongs to
            plot_idx = official_u.index.get_loc(pn)
            cluster_id = cluster_labels[plot_idx]
            
            dx = t.x - o.x
            dy = t.y - o.y
            
            if cluster_id not in cluster_shifts:
                cluster_shifts[cluster_id] = {'dxs': [], 'dys': []}
            cluster_shifts[cluster_id]['dxs'].append(dx)
            cluster_shifts[cluster_id]['dys'].append(dy)
    
    # Compute median shift for each cluster
    median_shifts = {}
    for cluster_id, shifts in cluster_shifts.items():
        mdx = statistics.median(shifts['dxs'])
        mdy = statistics.median(shifts['dys'])
        median_shifts[cluster_id] = (mdx, mdy)
        cluster_counts[cluster_id] = len(shifts['dxs'])
    
    # Calculate global median as fallback
    all_dxs = []
    all_dys = []
    for shifts in cluster_shifts.values():
        all_dxs.extend(shifts['dxs'])
        all_dys.extend(shifts['dys'])
    global_shift = (statistics.median(all_dxs), statistics.median(all_dys))
    
    return median_shifts, global_shift, cluster_labels, cluster_counts


def local_cluster_shift(village, confidence_base: float = 0.6) -> gpd.GeoDataFrame:
    """Estimate shifts per spatial cluster and apply them.
    
    This improves on global_median_shift by recognizing that the error
    varies across the village. We cluster plots spatially and apply
    different shifts to different clusters.
    
    Args:
        village: Village object with plots and example_truths
        confidence_base: Base confidence for plots with local data
    
    Returns:
        GeoDataFrame with corrected predictions and confidence scores
    """
    if village.example_truths is None:
        raise ValueError(f'{village.slug} has no example_truths.geojson to estimate shifts from')
    
    # Convert to UTM for accurate distance calculations
    utm = _utm_for(village.example_truths.geometry.iloc[0])
    official_u = village.plots.to_crs(utm)
    truth_u = village.example_truths.to_crs(utm)
    
    # Calculate shifts by cluster
    cluster_shifts, global_shift, cluster_labels, cluster_counts = _calculate_shifts_by_cluster(
        official_u, truth_u, village
    )
    
    # Apply shifts to all plots
    shifted = official_u.copy()
    confidences = []
    method_notes = []
    
    for idx, (pn, row) in enumerate(shifted.iterrows()):
        cluster_id = cluster_labels[idx]
        
        # Use cluster-specific shift if available, otherwise global
        if cluster_id in cluster_shifts:
            dx, dy = cluster_shifts[cluster_id]
            n_samples = cluster_counts[cluster_id]
            conf = confidence_base + (0.1 * min(n_samples / 5, 1.0))  # Higher confidence with more samples
            note = f'cluster {cluster_id} shift dx={dx:.1f}m dy={dy:.1f}m (n={n_samples})'
        else:
            dx, dy = global_shift
            conf = confidence_base - 0.1  # Lower confidence for fallback
            note = f'global fallback shift dx={dx:.1f}m dy={dy:.1f}m'
        
        # Apply translation
        shifted.at[pn, 'geometry'] = translate(row.geometry, dx, dy)
        confidences.append(min(max(conf, 0.0), 1.0))  # Clamp to [0, 1]
        method_notes.append(note)
    
    # Convert back to lon/lat
    # Convert back to lon/lat
    preds = shifted.to_crs('EPSG:4326')

    preds['confidence'] = confidences
    preds['method_note'] = method_notes

    # Flag low-confidence plots
    preds['status'] = preds['confidence'].apply(
       lambda c: 'corrected' if c >= 0.65 else 'flagged'
   )

    return preds[['plot_number', 'status', 'confidence', 'method_note', 'geometry']]