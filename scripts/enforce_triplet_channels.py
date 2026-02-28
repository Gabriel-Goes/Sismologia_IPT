#!/usr/bin/env python3
"""
Keep only events with required 3-channel triplet in compatible root.

Rule:
- event remains in compatible root if at least one station (net, sta, loc)
  has all required channels (default HHZ,HHN,HHE) in waveform files.
  This supports both:
  - split files per channel: NET.STA.LOC.HHZ_...mseed
  - merged 3C files: NET.STA.LOC.HH3_...mseed
  - merged 3C files: NET_STA_DATETIME.mseed
  (for merged files, channels are read from mseed headers)
- otherwise event is moved to incompatible root.
"""

from __future__ import annotations

import argparse
import csv
import glob
import os
import shutil
from collections import Counter
from datetime import datetime, timezone


def _station_channels_from_mseed(
    event_dir: str,
    waveforms_subdir: str,
    required_channels: set[str],
) -> dict[tuple[str, str, str], set[str]]:
    out: dict[tuple[str, str, str], set[str]] = {}
    pattern = os.path.join(event_dir, waveforms_subdir, "*.mseed")
    for fp in glob.glob(pattern):
        base = os.path.basename(fp)
        # Split-format hint in filename: NET.STA.LOC.CHA_YYYY...mseed
        left = base.split("_", 1)[0]
        parts = left.split(".")
        if len(parts) >= 4:
            net, sta, loc, cha = parts[0], parts[1], parts[2], parts[3].upper()
            key = (net, sta, loc)
            if cha in required_channels:
                out.setdefault(key, set()).add(cha)
                continue
        try:
            from obspy import read

            st = read(fp, headonly=True)
            for tr in st:
                net = str(getattr(tr.stats, "network", "") or (parts[0] if len(parts) >= 1 else ""))
                sta = str(getattr(tr.stats, "station", "") or (parts[1] if len(parts) >= 2 else ""))
                loc = str(getattr(tr.stats, "location", "") or (parts[2] if len(parts) >= 3 else ""))
                cha = str(getattr(tr.stats, "channel", "")).upper()
                if not net or not sta or not cha:
                    continue
                out.setdefault((net, sta, loc), set()).add(cha)
        except Exception:
            continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Enforce required 3-channel triplet in compatible events.")
    ap.add_argument("--compatible-root", default="data/eventos_compativeis")
    ap.add_argument("--incompatible-root", default="data/eventos_nao_compativeis")
    ap.add_argument("--waveforms-subdir", default="waveforms")
    ap.add_argument("--required-channels", default="HHZ,HHN,HHE")
    ap.add_argument("--report-csv", default="outputs/eventos_triplet_filter_report.csv")
    ap.add_argument("--report-md", default="outputs/eventos_triplet_filter_report.md")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    req = {x.strip().upper() for x in str(args.required_channels).split(",") if x.strip()}
    if not req:
        raise SystemExit("required-channels is empty")

    os.makedirs(args.compatible_root, exist_ok=True)
    os.makedirs(args.incompatible_root, exist_ok=True)
    os.makedirs(os.path.dirname(args.report_csv) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.report_md) or ".", exist_ok=True)

    comp_dirs = sorted([d for d in glob.glob(os.path.join(args.compatible_root, "*")) if os.path.isdir(d)])

    rows: list[dict[str, str]] = []
    stats = Counter()
    for d in comp_dirs:
        folder = os.path.basename(d)
        by_sta = _station_channels_from_mseed(d, args.waveforms_subdir, req)
        max_sta_channels = max((len(v) for v in by_sta.values()), default=0)
        has_triplet = any(req.issubset(chs) for chs in by_sta.values())

        action = "keep_compatible" if has_triplet else "move_to_incompatible"
        stats[action] += 1
        stats["events_scanned"] += 1

        if (not has_triplet) and (not args.dry_run):
            dst = os.path.join(args.incompatible_root, folder)
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            shutil.move(d, dst)

        rows.append(
            {
                "folder": folder,
                "has_triplet": "1" if has_triplet else "0",
                "stations_with_waveforms": str(len(by_sta)),
                "max_channels_on_single_station": str(max_sta_channels),
                "required_channels": ",".join(sorted(req)),
                "action": action,
            }
        )

    with open(args.report_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "folder",
                "has_triplet",
                "stations_with_waveforms",
                "max_channels_on_single_station",
                "required_channels",
                "action",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    with open(args.report_md, "w", encoding="utf-8") as f:
        f.write("# Triplet Channel Filter Report\n\n")
        f.write("## Config\n")
        f.write(f"- generated_at_utc: `{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}`\n")
        f.write(f"- compatible_root: `{args.compatible_root}`\n")
        f.write(f"- incompatible_root: `{args.incompatible_root}`\n")
        f.write(f"- waveforms_subdir: `{args.waveforms_subdir}`\n")
        f.write(f"- required_channels: `{','.join(sorted(req))}`\n")
        f.write(f"- dry_run: `{args.dry_run}`\n\n")
        f.write("## Totals\n")
        f.write(f"- events_scanned: `{stats['events_scanned']}`\n")
        f.write(f"- keep_compatible: `{stats['keep_compatible']}`\n")
        f.write(f"- move_to_incompatible: `{stats['move_to_incompatible']}`\n")
        f.write(f"- report_csv: `{args.report_csv}`\n")

    print(f"events_scanned={stats['events_scanned']}")
    print(f"keep_compatible={stats['keep_compatible']}")
    print(f"move_to_incompatible={stats['move_to_incompatible']}")
    print(f"report_csv={args.report_csv}")
    print(f"report_md={args.report_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
