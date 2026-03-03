#!/usr/bin/env python3
"""
Step 03: download waveform windows around P picks from step02 event bundles.

Rules implemented:
- use deterministic geographic gate: event origin must be inside MG polygon
- use only picks with phase_hint starting with "P" (P, Pg, Pn, ...)
- use only picks with dist_km <= --max-pick-dist-km
- fetch 60 s windows: [pick_time - --pre-p-s, pick_time + --post-p-s]
- do not fetch any waveform for events without qualifying P picks
- optional min-year gate is applied last
- when --component-channels is provided, default output is one 3C mseed per
  station using event origin tag (NET_STA_DATETIME.mseed)
  (use --split-component-files for legacy split-per-channel mode)
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from obspy import UTCDateTime
from obspy import Stream
from obspy.clients.fdsn import Client

_THIS_DIR = Path(__file__).resolve().parent
_SRC_DIR = _THIS_DIR.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from seismic_event_discriminator.mg_geo_filter import (  # noqa: E402
    KEEP_IN_MG,
    ensure_mg_polygon_loaded,
    evaluate_mg_filter,
)


_THREAD_LOCAL = threading.local()
STEP03_FILENAME_PATTERN = "NET_STA_DATETIME.mseed"
STEP03_DATETIME_SOURCE = "event_origin_utc"
STEP03_DATETIME_FORMAT = "%Y%jT%H%M%S"


def _client_for(base_url: str) -> Client:
    current_url = getattr(_THREAD_LOCAL, "client_url", None)
    current_client = getattr(_THREAD_LOCAL, "client", None)
    if current_client is None or current_url != base_url:
        current_client = Client(base_url=base_url)
        _THREAD_LOCAL.client = current_client
        _THREAD_LOCAL.client_url = base_url
    return current_client


def _is_p_phase(phase_hint: Any) -> bool:
    return str(phase_hint or "").upper().startswith("P")


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


def _event_id(payload: dict[str, Any]) -> str:
    rid = ((payload.get("fdsn") or {}).get("resource_id") or "").strip()
    return rid.split("/")[-1] if rid else ""


def _parse_utc_datetime(raw: Any) -> datetime | None:
    if raw is None:
        return None
    try:
        if isinstance(raw, datetime):
            dt = raw
        else:
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


def _event_datetime_tag(payload: dict[str, Any], event_folder: str) -> str | None:
    sis = payload.get("sisbra") or {}
    fdsn = payload.get("fdsn") or {}
    for candidate in (fdsn.get("origin_time"), sis.get("origin_time")):
        dt = _parse_utc_datetime(candidate)
        if dt is not None:
            return dt.strftime(STEP03_DATETIME_FORMAT)

    folder_head = str(event_folder or "").split("_")[0]
    try:
        dt = datetime.strptime(folder_head, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        return dt.strftime(STEP03_DATETIME_FORMAT)
    except Exception:
        return None


@dataclass(frozen=True)
class PickTask:
    event_dir: str
    event_folder: str
    match_status: str
    fdsn_event_id: str
    network: str
    station: str
    location: str
    channel: str
    phase_hint: str
    pick_time: str
    dist_km: float | None
    source_seed_id: str


@dataclass(frozen=True)
class TripletTask:
    event_dir: str
    event_folder: str
    match_status: str
    fdsn_event_id: str
    network: str
    station: str
    location: str
    channels: tuple[str, ...]
    phase_hint: str
    pick_time: str
    event_datetime_tag: str
    dist_km: float | None
    source_seed_id: str


def _selected_picks(payload: dict[str, Any], max_pick_dist_km: float) -> list[dict[str, Any]]:
    by_seed: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    picks = payload.get("picks") or []

    # One waveform per seed_id: keep earliest qualifying P pick.
    for p in sorted(picks, key=lambda x: (x.get("time") or "", x.get("seed_id") or "")):
        if not _is_p_phase(p.get("phase_hint")):
            continue
        dist_km = _safe_float(p.get("dist_km"))
        if dist_km is None or dist_km > max_pick_dist_km:
            continue
        t = p.get("time")
        if not t:
            continue

        key = (
            str(p.get("network") or ""),
            str(p.get("station") or ""),
            str(p.get("location") or ""),
            str(p.get("channel") or ""),
        )
        prev = by_seed.get(key)
        if prev is None or str(t) < str(prev.get("time") or ""):
            by_seed[key] = p

    out = list(by_seed.values())
    out.sort(key=lambda x: (x.get("time") or "", x.get("seed_id") or ""))
    return out


def _station_level_tasks(
    *,
    selected_picks: list[dict[str, Any]],
    channels: list[str],
) -> list[dict[str, Any]]:
    """
    From selected P picks, keep one reference pick per station (earliest pick time),
    then expand to one task per requested channel.
    """
    by_sta: dict[tuple[str, str, str], dict[str, Any]] = {}
    for p in selected_picks:
        key = (
            str(p.get("network") or ""),
            str(p.get("station") or ""),
            str(p.get("location") or ""),
        )
        prev = by_sta.get(key)
        if prev is None or str(p.get("time") or "") < str(prev.get("time") or ""):
            by_sta[key] = p

    tasks: list[dict[str, Any]] = []
    for (_net, _sta, _loc), ref in sorted(by_sta.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        for ch in channels:
            tasks.append(
                {
                    "network": str(ref.get("network") or ""),
                    "station": str(ref.get("station") or ""),
                    "location": str(ref.get("location") or ""),
                    "channel": ch,
                    "phase_hint": str(ref.get("phase_hint") or ""),
                    "time": str(ref.get("time") or ""),
                    "dist_km": _safe_float(ref.get("dist_km")),
                    "source_seed_id": str(ref.get("seed_id") or ""),
                }
            )
    return tasks


def _station_level_triplet_tasks(
    *,
    selected_picks: list[dict[str, Any]],
    channels: list[str],
) -> list[dict[str, Any]]:
    """
    From selected P picks, keep one reference pick per station (earliest pick time),
    and emit one task per station requesting all channels in a single output file.
    """
    by_sta: dict[tuple[str, str, str], dict[str, Any]] = {}
    for p in selected_picks:
        key = (
            str(p.get("network") or ""),
            str(p.get("station") or ""),
            str(p.get("location") or ""),
        )
        prev = by_sta.get(key)
        if prev is None or str(p.get("time") or "") < str(prev.get("time") or ""):
            by_sta[key] = p

    tasks: list[dict[str, Any]] = []
    for (_net, _sta, _loc), ref in sorted(by_sta.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        tasks.append(
            {
                "network": str(ref.get("network") or ""),
                "station": str(ref.get("station") or ""),
                "location": str(ref.get("location") or ""),
                "channels": tuple(channels),
                "phase_hint": str(ref.get("phase_hint") or ""),
                "time": str(ref.get("time") or ""),
                "dist_km": _safe_float(ref.get("dist_km")),
                "source_seed_id": str(ref.get("seed_id") or ""),
            }
        )
    return tasks


def _triplet_channel_tag(channels: tuple[str, ...]) -> str:
    prefixes = {ch[:2].upper() for ch in channels if len(ch) >= 2}
    if len(prefixes) == 1:
        prefix = list(prefixes)[0]
        return f"{prefix}3"
    return "CH3"


def _triplet_filename(task: TripletTask) -> str:
    return f"{task.network}_{task.station}_{task.event_datetime_tag}.mseed"


def _triplet_relpath(task: TripletTask, waveforms_subdir: str) -> str:
    return os.path.join(waveforms_subdir, _triplet_filename(task))


def _download_pick(
    *,
    client_url: str,
    task: PickTask,
    waveforms_subdir: str,
    pre_p_s: float,
    post_p_s: float,
    overwrite: bool,
    dry_run: bool,
) -> dict[str, Any]:
    network = task.network
    station = task.station
    location = task.location
    channel = task.channel
    phase_hint = task.phase_hint
    seed_id = f"{network}.{station}.{location}.{channel}"
    dist_km = task.dist_km
    pick_time_str = task.pick_time

    row = {
        "event_folder": task.event_folder,
        "match_status": task.match_status,
        "fdsn_event_id": task.fdsn_event_id,
        "seed_id": seed_id,
        "network": network,
        "station": station,
        "location": location,
        "channel": channel,
        "phase_hint": phase_hint,
        "pick_time": pick_time_str,
        "dist_km": dist_km if dist_km is not None else "",
        "start_time": "",
        "end_time": "",
        "status": "",
        "mseed_path": "",
        "channels_requested": channel,
        "event_datetime_tag": "",
        "filename_pattern": "",
        "name_collision": "0",
        "source_seed_id": task.source_seed_id,
        "error": "",
    }

    try:
        pick_time = UTCDateTime(pick_time_str)
        t0 = pick_time - float(pre_p_s)
        t1 = pick_time + float(post_p_s)
        row["start_time"] = t0.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        row["end_time"] = t1.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        loc_tag = location if location else "--"
        ptag = pick_time.strftime("%Y%m%dT%H%M%S%fZ")
        rel = os.path.join(waveforms_subdir, f"{network}.{station}.{loc_tag}.{channel}_{ptag}.mseed")
        out_path = os.path.join(task.event_dir, rel)
        row["mseed_path"] = out_path

        if os.path.exists(out_path) and not overwrite:
            row["status"] = "skipped_exists"
            return row

        if dry_run:
            row["status"] = "planned"
            return row

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        client = _client_for(client_url)
        st = client.get_waveforms(network, station, location, channel, t0, t1)
        if len(st) == 0:
            raise RuntimeError("empty stream")
        st.write(out_path, format="MSEED")
        row["status"] = "downloaded"
        return row

    except Exception as e:
        row["status"] = "error"
        row["error"] = str(e)
        return row


def _download_triplet(
    *,
    client_url: str,
    task: TripletTask,
    waveforms_subdir: str,
    pre_p_s: float,
    post_p_s: float,
    overwrite: bool,
    dry_run: bool,
) -> dict[str, Any]:
    network = task.network
    station = task.station
    location = task.location
    channels = tuple(ch.upper() for ch in task.channels)
    channel_tag = _triplet_channel_tag(channels)
    phase_hint = task.phase_hint
    seed_id = f"{network}.{station}.{location}.TRIPLET"
    dist_km = task.dist_km
    pick_time_str = task.pick_time

    row = {
        "event_folder": task.event_folder,
        "match_status": task.match_status,
        "fdsn_event_id": task.fdsn_event_id,
        "seed_id": seed_id,
        "network": network,
        "station": station,
        "location": location,
        "channel": channel_tag,
        "phase_hint": phase_hint,
        "pick_time": pick_time_str,
        "dist_km": dist_km if dist_km is not None else "",
        "start_time": "",
        "end_time": "",
        "status": "",
        "mseed_path": "",
        "channels_requested": ",".join(channels),
        "event_datetime_tag": task.event_datetime_tag,
        "filename_pattern": STEP03_FILENAME_PATTERN,
        "name_collision": "0",
        "source_seed_id": task.source_seed_id,
        "error": "",
    }

    try:
        if not task.event_datetime_tag:
            row["status"] = "error_missing_event_datetime"
            row["error"] = "could not resolve event origin datetime tag"
            return row

        pick_time = UTCDateTime(pick_time_str)
        t0 = pick_time - float(pre_p_s)
        t1 = pick_time + float(post_p_s)
        row["start_time"] = t0.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        row["end_time"] = t1.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        rel = _triplet_relpath(task, waveforms_subdir=waveforms_subdir)
        out_path = os.path.join(task.event_dir, rel)
        row["mseed_path"] = out_path

        if os.path.exists(out_path) and not overwrite:
            row["status"] = "skipped_exists"
            return row

        if dry_run:
            row["status"] = "planned"
            return row

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        client = _client_for(client_url)

        out = Stream()
        missing: list[str] = []
        for ch in channels:
            st = client.get_waveforms(network, station, location, ch, t0, t1)
            selected = st.select(channel=ch)
            if len(selected) == 0:
                missing.append(ch)
                continue
            out += selected[0].copy()

        if missing:
            raise RuntimeError(f"missing channels in download: {missing}")
        if len(out) == 0:
            raise RuntimeError("empty stream")

        out.write(out_path, format="MSEED")
        row["status"] = "downloaded"
        return row

    except Exception as e:
        row["status"] = "error"
        row["error"] = str(e)
        return row


def _triplet_collision_row(
    *,
    task: TripletTask,
    out_path: str,
    pre_p_s: float,
    post_p_s: float,
) -> dict[str, Any]:
    seed_id = f"{task.network}.{task.station}.{task.location}.TRIPLET"
    row = {
        "event_folder": task.event_folder,
        "match_status": task.match_status,
        "fdsn_event_id": task.fdsn_event_id,
        "seed_id": seed_id,
        "network": task.network,
        "station": task.station,
        "location": task.location,
        "channel": _triplet_channel_tag(tuple(ch.upper() for ch in task.channels)),
        "phase_hint": task.phase_hint,
        "pick_time": task.pick_time,
        "dist_km": task.dist_km if task.dist_km is not None else "",
        "start_time": "",
        "end_time": "",
        "status": "error_name_collision",
        "mseed_path": out_path,
        "channels_requested": ",".join(ch.upper() for ch in task.channels),
        "event_datetime_tag": task.event_datetime_tag,
        "filename_pattern": STEP03_FILENAME_PATTERN,
        "name_collision": "1",
        "source_seed_id": task.source_seed_id,
        "error": "duplicate NET_STA_DATETIME target for this event",
    }
    try:
        pick_time = UTCDateTime(task.pick_time)
        row["start_time"] = (pick_time - float(pre_p_s)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        row["end_time"] = (pick_time + float(post_p_s)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    except Exception:
        pass
    return row


def _split_triplet_tasks_by_collision(
    *,
    tasks: list[TripletTask],
    waveforms_subdir: str,
    pre_p_s: float,
    post_p_s: float,
) -> tuple[list[TripletTask], list[dict[str, Any]]]:
    by_out_path: dict[str, list[TripletTask]] = {}
    valid: list[TripletTask] = []
    collision_rows: list[dict[str, Any]] = []

    for t in tasks:
        if not t.event_datetime_tag:
            valid.append(t)
            continue
        out_path = os.path.join(t.event_dir, _triplet_relpath(t, waveforms_subdir=waveforms_subdir))
        by_out_path.setdefault(out_path, []).append(t)

    for out_path, bucket in by_out_path.items():
        if len(bucket) == 1:
            valid.append(bucket[0])
            continue
        for t in bucket:
            collision_rows.append(
                _triplet_collision_row(
                    task=t,
                    out_path=out_path,
                    pre_p_s=pre_p_s,
                    post_p_s=post_p_s,
                )
            )
    return valid, collision_rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Download 60 s waveform windows around P picks from step02 bundles.")
    ap.add_argument("--events-root", default="data/sisbra_mg_maglt4_depthlt10_w24")
    ap.add_argument("--client-url", default="http://127.0.0.1:28080")
    ap.add_argument("--max-pick-dist-km", type=float, default=400.0)
    ap.add_argument("--pre-p-s", type=float, default=10.0)
    ap.add_argument("--post-p-s", type=float, default=50.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--waveforms-subdir", default="waveform")
    ap.add_argument("--summary-csv", default="outputs/waveform_triplet_download_summary_events.csv")
    ap.add_argument("--limit-events", type=int, default=0, help="Optional event limit (0 = all).")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-non-matched", action="store_true")
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
    ap.add_argument("--max-mag", type=float, default=None, help="Optional strict upper bound for magnitude (mag < max-mag).")
    ap.add_argument("--max-depth-km", type=float, default=None, help="Optional strict upper bound for depth (depth_km < max-depth-km).")
    ap.add_argument("--min-year", type=int, default=None, help="Optional minimum year filter (applied last).")
    ap.add_argument(
        "--component-channels",
        default="",
        help="Comma-separated channel list to force per station, e.g. HHZ,HHN,HHE. "
        "If empty, downloads only picked channel.",
    )
    ap.add_argument(
        "--single-file-triplet",
        action="store_true",
        default=True,
        help="When component-channels are set, store one mseed per station using NET_STA_DATETIME naming (default: enabled).",
    )
    ap.add_argument(
        "--split-component-files",
        action="store_false",
        dest="single_file_triplet",
        help="When component-channels are set, store one mseed per channel (legacy mode).",
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
    component_channels_cli = [x.strip().upper() for x in str(args.component_channels).split(",") if x.strip()]

    event_json_paths = sorted(glob.glob(os.path.join(args.events_root, "*", "event.json")))
    if args.limit_events and args.limit_events > 0:
        event_json_paths = event_json_paths[: args.limit_events]
    if not event_json_paths:
        raise SystemExit(f"No event.json found under: {args.events_root}")

    pick_tasks_queue: list[PickTask] = []
    triplet_tasks_queue: list[TripletTask] = []
    events_scanned = 0
    events_selected = 0
    events_skipped_filters = 0
    events_with_p = 0
    events_no_p = 0
    events_state_inconsistent_audit = 0
    events_state_unknown_audit = 0
    skip_reason_counts: dict[str, int] = {}

    for p in event_json_paths:
        events_scanned += 1
        payload = json.load(open(p, "r", encoding="utf-8"))
        status = str(payload.get("match_status") or "")
        if (not args.include_non_matched) and status != "matched":
            continue

        sis = payload.get("sisbra") or {}
        geo = evaluate_mg_filter(
            latitude=sis.get("latitude"),
            longitude=sis.get("longitude"),
            state_value=sis.get("state"),
            state_target=str(args.state_filter or "MG"),
            mg_polygon_year=int(args.mg_polygon_year),
            mg_polygon_gpkg_path=str(args.mg_polygon_gpkg or ""),
            mg_polygon_layer=str(args.mg_polygon_layer or ""),
        )
        st_geo_consistency = str(geo["st_geo_consistency"])
        if st_geo_consistency.startswith("INCONSISTENT_"):
            events_state_inconsistent_audit += 1
        elif st_geo_consistency == "UNKNOWN_ST":
            events_state_unknown_audit += 1

        if str(geo["mg_filter_status"]) != KEEP_IN_MG:
            events_skipped_filters += 1
            reason = str(geo["mg_filter_status"]).lower()
            skip_reason_counts[reason] = skip_reason_counts.get(reason, 0) + 1
            continue

        if args.max_mag is not None:
            mag = _safe_float(sis.get("magnitude"))
            if mag is None or not (mag < float(args.max_mag)):
                events_skipped_filters += 1
                skip_reason_counts["mag_not_lt_max"] = skip_reason_counts.get("mag_not_lt_max", 0) + 1
                continue
        if args.max_depth_km is not None:
            depth_km = _safe_float(sis.get("depth_km"))
            if depth_km is None or not (depth_km < float(args.max_depth_km)):
                events_skipped_filters += 1
                skip_reason_counts["depth_not_lt_max"] = skip_reason_counts.get("depth_not_lt_max", 0) + 1
                continue
        if args.min_year is not None:
            year = _sis_event_year(sis)
            if year is None or year < int(args.min_year):
                events_skipped_filters += 1
                skip_reason_counts["year_lt_min_or_missing"] = (
                    skip_reason_counts.get("year_lt_min_or_missing", 0) + 1
                )
                continue

        events_selected += 1

        selected = _selected_picks(payload, max_pick_dist_km=float(args.max_pick_dist_km))
        if not selected:
            events_no_p += 1
            continue

        events_with_p += 1
        event_dir = os.path.dirname(p)
        folder = os.path.basename(event_dir)
        event_datetime_tag = _event_datetime_tag(payload, folder)
        ev_id = _event_id(payload)
        contract = payload.get("waveform_download_contract") or {}
        raw_contract_channels = contract.get("step03_component_channels")
        if isinstance(raw_contract_channels, list):
            contract_channels = [str(x).strip().upper() for x in raw_contract_channels if str(x).strip()]
        else:
            contract_channels = [
                x.strip().upper() for x in str(raw_contract_channels or "").split(",") if x.strip()
            ]
        event_component_channels = list(component_channels_cli) if component_channels_cli else contract_channels
        event_single_file_triplet = bool(args.single_file_triplet)
        contract_mode = str(contract.get("step03_output_mode") or "")
        if contract_mode == "triplet_single_file":
            event_single_file_triplet = True
        elif contract_mode == "split_component_files":
            event_single_file_triplet = False

        pick_tasks: list[dict[str, Any]]
        triplet_tasks: list[dict[str, Any]]
        if event_component_channels:
            if event_single_file_triplet:
                pick_tasks = []
                triplet_tasks = _station_level_triplet_tasks(
                    selected_picks=selected,
                    channels=event_component_channels,
                )
            else:
                pick_tasks = _station_level_tasks(
                    selected_picks=selected,
                    channels=event_component_channels,
                )
                triplet_tasks = []
        else:
            pick_tasks = []
            triplet_tasks = []
            for pick in selected:
                pick_tasks.append(
                    {
                        "network": str(pick.get("network") or ""),
                        "station": str(pick.get("station") or ""),
                        "location": str(pick.get("location") or ""),
                        "channel": str(pick.get("channel") or ""),
                        "phase_hint": str(pick.get("phase_hint") or ""),
                        "time": str(pick.get("time") or ""),
                        "dist_km": _safe_float(pick.get("dist_km")),
                        "source_seed_id": str(pick.get("seed_id") or ""),
                    }
                )

        for pick in pick_tasks:
            pick_tasks_queue.append(
                PickTask(
                    event_dir=event_dir,
                    event_folder=folder,
                    match_status=status,
                    fdsn_event_id=ev_id,
                    network=pick["network"],
                    station=pick["station"],
                    location=pick["location"],
                    channel=pick["channel"],
                    phase_hint=pick["phase_hint"],
                    pick_time=pick["time"],
                    dist_km=pick["dist_km"],
                    source_seed_id=pick["source_seed_id"],
                )
            )
        for triplet in triplet_tasks:
            triplet_tasks_queue.append(
                TripletTask(
                    event_dir=event_dir,
                    event_folder=folder,
                    match_status=status,
                    fdsn_event_id=ev_id,
                    network=triplet["network"],
                    station=triplet["station"],
                    location=triplet["location"],
                    channels=triplet["channels"],
                    phase_hint=triplet["phase_hint"],
                    pick_time=triplet["time"],
                    event_datetime_tag=event_datetime_tag or "",
                    dist_km=triplet["dist_km"],
                    source_seed_id=triplet["source_seed_id"],
                )
            )

    pre_p_s = float(args.pre_p_s)
    post_p_s = float(args.post_p_s)
    triplet_tasks_queue, collision_rows = _split_triplet_tasks_by_collision(
        tasks=triplet_tasks_queue,
        waveforms_subdir=args.waveforms_subdir,
        pre_p_s=pre_p_s,
        post_p_s=post_p_s,
    )

    rows: list[dict[str, Any]] = list(collision_rows)
    with ThreadPoolExecutor(max_workers=max(1, int(args.workers))) as ex:
        futs = []
        for t in pick_tasks_queue:
            futs.append(
                ex.submit(
                    _download_pick,
                    client_url=args.client_url,
                    task=t,
                    waveforms_subdir=args.waveforms_subdir,
                    pre_p_s=pre_p_s,
                    post_p_s=post_p_s,
                    overwrite=bool(args.overwrite),
                    dry_run=bool(args.dry_run),
                )
            )
        for t in triplet_tasks_queue:
            futs.append(
                ex.submit(
                    _download_triplet,
                    client_url=args.client_url,
                    task=t,
                    waveforms_subdir=args.waveforms_subdir,
                    pre_p_s=pre_p_s,
                    post_p_s=post_p_s,
                    overwrite=bool(args.overwrite),
                    dry_run=bool(args.dry_run),
                )
            )
        for fut in as_completed(futs):
            rows.append(fut.result())

    rows.sort(key=lambda r: (r["event_folder"], r["seed_id"], r["pick_time"]))
    os.makedirs(os.path.dirname(args.summary_csv) or ".", exist_ok=True)
    fieldnames = [
        "event_folder",
        "match_status",
        "fdsn_event_id",
        "seed_id",
        "network",
        "station",
        "location",
        "channel",
        "phase_hint",
        "pick_time",
        "dist_km",
        "start_time",
        "end_time",
        "status",
        "mseed_path",
        "channels_requested",
        "event_datetime_tag",
        "filename_pattern",
        "name_collision",
        "source_seed_id",
        "error",
    ]
    with open(args.summary_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    counts: dict[str, int] = {}
    for r in rows:
        s = str(r.get("status") or "")
        counts[s] = counts.get(s, 0) + 1

    print(f"events_root={args.events_root}")
    print(f"events_scanned={events_scanned}")
    print(f"events_selected={events_selected}")
    print(f"events_skipped_filters={events_skipped_filters}")
    print(f"events_with_p={events_with_p}")
    print(f"events_no_p={events_no_p}")
    print(f"state_filter_audit_only={args.state_filter}")
    print(f"mg_polygon_year={args.mg_polygon_year}")
    print(f"mg_polygon_gpkg={args.mg_polygon_gpkg}")
    print(f"mg_polygon_layer={args.mg_polygon_layer}")
    if args.min_year is not None:
        print(f"min_year={args.min_year}")
    print(f"events_state_inconsistent_audit={events_state_inconsistent_audit}")
    print(f"events_state_unknown_audit={events_state_unknown_audit}")
    print(f"skip_reason_counts={skip_reason_counts}")
    if component_channels_cli:
        print(f"component_channels_cli={component_channels_cli}")
    print(f"default_single_file_triplet={args.single_file_triplet}")
    print(f"single_file_pattern={STEP03_FILENAME_PATTERN}")
    print(f"single_file_datetime_source={STEP03_DATETIME_SOURCE}")
    print(f"single_file_datetime_format={STEP03_DATETIME_FORMAT}")
    print(f"name_collision_rows={len(collision_rows)}")
    print(f"pick_tasks={len(pick_tasks_queue)}")
    print(f"triplet_tasks={len(triplet_tasks_queue)}")
    print(f"download_jobs={len(pick_tasks_queue) + len(triplet_tasks_queue)}")
    print(f"summary_csv={args.summary_csv}")
    print(f"status_counts={counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
