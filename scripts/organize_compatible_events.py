#!/usr/bin/env python3
"""
Organize event folders into compatible/incompatible sets.

Compatible event (default policy):
- match_status == "matched"
- sisbra latitude/longitude inside MG polygon (deterministic)
- sisbra.magnitude < --max-mag
- sisbra.depth_km < --max-depth-km
- has at least one P pick (phase_hint starts with "P") with dist_km <= --max-pick-dist-km
- has at least one downloaded waveform in --download-summary-csv (status in downloaded/skipped_exists)
- optional min-year filter applied last

Output layout:
- compatible root: folders named only YYYYMMDDTHHMMSS
- incompatible root: original folder names preserved
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
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


def _safe_float(v: Any) -> float | None:
    try:
        return float(v)
    except Exception:
        return None


def _safe_int(v: Any) -> int | None:
    try:
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None
        return int(s)
    except Exception:
        return None


def _is_p_phase(phase_hint: Any) -> bool:
    return str(phase_hint or "").upper().startswith("P")


def _datetime_tag(origin_time: str) -> str | None:
    if not origin_time:
        return None
    try:
        dt = datetime.fromisoformat(origin_time.replace("Z", "+00:00"))
    except Exception:
        return None
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S")


def _parse_utc_datetime(raw: Any) -> datetime | None:
    if raw is None:
        return None
    try:
        s = str(raw).strip()
        if not s:
            return None
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _sis_event_year(sis: dict[str, Any]) -> int | None:
    year = _safe_int(sis.get("year"))
    if year is not None:
        return year
    dt = _parse_utc_datetime(sis.get("origin_time"))
    if dt is None:
        return None
    return int(dt.year)


def _load_download_stats(summary_csv: str) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = defaultdict(lambda: {"downloaded": 0, "skipped_exists": 0, "error": 0, "total": 0})
    if not os.path.exists(summary_csv):
        return stats
    with open(summary_csv, "r", encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            folder = str(r.get("event_folder") or "")
            status = str(r.get("status") or "")
            if not folder:
                continue
            stats[folder]["total"] += 1
            if status in stats[folder]:
                stats[folder][status] += 1
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Organize compatible/incompatible events after step02+step03.")
    ap.add_argument("--events-root", default="data/sisbra_mg_maglt4_depthlt10_w24")
    ap.add_argument("--download-summary-csv", default="outputs/waveform_picks_download_summary_mg.csv")
    ap.add_argument("--compatible-root", default="data/eventos_compativeis")
    ap.add_argument("--incompatible-root", default="data/eventos_nao_compativeis")
    ap.add_argument(
        "--state-filter",
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
    ap.add_argument("--max-mag", type=float, default=4.0)
    ap.add_argument("--max-depth-km", type=float, default=10.0)
    ap.add_argument("--max-pick-dist-km", type=float, default=400.0)
    ap.add_argument("--min-year", type=int, default=None, help="Optional minimum year filter (applied last).")
    ap.add_argument("--report-csv", default="outputs/eventos_compatibilidade_report.csv")
    ap.add_argument("--report-md", default="outputs/eventos_compatibilidade_report.md")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--copy", action="store_true", help="Copy instead of move.")
    args = ap.parse_args()
    try:
        ensure_mg_polygon_loaded(
            mg_polygon_year=int(args.mg_polygon_year),
            mg_polygon_gpkg_path=str(args.mg_polygon_gpkg or ""),
            mg_polygon_layer=str(args.mg_polygon_layer or ""),
        )
    except Exception as exc:
        raise SystemExit(f"MG polygon load failed: {exc}") from exc

    os.makedirs(args.compatible_root, exist_ok=True)
    os.makedirs(args.incompatible_root, exist_ok=True)
    os.makedirs(os.path.dirname(args.report_csv) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.report_md) or ".", exist_ok=True)

    dl_stats = _load_download_stats(args.download_summary_csv)

    report_rows: list[dict[str, Any]] = []
    reasons_counter = Counter()
    moved_compatible = 0
    moved_incompatible = 0
    collisions = 0
    st_geo_inconsistent = 0
    st_geo_unknown = 0

    event_json_paths = sorted(glob.glob(os.path.join(args.events_root, "*", "event.json")))
    for p in event_json_paths:
        event_dir = os.path.dirname(p)
        src_folder = os.path.basename(event_dir)
        payload = json.load(open(p, "r", encoding="utf-8"))

        sis = payload.get("sisbra") or {}
        match_status = str(payload.get("match_status") or "")
        state = str(sis.get("state") or "").strip().upper()
        year = _sis_event_year(sis)
        mag = _safe_float(sis.get("magnitude"))
        dep = _safe_float(sis.get("depth_km"))
        origin_time = str(sis.get("origin_time") or "")
        dt_tag = _datetime_tag(origin_time)
        geo = evaluate_mg_filter(
            latitude=sis.get("latitude"),
            longitude=sis.get("longitude"),
            state_value=state,
            state_target=str(args.state_filter or "MG"),
            mg_polygon_year=int(args.mg_polygon_year),
            mg_polygon_gpkg_path=str(args.mg_polygon_gpkg or ""),
            mg_polygon_layer=str(args.mg_polygon_layer or ""),
        )
        mg_filter_status = str(geo["mg_filter_status"])
        inside_mg_polygon = bool(geo["inside_mg_polygon"])
        st_geo_consistency = str(geo["st_geo_consistency"])
        if st_geo_consistency.startswith("INCONSISTENT_"):
            st_geo_inconsistent += 1
        elif st_geo_consistency == "UNKNOWN_ST":
            st_geo_unknown += 1

        picks = payload.get("picks") or []
        p_picks_lt400 = 0
        for pk in picks:
            if not _is_p_phase(pk.get("phase_hint")):
                continue
            dist = _safe_float(pk.get("dist_km"))
            if dist is not None and dist <= float(args.max_pick_dist_km):
                p_picks_lt400 += 1

        dls = dl_stats.get(src_folder, {"downloaded": 0, "skipped_exists": 0, "error": 0, "total": 0})
        have_waveform = (dls.get("downloaded", 0) + dls.get("skipped_exists", 0)) > 0

        reasons: list[str] = []
        if match_status != "matched":
            reasons.append("not_matched")
        if mg_filter_status != KEEP_IN_MG:
            if mg_filter_status == DROP_OUTSIDE_MG:
                reasons.append("outside_mg_polygon")
            elif mg_filter_status == DROP_NO_VALID_COORDS:
                reasons.append("no_valid_coords")
            else:
                reasons.append("outside_mg_polygon")
        if mag is None or not (mag < float(args.max_mag)):
            reasons.append("mag_not_lt_max")
        if dep is None or not (dep < float(args.max_depth_km)):
            reasons.append("depth_not_lt_max")
        if p_picks_lt400 <= 0:
            reasons.append("no_p_pick_lte_400km")
        if not have_waveform:
            reasons.append("no_downloaded_waveform")
        if not dt_tag:
            reasons.append("invalid_origin_time")
        if args.min_year is not None and (year is None or year < int(args.min_year)):
            reasons.append("year_lt_min_or_missing")

        compatible = len(reasons) == 0

        if compatible:
            dst = os.path.join(args.compatible_root, dt_tag)
            if os.path.exists(dst):
                compatible = False
                reasons.append("datetime_collision")
                collisions += 1
                dst = os.path.join(args.incompatible_root, src_folder)
            else:
                moved_compatible += 1
        if not compatible:
            dst = os.path.join(args.incompatible_root, src_folder)
            moved_incompatible += 1

        for r in reasons:
            reasons_counter[r] += 1

        if not args.dry_run:
            if args.copy:
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                shutil.copytree(event_dir, dst)
            else:
                if os.path.isdir(dst):
                    shutil.rmtree(dst)
                shutil.move(event_dir, dst)

        report_rows.append(
            {
                "source_folder": src_folder,
                "target_group": "compatible" if compatible else "incompatible",
                "target_folder": os.path.basename(dst),
                "match_status": match_status,
                "origin_time": origin_time,
                "state": state,
                "year": "" if year is None else f"{year}",
                "inside_mg_polygon": "1" if inside_mg_polygon else "0",
                "mg_filter_status": mg_filter_status,
                "st_geo_consistency": st_geo_consistency,
                "magnitude": "" if mag is None else f"{mag}",
                "depth_km": "" if dep is None else f"{dep}",
                "picks_total": len(picks),
                "p_picks_lte_400km": p_picks_lt400,
                "waveforms_downloaded_or_existing": dls.get("downloaded", 0) + dls.get("skipped_exists", 0),
                "waveforms_error": dls.get("error", 0),
                "reasons": ";".join(reasons),
            }
        )

    report_rows.sort(key=lambda r: (r["target_group"], r["target_folder"], r["source_folder"]))
    with open(args.report_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "source_folder",
                "target_group",
                "target_folder",
                "match_status",
                "origin_time",
                "state",
                "year",
                "inside_mg_polygon",
                "mg_filter_status",
                "st_geo_consistency",
                "magnitude",
                "depth_km",
                "picks_total",
                "p_picks_lte_400km",
                "waveforms_downloaded_or_existing",
                "waveforms_error",
                "reasons",
            ],
        )
        w.writeheader()
        w.writerows(report_rows)

    with open(args.report_md, "w", encoding="utf-8") as f:
        f.write("# Relatorio de Compatibilidade de Eventos\n\n")
        f.write("## Config\n")
        f.write(f"- events_root: `{args.events_root}`\n")
        f.write(f"- download_summary_csv: `{args.download_summary_csv}`\n")
        f.write(f"- compatible_root: `{args.compatible_root}`\n")
        f.write(f"- incompatible_root: `{args.incompatible_root}`\n")
        f.write(f"- state_filter (audit only): `{args.state_filter}`\n")
        f.write(f"- mg_polygon_year: `{args.mg_polygon_year}`\n")
        f.write(f"- mg_polygon_gpkg: `{args.mg_polygon_gpkg}`\n")
        f.write(f"- mg_polygon_layer: `{args.mg_polygon_layer}`\n")
        f.write(f"- min_year (last): `{args.min_year}`\n")
        f.write(f"- max_mag (strict): `< {args.max_mag}`\n")
        f.write(f"- max_depth_km (strict): `< {args.max_depth_km}`\n")
        f.write(f"- max_pick_dist_km: `<= {args.max_pick_dist_km}`\n")
        f.write(f"- mode: `{'copy' if args.copy else 'move'}`\n")
        f.write(f"- dry_run: `{args.dry_run}`\n\n")
        f.write("## Totais\n")
        f.write(f"- event_json_found: `{len(event_json_paths)}`\n")
        f.write(f"- compatible: `{moved_compatible}`\n")
        f.write(f"- incompatible: `{moved_incompatible}`\n")
        f.write(f"- datetime_collisions: `{collisions}`\n\n")
        f.write("## Auditoria ST x geometria\n")
        f.write(f"- st_geo_inconsistent: `{st_geo_inconsistent}`\n")
        f.write(f"- st_geo_unknown: `{st_geo_unknown}`\n\n")
        f.write("## Razoes de Incompatibilidade\n")
        for k, v in reasons_counter.most_common():
            f.write(f"- {k}: `{v}`\n")
        f.write("\n")
        f.write(f"- report_csv: `{args.report_csv}`\n")

    print(f"event_json_found={len(event_json_paths)}")
    print(f"compatible={moved_compatible}")
    print(f"incompatible={moved_incompatible}")
    print(f"datetime_collisions={collisions}")
    print(f"report_csv={args.report_csv}")
    print(f"report_md={args.report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
