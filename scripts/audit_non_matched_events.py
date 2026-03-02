#!/usr/bin/env python3
"""
Audit non-matched step02 bundles (no_match + ambiguous) for investigation.

Produces:
- consolidated CSV with severity and agency context
- per-status CSVs (ambiguous/no_match)
- markdown summary with counts and top critical agencies
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
from collections import Counter
from typing import Any


def _extract_agency_tag(source_comments: str) -> str:
    s = (source_comments or "").strip()
    if not s:
        return "UNKNOWN"
    m = re.search(r"\(([^)]+)\)", s)
    if m:
        tag = m.group(1).strip()
    else:
        tag = s.split()[0].strip()
    return tag if tag else "UNKNOWN"


def _normalize_agency_tag(tag: str) -> str:
    t = str(tag or "").upper()
    t = re.sub(r"[^A-Z0-9]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t if t else "UNKNOWN"


def _is_critical_agency(agency_tag_normalized: str, critical_patterns: list[str]) -> bool:
    haystack = _normalize_agency_tag(agency_tag_normalized)
    for p in critical_patterns:
        needle = _normalize_agency_tag(p)
        if not needle or needle == "UNKNOWN":
            continue
        if needle in haystack:
            return True
    return False


def _severity_for_status(match_status: str, is_critical_agency: bool) -> str:
    status = str(match_status or "").strip().lower()
    if status == "matched":
        return "none"
    if is_critical_agency:
        return "critical"
    if status == "ambiguous":
        return "high"
    if status == "no_match":
        return "medium"
    return "high"


def _safe_float(v: Any) -> float | None:
    try:
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None
        return float(s)
    except Exception:
        return None


def _load_non_matched_bundles(non_matched_root: str) -> list[tuple[str, dict[str, Any]]]:
    pattern = os.path.join(non_matched_root, "**", "event.json")
    rows: list[tuple[str, dict[str, Any]]] = []
    for p in sorted(glob.glob(pattern, recursive=True)):
        try:
            with open(p, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception:
            continue
        status = str(payload.get("match_status") or "").strip().lower()
        if status in {"no_match", "ambiguous"}:
            rows.append((p, payload))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit no_match/ambiguous bundles for investigation.")
    ap.add_argument("--non-matched-root", default="data/events_stage_non_matched")
    ap.add_argument("--report-csv", default="outputs/non_matched_audit.csv")
    ap.add_argument("--report-md", default="outputs/non_matched_audit.md")
    ap.add_argument("--ambiguous-csv", default="outputs/ambiguous_events.csv")
    ap.add_argument("--no-match-csv", default="outputs/no_match_events.csv")
    ap.add_argument(
        "--critical-agency-patterns",
        default="IAG,USP,IAG-USP",
        help="CSV list of normalized agency patterns that should be marked critical.",
    )
    args = ap.parse_args()

    items = _load_non_matched_bundles(args.non_matched_root)
    if not items:
        raise SystemExit(f"No non-matched event.json found under: {args.non_matched_root}")

    critical_patterns = [
        _normalize_agency_tag(x) for x in str(args.critical_agency_patterns).split(",") if x.strip()
    ]

    rows: list[dict[str, Any]] = []
    by_status = Counter()
    by_severity = Counter()
    by_agency = Counter()
    by_agency_status = Counter()

    for path, payload in items:
        folder = os.path.basename(os.path.dirname(path))
        status = str(payload.get("match_status") or "").strip().lower()
        match = payload.get("match") or {}
        sis = payload.get("sisbra") or {}
        fdsn = payload.get("fdsn") or {}
        q = match.get("query") or {}
        source_comments = str(sis.get("source_comments") or "")
        sis_mag = _safe_float(sis.get("magnitude"))
        sis_depth = _safe_float(sis.get("depth_km"))

        agency_raw = str(match.get("sisbra_agency_tag_raw") or "").strip() or _extract_agency_tag(source_comments)
        agency_normalized = (
            str(match.get("sisbra_agency_tag_normalized") or "").strip() or _normalize_agency_tag(agency_raw)
        )
        is_critical_agency = _is_critical_agency(agency_normalized, critical_patterns)
        severity = str(match.get("severity") or "").strip().lower() or _severity_for_status(status, is_critical_agency)

        row = {
            "event_folder": folder,
            "event_json_path": path,
            "status": status,
            "severity": severity,
            "is_critical_agency": "1" if is_critical_agency else "0",
            "sisbra_origin_time": sis.get("origin_time", ""),
            "sisbra_state": str(sis.get("state") or "").strip().upper(),
            "sisbra_magnitude": "" if sis_mag is None else f"{sis_mag}",
            "sisbra_depth_km": "" if sis_depth is None else f"{sis_depth}",
            "sisbra_latitude": sis.get("latitude", ""),
            "sisbra_longitude": sis.get("longitude", ""),
            "sisbra_localities": sis.get("localities", ""),
            "sisbra_source_comments": source_comments,
            "sisbra_agency_tag_raw": agency_raw,
            "sisbra_agency_tag_normalized": agency_normalized,
            "fdsn_event_id": str(fdsn.get("resource_id") or ""),
            "candidate_count": match.get("candidate_count", ""),
            "best_dt_s": match.get("dt_s", ""),
            "best_dist_km": match.get("dist_km", ""),
            "best_mag_diff": match.get("mag_diff", ""),
            "alt_dt_s": (match.get("alt_candidate") or {}).get("dt_s", ""),
            "alt_dist_km": (match.get("alt_candidate") or {}).get("dist_km", ""),
            "alt_mag_diff": (match.get("alt_candidate") or {}).get("mag_diff", ""),
            "query_starttime": q.get("starttime", ""),
            "query_endtime": q.get("endtime", ""),
            "query_latitude": q.get("latitude", ""),
            "query_longitude": q.get("longitude", ""),
            "query_maxradius": q.get("maxradius", ""),
            "query_minmagnitude": q.get("minmagnitude", ""),
            "query_maxmagnitude": q.get("maxmagnitude", ""),
            "match_error": match.get("error", ""),
        }
        rows.append(row)

        by_status[status] += 1
        by_severity[severity] += 1
        by_agency[agency_normalized] += 1
        by_agency_status[(agency_normalized, status)] += 1

    rows.sort(key=lambda r: (r["severity"], r["status"], r["sisbra_origin_time"], r["event_folder"]))

    os.makedirs(os.path.dirname(args.report_csv) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.report_md) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.ambiguous_csv) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(args.no_match_csv) or ".", exist_ok=True)

    fieldnames = list(rows[0].keys())
    with open(args.report_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    with open(args.ambiguous_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows([r for r in rows if r["status"] == "ambiguous"])

    with open(args.no_match_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows([r for r in rows if r["status"] == "no_match"])

    critical_rows = [r for r in rows if r["severity"] == "critical"]
    top_agencies = sorted(by_agency.items(), key=lambda x: (-x[1], x[0]))

    with open(args.report_md, "w", encoding="utf-8") as f:
        f.write("# Non-matched Audit Report\n\n")
        f.write("## Inputs\n")
        f.write(f"- non_matched_root: `{args.non_matched_root}`\n")
        f.write(f"- critical_agency_patterns: `{','.join(critical_patterns)}`\n\n")
        f.write("## Totals\n")
        f.write(f"- events: `{len(rows)}`\n")
        for status, count in sorted(by_status.items()):
            f.write(f"- status_{status}: `{count}`\n")
        for severity, count in sorted(by_severity.items()):
            f.write(f"- severity_{severity}: `{count}`\n")
        f.write(f"- critical_events: `{len(critical_rows)}`\n\n")
        f.write("## Top Agencies\n")
        for agency, count in top_agencies[:20]:
            no_match_count = by_agency_status.get((agency, "no_match"), 0)
            ambiguous_count = by_agency_status.get((agency, "ambiguous"), 0)
            f.write(
                f"- {agency}: total={count} no_match={no_match_count} ambiguous={ambiguous_count}\n"
            )
        f.write("\n")
        f.write("## Outputs\n")
        f.write(f"- report_csv: `{args.report_csv}`\n")
        f.write(f"- ambiguous_csv: `{args.ambiguous_csv}`\n")
        f.write(f"- no_match_csv: `{args.no_match_csv}`\n")

    print(f"non_matched_root={args.non_matched_root}")
    print(f"events={len(rows)}")
    print(f"status_counts={dict(by_status)}")
    print(f"severity_counts={dict(by_severity)}")
    print(f"report_csv={args.report_csv}")
    print(f"report_md={args.report_md}")
    print(f"ambiguous_csv={args.ambiguous_csv}")
    print(f"no_match_csv={args.no_match_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
