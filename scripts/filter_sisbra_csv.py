#!/usr/bin/env python3
"""
Filter SISBRA CSV rows for compatible-event candidate criteria.

Default policy for this project:
- geographic gate by point-in-polygon inside MG (deterministic)
- magnitude < 4
- depth_km < 10
- year >= 2020 (applied last)

Field `ST` is kept for audit/comparison only (not as inclusion gate).
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Any

_THIS_DIR = Path(__file__).resolve().parent
_SRC_DIR = _THIS_DIR.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from seismic_event_discriminator.mg_geo_filter import (  # noqa: E402
    DROP_NO_VALID_COORDS,
    DROP_OUTSIDE_MG,
    KEEP_IN_MG,
    ensure_mg_polygon_loaded,
    evaluate_mg_filter,
)


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
    ap = argparse.ArgumentParser(
        description="Filter SISBRA CSV by MG point-in-polygon, magnitude/depth, and year (last)."
    )
    ap.add_argument(
        "--input-csv",
        default="outputs/catalogs/sisbra_v2024May09/sisbra_raw_normalized_v2024May09.csv",
        help="Input SISBRA CSV path (default: project-owned normalized RAW).",
    )
    ap.add_argument(
        "--output-csv",
        default="outputs/catalogs/sisbra_v2024May09/sisbra_raw_mg_maglt4_depthlt10_yearge2020_v2024May09.csv",
        help="Output filtered CSV path.",
    )
    ap.add_argument(
        "--state",
        default="MG",
        help="Deprecated inclusion parameter. Used only for ST-vs-geometry audit labels.",
    )
    ap.add_argument(
        "--mg-polygon-year",
        type=int,
        default=2020,
        help="geobr year used if GeoPackage is unavailable.",
    )
    ap.add_argument(
        "--mg-polygon-gpkg",
        default="~/geodatabase.gpkg",
        help="Local GeoPackage path for MG polygon (preferred in offline environments).",
    )
    ap.add_argument(
        "--mg-polygon-layer",
        default="ibge_mg_uf_2024",
        help="Layer name inside GeoPackage used for MG polygon.",
    )
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
    ap.add_argument(
        "--min-year",
        type=int,
        default=2020,
        help="Minimum year to keep (applied last).",
    )
    args = ap.parse_args()

    try:
        ensure_mg_polygon_loaded(
            mg_polygon_year=int(args.mg_polygon_year),
            mg_polygon_gpkg_path=str(args.mg_polygon_gpkg or ""),
            mg_polygon_layer=str(args.mg_polygon_layer or ""),
        )
    except Exception as exc:
        raise SystemExit(f"MG polygon load failed: {exc}") from exc

    rows_in = 0
    rows_out = 0

    passed_geo = 0
    passed_mag = 0
    passed_depth = 0
    passed_year = 0

    dropped_geo_outside = 0
    dropped_geo_no_coords = 0
    dropped_mag = 0
    dropped_depth = 0
    dropped_year = 0

    st_inconsistent = 0
    st_unknown = 0

    state_target = str(args.state).strip().upper()

    with open(args.input_csv, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise SystemExit(f"Input has no header: {args.input_csv}")
        fieldnames = list(reader.fieldnames)
        for extra_col in ("inside_mg_polygon", "mg_filter_status", "st_geo_consistency"):
            if extra_col not in fieldnames:
                fieldnames.append(extra_col)

        kept_rows: list[dict[str, Any]] = []
        for row in reader:
            rows_in += 1

            geo = evaluate_mg_filter(
                latitude=row.get("latit_num") or row.get("latit"),
                longitude=row.get("longit_num") or row.get("longit"),
                state_value=row.get("ST_norm") or row.get("ST"),
                state_target=state_target,
                mg_polygon_year=int(args.mg_polygon_year),
                mg_polygon_gpkg_path=str(args.mg_polygon_gpkg or ""),
                mg_polygon_layer=str(args.mg_polygon_layer or ""),
            )
            row["inside_mg_polygon"] = "1" if geo["inside_mg_polygon"] else "0"
            row["mg_filter_status"] = str(geo["mg_filter_status"])
            row["st_geo_consistency"] = str(geo["st_geo_consistency"])

            if str(geo["st_geo_consistency"]).startswith("INCONSISTENT_"):
                st_inconsistent += 1
            if str(geo["st_geo_consistency"]) == "UNKNOWN_ST":
                st_unknown += 1

            if geo["mg_filter_status"] != KEEP_IN_MG:
                if geo["mg_filter_status"] == DROP_OUTSIDE_MG:
                    dropped_geo_outside += 1
                elif geo["mg_filter_status"] == DROP_NO_VALID_COORDS:
                    dropped_geo_no_coords += 1
                else:
                    dropped_geo_outside += 1
                continue
            passed_geo += 1

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

            year = _safe_int(row.get("year"))
            if year is None or year < int(args.min_year):
                dropped_year += 1
                continue
            passed_year += 1

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
    print(f"passed_geo_inside_mg={passed_geo}")
    print(f"passed_mag={passed_mag}")
    print(f"passed_depth={passed_depth}")
    print(f"passed_year={passed_year}")
    print(f"rows_out={rows_out}")
    print(f"dropped_geo_outside_mg={dropped_geo_outside}")
    print(f"dropped_geo_no_valid_coords={dropped_geo_no_coords}")
    print(f"dropped_mag_ge_{args.max_mag}_or_missing={dropped_mag}")
    print(f"dropped_depth_ge_{args.max_depth_km}_or_missing={dropped_depth}")
    print(f"dropped_year_lt_{args.min_year}_or_missing={dropped_year}")
    print(f"st_geo_inconsistent_rows={st_inconsistent}")
    print(f"st_geo_unknown_rows={st_unknown}")
    print(
        "filters=inside_mg_polygon,mag<{0},depth<{1},year>={2}(last),state_audit={3},mg_polygon_year={4}".format(
            args.max_mag,
            args.max_depth_km,
            args.min_year,
            state_target,
            args.mg_polygon_year,
        )
    )
    print(f"mg_polygon_gpkg={args.mg_polygon_gpkg}")
    print(f"mg_polygon_layer={args.mg_polygon_layer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
