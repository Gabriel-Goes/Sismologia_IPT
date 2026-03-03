#!/usr/bin/env python3
"""
Materialize final compatible events dataset from step02/step03 stage output.

Final layout target:
  data/events/YYYYJJJTHHMMSS/
    event.json
    event.xml
    waveform/*.mseed

Compatibility policy (strict):
- match_status == matched
- event origin inside MG polygon (deterministic point-in-polygon)
- magnitude < max-mag
- depth_km < max-depth-km
- has at least one P* pick with dist_km <= max-pick-dist-km
- has at least one successful waveform download (downloaded or skipped_exists)
- event.xml exists
- datetime tag resolvable
- optional year >= min-year (applied last)

Collision policy:
- abort (default): if any two compatible events map to the same target folder,
  or if target folder already exists in output root, no moves/copies are applied.
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
from dataclasses import dataclass
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


@dataclass
class EventEval:
    source_folder: str
    source_dir: str
    target_folder: str
    target_path: str
    eligible: bool
    reasons: list[str]
    action: str
    match_status: str
    state: str
    year: int | None
    inside_mg_polygon: bool
    mg_filter_status: str
    st_geo_consistency: str
    magnitude: float | None
    depth_km: float | None
    p_picks_lte_maxdist: int
    picks_total: int
    waveforms_ok_count: int
    waveforms_error_count: int
    waveforms_total_count: int
    waveform_files_count: int
    xml_exists: bool
    datetime_source: str


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


def _is_p_phase(phase_hint: Any) -> bool:
    return str(phase_hint or "").upper().startswith("P")


def _parse_utc_datetime(raw: Any) -> datetime | None:
    if raw is None:
        return None
    try:
        if isinstance(raw, datetime):
            dt = raw
        else:
            dt = datetime.fromisoformat(str(raw).strip().replace("Z", "+00:00"))
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


def _resolve_datetime_tag(
    payload: dict[str, Any],
    *,
    datetime_source: str,
    datetime_format: str,
) -> tuple[str | None, str]:
    sis = payload.get("sisbra") or {}
    fdsn = payload.get("fdsn") or {}

    orders: list[tuple[str, Any]]
    if datetime_source == "fdsn_then_sisbra":
        orders = [
            ("fdsn.origin_time", fdsn.get("origin_time")),
            ("sisbra.origin_time", sis.get("origin_time")),
        ]
    elif datetime_source == "sisbra_then_fdsn":
        orders = [
            ("sisbra.origin_time", sis.get("origin_time")),
            ("fdsn.origin_time", fdsn.get("origin_time")),
        ]
    else:
        raise ValueError(f"Unsupported datetime_source: {datetime_source}")

    for source_name, raw in orders:
        dt = _parse_utc_datetime(raw)
        if dt is not None:
            return dt.strftime(datetime_format), source_name

    return None, ""


def _load_download_stats(summary_csv: str) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"downloaded": 0, "skipped_exists": 0, "error": 0, "total": 0}
    )

    if not os.path.exists(summary_csv):
        return stats

    with open(summary_csv, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            folder = str(row.get("event_folder") or "").strip()
            if not folder:
                continue
            status = str(row.get("status") or "").strip()

            stats[folder]["total"] += 1
            if status == "downloaded":
                stats[folder]["downloaded"] += 1
            elif status == "skipped_exists":
                stats[folder]["skipped_exists"] += 1
            elif status.startswith("error"):
                stats[folder]["error"] += 1

    return stats


def _scan_event(
    *,
    event_json_path: str,
    output_root: str,
    dl_stats: dict[str, dict[str, int]],
    state_filter: str,
    min_year: int | None,
    mg_polygon_year: int,
    mg_polygon_gpkg: str,
    mg_polygon_layer: str,
    max_mag: float,
    max_depth_km: float,
    max_pick_dist_km: float,
    datetime_source: str,
    datetime_format: str,
    waveforms_subdir: str,
) -> EventEval:
    event_dir = os.path.dirname(event_json_path)
    source_folder = os.path.basename(event_dir)
    payload = json.load(open(event_json_path, "r", encoding="utf-8"))

    reasons: list[str] = []
    match_status = str(payload.get("match_status") or "")

    sis = payload.get("sisbra") or {}
    state = str(sis.get("state") or "").strip().upper()
    year = _sis_event_year(sis)
    magnitude = _safe_float(sis.get("magnitude"))
    depth_km = _safe_float(sis.get("depth_km"))
    geo = evaluate_mg_filter(
        latitude=sis.get("latitude"),
        longitude=sis.get("longitude"),
        state_value=state,
        state_target=str(state_filter or "MG"),
        mg_polygon_year=int(mg_polygon_year),
        mg_polygon_gpkg_path=str(mg_polygon_gpkg or ""),
        mg_polygon_layer=str(mg_polygon_layer or ""),
    )
    inside_mg_polygon = bool(geo["inside_mg_polygon"])
    mg_filter_status = str(geo["mg_filter_status"])
    st_geo_consistency = str(geo["st_geo_consistency"])

    picks = payload.get("picks") or []
    p_picks_lte = 0
    for pk in picks:
        if not _is_p_phase(pk.get("phase_hint")):
            continue
        dist = _safe_float(pk.get("dist_km"))
        if dist is not None and dist <= float(max_pick_dist_km):
            p_picks_lte += 1

    dls = dl_stats.get(source_folder, {"downloaded": 0, "skipped_exists": 0, "error": 0, "total": 0})
    waveforms_ok_count = int(dls.get("downloaded", 0)) + int(dls.get("skipped_exists", 0))
    waveforms_error_count = int(dls.get("error", 0))
    waveforms_total_count = int(dls.get("total", 0))

    waveform_files = glob.glob(os.path.join(event_dir, waveforms_subdir, "*.mseed"))
    waveform_files_count = len(waveform_files)

    xml_path = os.path.join(event_dir, "event.xml")
    xml_exists = os.path.exists(xml_path)

    target_folder, dt_source = _resolve_datetime_tag(
        payload,
        datetime_source=datetime_source,
        datetime_format=datetime_format,
    )

    if match_status != "matched":
        reasons.append("not_matched")
    if mg_filter_status != KEEP_IN_MG:
        if mg_filter_status == DROP_OUTSIDE_MG:
            reasons.append("outside_mg_polygon")
        elif mg_filter_status == DROP_NO_VALID_COORDS:
            reasons.append("no_valid_coords")
        else:
            reasons.append("outside_mg_polygon")
    if magnitude is None or not (magnitude < float(max_mag)):
        reasons.append("mag_not_lt_max")
    if depth_km is None or not (depth_km < float(max_depth_km)):
        reasons.append("depth_not_lt_max")
    if p_picks_lte <= 0:
        reasons.append("no_p_pick_lte_maxdist")
    if waveforms_ok_count <= 0:
        reasons.append("no_downloaded_waveform")
    if waveform_files_count <= 0:
        reasons.append("no_waveform_file")
    if not xml_exists:
        reasons.append("missing_event_xml")
    if not target_folder:
        reasons.append("invalid_event_datetime")
    if min_year is not None:
        if year is None or year < int(min_year):
            reasons.append("year_lt_min_or_missing")

    eligible = len(reasons) == 0
    target_path = os.path.join(output_root, target_folder) if target_folder else ""

    return EventEval(
        source_folder=source_folder,
        source_dir=event_dir,
        target_folder=target_folder or "",
        target_path=target_path,
        eligible=eligible,
        reasons=reasons,
        action="pending" if eligible else "skipped",
        match_status=match_status,
        state=state,
        year=year,
        inside_mg_polygon=inside_mg_polygon,
        mg_filter_status=mg_filter_status,
        st_geo_consistency=st_geo_consistency,
        magnitude=magnitude,
        depth_km=depth_km,
        p_picks_lte_maxdist=p_picks_lte,
        picks_total=len(picks),
        waveforms_ok_count=waveforms_ok_count,
        waveforms_error_count=waveforms_error_count,
        waveforms_total_count=waveforms_total_count,
        waveform_files_count=waveform_files_count,
        xml_exists=xml_exists,
        datetime_source=dt_source,
    )


def _append_reason(ev: EventEval, reason: str) -> None:
    if reason not in ev.reasons:
        ev.reasons.append(reason)


def _write_reports(
    *,
    report_csv: str,
    report_md: str,
    events: list[EventEval],
    config: dict[str, Any],
) -> None:
    os.makedirs(os.path.dirname(report_csv) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(report_md) or ".", exist_ok=True)

    rows = []
    reasons_counter = Counter()
    actions_counter = Counter()
    for ev in events:
        for r in ev.reasons:
            reasons_counter[r] += 1
        actions_counter[ev.action] += 1

        rows.append(
            {
                "source_folder": ev.source_folder,
                "target_folder": ev.target_folder,
                "eligible": "1" if ev.eligible else "0",
                "action": ev.action,
                "reasons": ";".join(ev.reasons),
                "match_status": ev.match_status,
                "state": ev.state,
                "year": "" if ev.year is None else f"{ev.year}",
                "inside_mg_polygon": "1" if ev.inside_mg_polygon else "0",
                "mg_filter_status": ev.mg_filter_status,
                "st_geo_consistency": ev.st_geo_consistency,
                "magnitude": "" if ev.magnitude is None else f"{ev.magnitude}",
                "depth_km": "" if ev.depth_km is None else f"{ev.depth_km}",
                "picks_total": ev.picks_total,
                "p_picks_lte_maxdist": ev.p_picks_lte_maxdist,
                "waveforms_ok_count": ev.waveforms_ok_count,
                "waveforms_error_count": ev.waveforms_error_count,
                "waveforms_total_count": ev.waveforms_total_count,
                "waveform_files_count": ev.waveform_files_count,
                "xml_exists": "1" if ev.xml_exists else "0",
                "datetime_source": ev.datetime_source,
            }
        )

    rows.sort(key=lambda x: (x["eligible"], x["target_folder"], x["source_folder"]))

    with open(report_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "source_folder",
                "target_folder",
                "eligible",
                "action",
                "reasons",
                "match_status",
                "state",
                "year",
                "inside_mg_polygon",
                "mg_filter_status",
                "st_geo_consistency",
                "magnitude",
                "depth_km",
                "picks_total",
                "p_picks_lte_maxdist",
                "waveforms_ok_count",
                "waveforms_error_count",
                "waveforms_total_count",
                "waveform_files_count",
                "xml_exists",
                "datetime_source",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    with open(report_md, "w", encoding="utf-8") as f:
        f.write("# Event Materialization Report\n\n")
        f.write("## Config\n")
        for k in sorted(config):
            f.write(f"- {k}: `{config[k]}`\n")
        f.write("\n")
        f.write("## Totals\n")
        f.write(f"- scanned: `{len(events)}`\n")
        f.write(f"- eligible: `{sum(1 for ev in events if ev.eligible)}`\n")
        f.write(f"- moved: `{actions_counter.get('moved', 0)}`\n")
        f.write(f"- copied: `{actions_counter.get('copied', 0)}`\n")
        f.write(f"- skipped: `{actions_counter.get('skipped', 0)}`\n")
        f.write(f"- aborted_collision: `{actions_counter.get('aborted_collision', 0)}`\n")
        f.write("\n")
        f.write("## Reasons\n")
        if reasons_counter:
            for reason, count in reasons_counter.most_common():
                f.write(f"- {reason}: `{count}`\n")
        else:
            f.write("- none\n")
        f.write("\n")
        f.write(f"- report_csv: `{report_csv}`\n")


def _output_root_has_content(path: str) -> bool:
    if not os.path.isdir(path):
        return False
    return any(True for _ in os.scandir(path))


def main() -> int:
    ap = argparse.ArgumentParser(description="Materialize compatible events into final data/events layout.")
    ap.add_argument("--events-root", default="data/events_stage", help="Step02/03 root containing */event.json.")
    ap.add_argument(
        "--download-summary-csv",
        default="outputs/waveform_triplet_download_summary_events.csv",
        help="Step03 summary CSV.",
    )
    ap.add_argument("--output-root", default="data/events", help="Final output root.")
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
    ap.add_argument("--min-year", type=int, default=None, help="Optional minimum year filter (applied last).")
    ap.add_argument("--max-mag", type=float, default=4.0, help="Strict upper bound (mag < max-mag).")
    ap.add_argument(
        "--max-depth-km",
        type=float,
        default=10.0,
        help="Strict upper bound (depth_km < max-depth-km).",
    )
    ap.add_argument("--max-pick-dist-km", type=float, default=400.0)
    ap.add_argument(
        "--datetime-source",
        default="fdsn_then_sisbra",
        choices=["fdsn_then_sisbra", "sisbra_then_fdsn"],
    )
    ap.add_argument("--datetime-format", default="%Y%jT%H%M%S")
    ap.add_argument("--waveforms-subdir", default="waveform")
    ap.add_argument(
        "--collision-policy",
        default="abort",
        choices=["abort"],
        help="Collision behavior for target folder tags.",
    )
    ap.add_argument("--report-csv", default="outputs/events_materialize_report.csv")
    ap.add_argument("--report-md", default="outputs/events_materialize_report.md")
    ap.add_argument("--copy", action="store_true", help="Copy instead of move.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--allow-nonempty-output-root",
        action="store_true",
        help="Allow output root with existing content (default: disabled).",
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

    if not os.path.isdir(args.events_root):
        raise SystemExit(f"events_root not found: {args.events_root}")

    os.makedirs(args.output_root, exist_ok=True)
    if (not args.allow_nonempty_output_root) and _output_root_has_content(args.output_root):
        raise SystemExit(
            f"output_root is not empty: {args.output_root}. "
            "Clean it manually or pass --allow-nonempty-output-root."
        )

    dl_stats = _load_download_stats(args.download_summary_csv)

    event_json_paths = sorted(glob.glob(os.path.join(args.events_root, "*", "event.json")))
    events: list[EventEval] = []
    for path in event_json_paths:
        events.append(
            _scan_event(
                event_json_path=path,
                output_root=args.output_root,
                dl_stats=dl_stats,
                state_filter=args.state_filter,
                min_year=args.min_year,
                mg_polygon_year=int(args.mg_polygon_year),
                mg_polygon_gpkg=str(args.mg_polygon_gpkg or ""),
                mg_polygon_layer=str(args.mg_polygon_layer or ""),
                max_mag=float(args.max_mag),
                max_depth_km=float(args.max_depth_km),
                max_pick_dist_km=float(args.max_pick_dist_km),
                datetime_source=args.datetime_source,
                datetime_format=args.datetime_format,
                waveforms_subdir=args.waveforms_subdir,
            )
        )

    # Detect collisions only among currently eligible events.
    by_tag: dict[str, list[int]] = defaultdict(list)
    for i, ev in enumerate(events):
        if ev.eligible and ev.target_folder:
            by_tag[ev.target_folder].append(i)

    collision_idxs: set[int] = set()
    for tag, idxs in by_tag.items():
        if len(idxs) > 1:
            for idx in idxs:
                collision_idxs.add(idx)

    for i, ev in enumerate(events):
        if not ev.eligible:
            continue
        if os.path.exists(ev.target_path):
            collision_idxs.add(i)

    if collision_idxs:
        for idx in sorted(collision_idxs):
            ev = events[idx]
            _append_reason(ev, "datetime_collision")
            ev.eligible = False
            ev.action = "aborted_collision"

        config = {
            "events_root": args.events_root,
            "download_summary_csv": args.download_summary_csv,
            "output_root": args.output_root,
            "state_filter": args.state_filter,
            "mg_polygon_year": args.mg_polygon_year,
            "mg_polygon_gpkg": args.mg_polygon_gpkg,
            "mg_polygon_layer": args.mg_polygon_layer,
            "min_year": args.min_year,
            "max_mag": args.max_mag,
            "max_depth_km": args.max_depth_km,
            "max_pick_dist_km": args.max_pick_dist_km,
            "datetime_source": args.datetime_source,
            "datetime_format": args.datetime_format,
            "waveforms_subdir": args.waveforms_subdir,
            "collision_policy": args.collision_policy,
            "copy_mode": args.copy,
            "dry_run": args.dry_run,
            "allow_nonempty_output_root": args.allow_nonempty_output_root,
            "collision_count": len(collision_idxs),
        }
        _write_reports(report_csv=args.report_csv, report_md=args.report_md, events=events, config=config)

        print(f"event_json_found={len(event_json_paths)}")
        print(f"eligible_after_collision=0")
        print(f"collision_count={len(collision_idxs)}")
        print(f"report_csv={args.report_csv}")
        print(f"report_md={args.report_md}")
        raise SystemExit(2)

    moved = 0
    copied = 0
    skipped = 0

    for ev in events:
        if not ev.eligible:
            ev.action = "skipped"
            skipped += 1
            continue

        if args.dry_run:
            ev.action = "dry_run"
            continue

        if args.copy:
            shutil.copytree(ev.source_dir, ev.target_path)
            ev.action = "copied"
            copied += 1
        else:
            shutil.move(ev.source_dir, ev.target_path)
            ev.action = "moved"
            moved += 1

    config = {
        "events_root": args.events_root,
        "download_summary_csv": args.download_summary_csv,
        "output_root": args.output_root,
        "state_filter": args.state_filter,
        "mg_polygon_year": args.mg_polygon_year,
        "mg_polygon_gpkg": args.mg_polygon_gpkg,
        "mg_polygon_layer": args.mg_polygon_layer,
        "min_year": args.min_year,
        "max_mag": args.max_mag,
        "max_depth_km": args.max_depth_km,
        "max_pick_dist_km": args.max_pick_dist_km,
        "datetime_source": args.datetime_source,
        "datetime_format": args.datetime_format,
        "waveforms_subdir": args.waveforms_subdir,
        "collision_policy": args.collision_policy,
        "copy_mode": args.copy,
        "dry_run": args.dry_run,
        "allow_nonempty_output_root": args.allow_nonempty_output_root,
    }
    _write_reports(report_csv=args.report_csv, report_md=args.report_md, events=events, config=config)

    print(f"event_json_found={len(event_json_paths)}")
    print(f"eligible={sum(1 for ev in events if ev.eligible)}")
    print(f"moved={moved}")
    print(f"copied={copied}")
    print(f"skipped={skipped}")
    print(f"report_csv={args.report_csv}")
    print(f"report_md={args.report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
