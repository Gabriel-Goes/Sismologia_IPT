#!/usr/bin/env python3
"""
Merge split HHZ/HHN/HHE waveform files into one 3C mseed per station.

Target naming:
- NET_STA_DATETIME.mseed (DATETIME = event origin UTC, %Y%jT%H%M%S)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from seismic_event_discriminator.rnc_adapter import discover_triplets, list_event_dirs


FILENAME_PATTERN = "NET_STA_DATETIME.mseed"
DATETIME_FORMAT = "%Y%jT%H%M%S"


def _parse_utc_datetime(raw: object) -> datetime | None:
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


def _event_datetime_tag(event_dir: str, event_id: str) -> str | None:
    event_json = os.path.join(event_dir, "event.json")
    if os.path.exists(event_json):
        try:
            payload = json.load(open(event_json, "r", encoding="utf-8"))
            sis = payload.get("sisbra") or {}
            fdsn = payload.get("fdsn") or {}
            for candidate in (sis.get("origin_time"), fdsn.get("origin_time")):
                dt = _parse_utc_datetime(candidate)
                if dt is not None:
                    return dt.strftime(DATETIME_FORMAT)
        except Exception:
            pass
    base = str(event_id or "").split("_")[0]
    try:
        dt = datetime.strptime(base, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
        return dt.strftime(DATETIME_FORMAT)
    except Exception:
        return None


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Merge triplet waveforms into NET_STA_DATETIME.mseed files.")
    ap.add_argument("--compatible-root", default="data/eventos_compativeis")
    ap.add_argument("--waveforms-subdir", default="waveforms")
    ap.add_argument("--merged-subdir", default="waveforms_3c")
    ap.add_argument("--required-channels", default="HHZ,HHN,HHE")
    ap.add_argument("--limit-events", type=int, default=0, help="0 means all events.")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--summary-csv", default="outputs/waveforms_3c_merge_summary.csv")
    return ap.parse_args()


def main() -> int:
    args = _parse_args()
    required_channels = [x.strip().upper() for x in str(args.required_channels).split(",") if x.strip()]
    event_dirs = list_event_dirs(args.compatible_root)
    if args.limit_events and args.limit_events > 0:
        event_dirs = event_dirs[: args.limit_events]

    os.makedirs(os.path.dirname(args.summary_csv) or ".", exist_ok=True)
    rows: list[dict[str, str]] = []
    written = 0
    skipped = 0
    errors = 0

    # Lazy import keeps --help usable even without ObsPy.
    import obspy as op

    for idx, event_dir in enumerate(event_dirs, start=1):
        event_id = os.path.basename(event_dir)
        event_datetime_tag = _event_datetime_tag(event_dir, event_id)
        triplets, discovery_errors = discover_triplets(
            event_dir=event_dir,
            waveforms_subdir=args.waveforms_subdir,
            required_channels=required_channels,
        )
        if discovery_errors:
            for err in discovery_errors:
                rows.append(
                    {
                        "event_id": event_id,
                        "network": str(err.get("network") or ""),
                        "station": str(err.get("station") or ""),
                        "location": str(err.get("location") or ""),
                        "pick_time_tag": str(err.get("pick_time_tag") or ""),
                        "event_datetime_tag": event_datetime_tag or "",
                        "filename_pattern": FILENAME_PATTERN,
                        "merged_path": "",
                        "status": "error_discovery",
                        "message": str(err.get("message") or ""),
                    }
                )
                errors += 1

        out_dir = os.path.join(event_dir, args.merged_subdir)
        os.makedirs(out_dir, exist_ok=True)

        pending_merges: list[tuple[object, str]] = []
        pending_by_target: dict[str, list[object]] = {}
        for t in triplets:
            if t.merged_path:
                rows.append(
                    {
                        "event_id": event_id,
                        "network": t.network,
                        "station": t.station,
                        "location": t.location if t.location else "--",
                        "pick_time_tag": t.pick_time_tag,
                        "event_datetime_tag": event_datetime_tag or "",
                        "filename_pattern": FILENAME_PATTERN,
                        "merged_path": t.merged_path,
                        "status": "skipped_already_merged",
                        "message": "",
                    }
                )
                skipped += 1
                continue
            if not event_datetime_tag:
                rows.append(
                    {
                        "event_id": event_id,
                        "network": t.network,
                        "station": t.station,
                        "location": t.location if t.location else "--",
                        "pick_time_tag": t.pick_time_tag,
                        "event_datetime_tag": "",
                        "filename_pattern": FILENAME_PATTERN,
                        "merged_path": "",
                        "status": "error_missing_event_datetime",
                        "message": "could not resolve event origin datetime tag",
                    }
                )
                errors += 1
                continue
            merged_name = f"{t.network}_{t.station}_{event_datetime_tag}.mseed"
            merged_path = os.path.join(out_dir, merged_name)
            pending_by_target.setdefault(merged_path, []).append(t)

        for merged_path, bucket in pending_by_target.items():
            if len(bucket) == 1:
                pending_merges.append((bucket[0], merged_path))
                continue
            for t in bucket:
                rows.append(
                    {
                        "event_id": event_id,
                        "network": t.network,
                        "station": t.station,
                        "location": t.location if t.location else "--",
                        "pick_time_tag": t.pick_time_tag,
                        "event_datetime_tag": event_datetime_tag or "",
                        "filename_pattern": FILENAME_PATTERN,
                        "merged_path": merged_path,
                        "status": "error_name_collision",
                        "message": "duplicate NET_STA_DATETIME target for this event",
                    }
                )
                errors += 1

        for t, merged_path in pending_merges:
            loc_tag = t.location if t.location else "--"

            if os.path.exists(merged_path) and not args.overwrite:
                rows.append(
                    {
                        "event_id": event_id,
                        "network": t.network,
                        "station": t.station,
                        "location": loc_tag,
                        "pick_time_tag": t.pick_time_tag,
                        "event_datetime_tag": event_datetime_tag or "",
                        "filename_pattern": FILENAME_PATTERN,
                        "merged_path": merged_path,
                        "status": "skipped_exists",
                        "message": "",
                    }
                )
                skipped += 1
                continue

            try:
                stream = op.Stream()
                for ch in required_channels:
                    st = op.read(t.component_paths[ch], dtype=float)
                    if len(st) == 0:
                        raise RuntimeError(f"empty stream for channel {ch}")
                    st.merge(method=1, fill_value="interpolate")
                    tr = st[0].copy()
                    tr.stats.channel = ch
                    stream += tr
                stream.write(merged_path, format="MSEED")
                rows.append(
                    {
                        "event_id": event_id,
                        "network": t.network,
                        "station": t.station,
                        "location": loc_tag,
                        "pick_time_tag": t.pick_time_tag,
                        "event_datetime_tag": event_datetime_tag or "",
                        "filename_pattern": FILENAME_PATTERN,
                        "merged_path": merged_path,
                        "status": "written",
                        "message": "",
                    }
                )
                written += 1
            except Exception as e:
                rows.append(
                    {
                        "event_id": event_id,
                        "network": t.network,
                        "station": t.station,
                        "location": loc_tag,
                        "pick_time_tag": t.pick_time_tag,
                        "event_datetime_tag": event_datetime_tag or "",
                        "filename_pattern": FILENAME_PATTERN,
                        "merged_path": merged_path,
                        "status": "error_merge",
                        "message": str(e),
                    }
                )
                errors += 1

        print(f"[{idx}/{len(event_dirs)}] {event_id} triplets={len(triplets)} event_datetime_tag={event_datetime_tag}")

    rows.sort(key=lambda r: (r["event_id"], r["network"], r["station"], r["pick_time_tag"], r["status"]))
    with open(args.summary_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "event_id",
                "network",
                "station",
                "location",
                "pick_time_tag",
                "event_datetime_tag",
                "filename_pattern",
                "merged_path",
                "status",
                "message",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    print(f"events={len(event_dirs)}")
    print(f"written={written}")
    print(f"skipped_exists={skipped}")
    print(f"errors={errors}")
    print(f"summary_csv={args.summary_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
