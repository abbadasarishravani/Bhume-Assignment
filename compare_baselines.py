#!/usr/bin/env python3
"""
Compare the original baseline, improved baseline,
and average shift method.

Run:
python compare_baselines.py data/34855_vadnerbhairav_chandavad_nashik
"""

from __future__ import annotations

import sys
from pathlib import Path

from bhume import load, score, write_predictions
from bhume.baseline import global_median_shift
from bhume.improved_baseline import local_cluster_shift
from bhume.io import read_predictions


def main(village_dir: str) -> None:

    print("=" * 60)
    print("Comparing Baseline vs Improved vs Average Shift")
    print("=" * 60)

    # Load village
    village = load(village_dir)

    print(f"\nLoaded {village.slug}")
    print(f"  {len(village.plots)} plots")
    print(
        f"  {len(village.example_truths) if village.example_truths is not None else 0} example truths"
    )

    # --------------------------------------------------
    # 1. Original baseline
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("1. Running ORIGINAL BASELINE")
    print("-" * 60)

    baseline_preds = global_median_shift(village)

    baseline_out = write_predictions(
        Path(village_dir) / "predictions_baseline.geojson",
        baseline_preds
    )

    print(f"  Wrote {len(baseline_preds)} predictions")

    baseline_score = score(baseline_preds, village)

    print(baseline_score)

    # --------------------------------------------------
    # 2. Improved baseline
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("2. Running IMPROVED BASELINE")
    print("-" * 60)

    improved_preds = local_cluster_shift(
        village,
        confidence_base=0.6
    )

    improved_out = write_predictions(
        Path(village_dir) / "predictions_improved.geojson",
        improved_preds
    )

    print(f"  Wrote {len(improved_preds)} predictions")

    improved_score = score(improved_preds, village)

    print(improved_score)

    # --------------------------------------------------
    # 3. Average Shift
    # --------------------------------------------------

    print("\n" + "-" * 60)
    print("3. Scoring AVERAGE SHIFT")
    print("-" * 60)

    avg_preds = read_predictions(
        Path("data") / "predictions_average_shift.geojson"
    )

    avg_score = score(avg_preds, village)

    print(avg_score)

    # --------------------------------------------------
    # Summary
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)

    print("\nMedian IoU:")

    print(
        f"  Baseline:      {baseline_score.median_iou_pred:.3f}"
    )

    print(
        f"  Improved:      {improved_score.median_iou_pred:.3f}"
    )

    print(
        f"  AverageShift:  {avg_score.median_iou_pred:.3f}"
    )

    print("\nMedian Improvement:")

    print(
        f"  Baseline:      {baseline_score.median_improvement:.3f}"
    )

    print(
        f"  Improved:      {improved_score.median_improvement:.3f}"
    )

    print(
        f"  AverageShift:  {avg_score.median_improvement:.3f}"
    )

    print("\nAccurate Rate (IoU >= 0.5):")

    print(
        f"  Baseline:      {baseline_score.accurate_rate:.3f}"
    )

    print(
        f"  Improved:      {improved_score.accurate_rate:.3f}"
    )

    print(
        f"  AverageShift:  {avg_score.accurate_rate:.3f}"
    )

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":

    village_dir = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "data/34855_vadnerbhairav_chandavad_nashik"
    )

    main(village_dir)