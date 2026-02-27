#!/usr/bin/env python3
"""
Organize event folders into compatible/incompatible sets.

Compatible event (default policy):
- match_status == "matched"
- sisbra.state == --state-filter
- sisbra.magnitude < --max-mag
- sisbra.depth_km < --max-depth-km
- has at least one P pick (phase_hint starts with "P") with dist_km <= --max-pick-dist-km
- has at least one downloaded waveform in --download-summary-csv (status in downloaded/skipped_exists)

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
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any


def _safe_float(v: Any) -> float | None:
    try:
        return float(v)
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
    ap.add_argument("--state-filter", default="MG")
    ap.add_argument("--max-mag", type=float, default=4.0)
    ap.add_argument("--max-depth-km", type=float, default=10.0)
    ap.add_argument("--max-pick-dist-km", type=float, default=400.0)
    ap.add_argument("--report-csv", default="outputs/eventos_compatibilidade_report.csv")
    ap.add_argument("--report-md", default="outputs/eventos_compatibilidade_report.md")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--copy", action="store_true", help="Copy instead of move.")
    args = ap.parse_args()

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

    event_json_paths = sorted(glob.glob(os.path.join(args.events_root, "*", "event.json")))
    for p in event_json_paths:
        event_dir = os.path.dirname(p)
        src_folder = os.path.basename(event_dir)
        payload = json.load(open(p, "r", encoding="utf-8"))

        sis = payload.get("sisbra") or {}
        match_status = str(payload.get("match_status") or "")
        state = str(sis.get("state") or "").strip().upper()
        mag = _safe_float(sis.get("magnitude"))
        dep = _safe_float(sis.get("depth_km"))
        origin_time = str(sis.get("origin_time") or "")
        dt_tag = _datetime_tag(origin_time)

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
        if state != str(args.state_filter).upper():
            reasons.append("state_mismatch")
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
        f.write(f"- state_filter: `{args.state_filter}`\n")
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

