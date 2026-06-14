#!/usr/bin/env python3

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import geopandas as gpd
from pathlib import Path

from bhume import load, patch_for_plot
from bhume.geo import open_imagery, geom_to_imagery_crs
from bhume.baseline import _utm_for


def main(village_dir):

    print("=" * 70)
    print("DATA EXPLORATION")
    print("=" * 70)

    village = load(village_dir)

    print("\nLoaded village:", village.slug)
    print("Data directory:", village.dir)

    print("\nNumber of plots:", len(village.plots))

    n_truth = 0

    if village.example_truths is not None:

        n_truth = len(village.example_truths)

    print("Number of example truths:", n_truth)

    if n_truth == 0:

        print("No example truths found")

        return

    print("\nExample truth plot numbers:")

    print(list(village.example_truths.index))

    print("\n" + "=" * 70)

    print("ANALYZING ALL EXAMPLE TRUTHS")

    print("=" * 70)

    for plot_num in village.example_truths.index:

        print("\n" + "-" * 50)

        print(f"Plot {plot_num}")

        print("-" * 50)

        official_geom = village.plot(plot_num)

        truth_geom = village.example_truths.loc[
            plot_num,
            "geometry"
        ]

        print("Official geometry:", official_geom.geom_type)

        print("Truth geometry:", truth_geom.geom_type)

        # Convert to UTM

        utm = _utm_for(official_geom)

        official_gdf = gpd.GeoDataFrame(

            geometry=[official_geom],

            crs="EPSG:4326"

        )

        truth_gdf = gpd.GeoDataFrame(

            geometry=[truth_geom],

            crs="EPSG:4326"

        )

        official_u = official_gdf.to_crs(utm)

        truth_u = truth_gdf.to_crs(utm)

        oc = official_u.geometry.iloc[0].centroid

        tc = truth_u.geometry.iloc[0].centroid

        dx = tc.x - oc.x

        dy = tc.y - oc.y

        dist = oc.distance(tc)


        print(
            plot_num,
            f"{oc.x:.2f}",
            f"{oc.y:.2f}",
            f"{dx:.2f}",
            f"{dy:.2f}"
       )

        print(f"dx = {dx:.2f} m")

        print(f"dy = {dy:.2f} m")

        print(f"distance = {dist:.2f} m")

        # Create visualization

        with open_imagery(village.imagery_path) as src:

            patch = patch_for_plot(

                src,

                official_geom,

                pad_m=50

            )

            fig, ax = plt.subplots(

                figsize=(8, 8)

            )

            ax.imshow(patch.image)

            ax.set_title(

                f"Plot {plot_num}\n"

                f"dx={dx:.1f}m  "

                f"dy={dy:.1f}m  "

                f"dist={dist:.1f}m"

            )

            ax.axis("off")

            transform_inv = ~patch.transform

            def to_pixels(geom_4326):

                geom_img = geom_to_imagery_crs(

                    src,

                    geom_4326

                )

                polys = []

                if geom_img.geom_type == "Polygon":

                    geoms = [geom_img]

                elif geom_img.geom_type == "MultiPolygon":

                    geoms = list(

                        geom_img.geoms

                    )

                else:

                    return []

                for poly in geoms:

                    coords = []

                    for x, y in poly.exterior.coords:

                        col, row = (

                            transform_inv * (x, y)

                        )

                        coords.append(

                            [col, row]

                        )

                    polys.append(

                        np.array(coords)

                    )

                return polys

            off_pixels = to_pixels(

                official_geom

            )

            truth_pixels = to_pixels(

                truth_geom

            )

            first = True

            for poly in off_pixels:

                polygon = patches.Polygon(

                    poly,

                    linewidth=3,

                    edgecolor="red",

                    facecolor="none",

                    label="Official"

                    if first

                    else None

                )

                ax.add_patch(

                    polygon

                )

                first = False

            first = True

            for poly in truth_pixels:

                polygon = patches.Polygon(

                    poly,

                    linewidth=3,

                    edgecolor="lime",

                    facecolor="none",

                    linestyle="--",

                    label="Truth"

                    if first

                    else None

                )

                ax.add_patch(

                    polygon

                )

                first = False

            ax.legend()

            output = (

                Path(village_dir)

                /

                f"plot_{plot_num}_comparison.png"

            )

            plt.savefig(

                output,

                dpi=150,

                bbox_inches="tight"

            )

            plt.close()

            print(

                "Saved:",

                output

            )

    print("\n" + "=" * 70)

    print("DONE")

    print("=" * 70)


if __name__ == "__main__":

    import sys

    village_dir = (

        sys.argv[1]

        if len(sys.argv) > 1

        else "data/34855_vadnerbhairav_chandavad_nashik"

    )

    main(village_dir)