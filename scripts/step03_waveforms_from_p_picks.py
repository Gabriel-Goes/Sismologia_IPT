#!/usr/bin/env python3
"""
Step 03: download waveform windows around P picks from step02 event bundles.

Rules implemented:
- use only picks with phase_hint starting with "P" (P, Pg, Pn, ...)
- use only picks with dist_km <= --max-pick-dist-km
- fetch 60 s windows: [pick_time - --pre-p-s, pick_time + --post-p-s]
- do not fetch any waveform for events without qualifying P picks
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any

from obspy import UTCDateTime
from obspy.clients.fdsn import Client


_THREAD_LOCAL = threading.local()


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


def _event_id(payload: dict[str, Any]) -> str:
    rid = ((payload.get("fdsn") or {}).get("resource_id") or "").strip()
    return rid.split("/")[-1] if rid else ""


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


def main() -> int:
    ap = argparse.ArgumentParser(description="Download 60 s waveform windows around P picks from step02 bundles.")
    ap.add_argument("--events-root", default="data/sisbra_mg_maglt4_depthlt10_w24")
    ap.add_argument("--client-url", default="http://127.0.0.1:28080")
    ap.add_argument("--max-pick-dist-km", type=float, default=400.0)
    ap.add_argument("--pre-p-s", type=float, default=10.0)
    ap.add_argument("--post-p-s", type=float, default=50.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--waveforms-subdir", default="waveforms")
    ap.add_argument("--summary-csv", default="outputs/waveform_picks_download_summary.csv")
    ap.add_argument("--limit-events", type=int, default=0, help="Optional event limit (0 = all).")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-non-matched", action="store_true")
    ap.add_argument("--state-filter", default="", help="Optional SISBRA state filter, e.g. MG.")
    ap.add_argument("--max-mag", type=float, default=None, help="Optional strict upper bound for magnitude (mag < max-mag).")
    ap.add_argument("--max-depth-km", type=float, default=None, help="Optional strict upper bound for depth (depth_km < max-depth-km).")
    ap.add_argument(
        "--component-channels",
        default="",
        help="Comma-separated channel list to force per station, e.g. HHZ,HHN,HHE. "
        "If empty, downloads only picked channel.",
    )
    args = ap.parse_args()
    component_channels = [x.strip().upper() for x in str(args.component_channels).split(",") if x.strip()]

    event_json_paths = sorted(glob.glob(os.path.join(args.events_root, "*", "event.json")))
    if args.limit_events and args.limit_events > 0:
        event_json_paths = event_json_paths[: args.limit_events]
    if not event_json_paths:
        raise SystemExit(f"No event.json found under: {args.events_root}")

    tasks: list[PickTask] = []
    events_scanned = 0
    events_selected = 0
    events_skipped_filters = 0
    events_with_p = 0
    events_no_p = 0

    for p in event_json_paths:
        events_scanned += 1
        payload = json.load(open(p, "r", encoding="utf-8"))
        status = str(payload.get("match_status") or "")
        if (not args.include_non_matched) and status != "matched":
            continue

        sis = payload.get("sisbra") or {}
        if args.state_filter:
            state = str(sis.get("state") or "").strip().upper()
            if state != str(args.state_filter).strip().upper():
                events_skipped_filters += 1
                continue
        if args.max_mag is not None:
            mag = _safe_float(sis.get("magnitude"))
            if mag is None or not (mag < float(args.max_mag)):
                events_skipped_filters += 1
                continue
        if args.max_depth_km is not None:
            depth_km = _safe_float(sis.get("depth_km"))
            if depth_km is None or not (depth_km < float(args.max_depth_km)):
                events_skipped_filters += 1
                continue

        events_selected += 1

        selected = _selected_picks(payload, max_pick_dist_km=float(args.max_pick_dist_km))
        if not selected:
            events_no_p += 1
            continue

        events_with_p += 1
        event_dir = os.path.dirname(p)
        folder = os.path.basename(event_dir)
        ev_id = _event_id(payload)
        pick_tasks: list[dict[str, Any]]
        if component_channels:
            pick_tasks = _station_level_tasks(selected_picks=selected, channels=component_channels)
        else:
            pick_tasks = []
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
            tasks.append(
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

    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, int(args.workers))) as ex:
        futs = [
            ex.submit(
                _download_pick,
                client_url=args.client_url,
                task=t,
                waveforms_subdir=args.waveforms_subdir,
                pre_p_s=float(args.pre_p_s),
                post_p_s=float(args.post_p_s),
                overwrite=bool(args.overwrite),
                dry_run=bool(args.dry_run),
            )
            for t in tasks
        ]
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
    if component_channels:
        print(f"component_channels={component_channels}")
    print(f"pick_tasks={len(tasks)}")
    print(f"summary_csv={args.summary_csv}")
    print(f"status_counts={counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
