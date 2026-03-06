#!/usr/bin/env python3
"""
Normalize the SISBRA RAW catalog into a reproducible CSV owned by this project.

Policy:
- RAW is the canonical input source.
- Coordinates are parsed and validated by this pipeline.
- Rows without valid coordinates are excluded from the operational flow and
  written to a dedicated audit CSV.
- No attempt is made to recover coordinates from toponymy/localities.
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
        text = str(value).strip()
        if not text:
            return None
        return float(text)
    except Exception:
        return None


def _normalize_state(value: Any) -> str:
    return str(value or "").strip().upper()


def _coord_parse_status(lat: float | None, lon: float | None) -> str:
    if lat is None and lon is None:
        return "MISSING_BOTH"
    if lat is None:
        return "MISSING_LAT"
    if lon is None:
        return "MISSING_LON"
    if not (-90.0 <= float(lat) <= 90.0):
        return "INVALID_LAT_RANGE"
    if not (-180.0 <= float(lon) <= 180.0):
        return "INVALID_LON_RANGE"
    return "VALID"


def _format_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{float(value):.8f}".rstrip("0").rstrip(".")


def _write_csv(path: str, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="Normalize SISBRA RAW and emit audit artifacts.")
    ap.add_argument(
        "--input-csv",
        default="catalogs/sisbra/sisbra_v2024May09/catalogo_RAW_v2024May09.csv",
        help="Input SISBRA RAW CSV path.",
    )
    ap.add_argument(
        "--output-csv",
        default="outputs/catalogs/sisbra_v2024May09/sisbra_raw_normalized_v2024May09.csv",
        help="Normalized CSV path (all rows preserved, including invalid coordinates).",
    )
    ap.add_argument(
        "--rejected-no-valid-coords-csv",
        default="outputs/catalogs/sisbra_v2024May09/sisbra_raw_rejected_no_valid_coords_v2024May09.csv",
        help="Audit CSV with rows that do not have valid coordinates.",
    )
    ap.add_argument(
        "--report-md",
        default="outputs/catalogs/sisbra_v2024May09/sisbra_raw_normalization_report_v2024May09.md",
        help="Markdown report path.",
    )
    args = ap.parse_args()

    with open(args.input_csv, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise SystemExit(f"Input has no header: {args.input_csv}")
        original_fields = list(reader.fieldnames)

        extra_fields = [
            "rownum_source",
            "latit_num",
            "longit_num",
            "has_valid_latlon",
            "coord_parse_status",
            "ST_norm",
        ]
        fieldnames = original_fields + [x for x in extra_fields if x not in original_fields]

        normalized_rows: list[dict[str, Any]] = []
        rejected_rows: list[dict[str, Any]] = []
        rows_in = 0
        rows_valid = 0
        rows_invalid = 0

        for rownum_source, row in enumerate(reader, start=2):
            rows_in += 1
            lat = _safe_float(row.get("latit"))
            lon = _safe_float(row.get("longit"))
            coord_status = _coord_parse_status(lat, lon)
            has_valid = coord_status == "VALID"

            normalized = dict(row)
            normalized["rownum_source"] = str(rownum_source)
            normalized["latit_num"] = _format_float(lat)
            normalized["longit_num"] = _format_float(lon)
            normalized["has_valid_latlon"] = "1" if has_valid else "0"
            normalized["coord_parse_status"] = coord_status
            normalized["ST_norm"] = _normalize_state(row.get("ST"))

            normalized_rows.append(normalized)
            if has_valid:
                rows_valid += 1
            else:
                rows_invalid += 1
                rejected_rows.append(normalized)

    _write_csv(args.output_csv, fieldnames, normalized_rows)
    _write_csv(args.rejected_no_valid_coords_csv, fieldnames, rejected_rows)

    os.makedirs(os.path.dirname(args.report_md) or ".", exist_ok=True)
    with open(args.report_md, "w", encoding="utf-8") as handle:
        handle.write("# SISBRA RAW Normalization Report\n\n")
        handle.write(f"- input_csv: `{args.input_csv}`\n")
        handle.write(f"- output_csv: `{args.output_csv}`\n")
        handle.write(f"- rejected_no_valid_coords_csv: `{args.rejected_no_valid_coords_csv}`\n")
        handle.write(f"- rows_raw_total: `{rows_in}`\n")
        handle.write(f"- rows_valid_coords: `{rows_valid}`\n")
        handle.write(f"- rows_invalid_coords: `{rows_invalid}`\n")

    print(f"input_csv={args.input_csv}")
    print(f"output_csv={args.output_csv}")
    print(f"rejected_no_valid_coords_csv={args.rejected_no_valid_coords_csv}")
    print(f"report_md={args.report_md}")
    print(f"rows_raw_total={rows_in}")
    print(f"rows_valid_coords={rows_valid}")
    print(f"rows_invalid_coords={rows_invalid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
