#!/usr/bin/env python3
"""
Filter SISBRA CSV rows for compatible-event candidate criteria.

Default policy for this project:
- state == MG
- year >= 2020
- magnitude < 4
- depth_km < 10

This script preserves original columns and writes a filtered CSV.
"""

from __future__ import annotations

import argparse
import csv
import os
from typing import Any


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        s = str(value).strip()
        if not s:
            return None
        return float(s)
    except Exception:
        return None


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        s = str(value).strip()
        if not s:
            return None
        return int(s)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Filter SISBRA CSV by state/magnitude/depth/year criteria.")
    ap.add_argument(
        "--input-csv",
        default="catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv",
        help="Input SISBRA CSV path.",
    )
    ap.add_argument(
        "--output-csv",
        default="outputs/sisbra_mg_maglt4_depthlt10.csv",
        help="Output filtered CSV path.",
    )
    ap.add_argument("--state", default="MG", help="State code filter (exact, case-insensitive).")
    ap.add_argument(
        "--max-mag",
        type=float,
        default=4.0,
        help="Strict upper bound for magnitude (mag < max-mag).",
    )
    ap.add_argument(
        "--max-depth-km",
        type=float,
        default=10.0,
        help="Strict upper bound for depth in km (depth < max-depth-km).",
    )
    ap.add_argument("--min-year", type=int, default=2020, help="Minimum year to keep.")
    args = ap.parse_args()

    rows_in = 0
    rows_out = 0  # after all filters

    # Sequential/linear pipeline counters:
    # state -> year -> magnitude -> depth
    passed_state = 0
    passed_year = 0
    passed_mag = 0
    passed_depth = 0

    dropped_state = 0
    dropped_year = 0
    dropped_mag = 0
    dropped_depth = 0

    state_target = str(args.state).strip().upper()

    with open(args.input_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit(f"Input has no header: {args.input_csv}")
        fieldnames = list(reader.fieldnames)

        kept_rows: list[dict[str, Any]] = []
        for row in reader:
            rows_in += 1

            state = str(row.get("ST") or "").strip().upper()
            if state != state_target:
                dropped_state += 1
                continue
            passed_state += 1

            year = _safe_int(row.get("year"))
            if year is None or year < int(args.min_year):
                dropped_year += 1
                continue
            passed_year += 1

            mag = _safe_float(row.get("mag"))
            if mag is None or not (mag < float(args.max_mag)):
                dropped_mag += 1
                continue
            passed_mag += 1

            depth = _safe_float(row.get("depth"))
            if depth is None or not (depth < float(args.max_depth_km)):
                dropped_depth += 1
                continue
            passed_depth += 1

            kept_rows.append(row)
            rows_out += 1

    os.makedirs(os.path.dirname(args.output_csv) or ".", exist_ok=True)
    with open(args.output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_rows)

    print(f"input_csv={args.input_csv}")
    print(f"output_csv={args.output_csv}")
    print(f"rows_in={rows_in}")
    print(f"passed_state={passed_state}")
    print(f"passed_year={passed_year}")
    print(f"passed_mag={passed_mag}")
    print(f"passed_depth={passed_depth}")
    print(f"rows_out={rows_out}")
    print(f"dropped_state_not_{state_target}_or_missing={dropped_state}")
    print(f"dropped_year_lt_{args.min_year}_or_missing={dropped_year}")
    print(f"dropped_mag_ge_{args.max_mag}_or_missing={dropped_mag}")
    print(f"dropped_depth_ge_{args.max_depth_km}_or_missing={dropped_depth}")
    print(f"filters=state={state_target},mag<{args.max_mag},depth<{args.max_depth_km},year>={args.min_year}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
