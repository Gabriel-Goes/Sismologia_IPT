#!/usr/bin/env python3
"""
Re-check no_match rows from association output against one or more FDSN endpoints.

Purpose:
- Verify whether SISBRA no_match rows from seisArc are found in other FDSN services.
- Produce machine-readable evidence for reporting.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from typing import Iterable

from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNNoDataException, FDSNNoServiceException
from obspy.geodetics import gps2dist_azimuth


def _parse_endpoints(spec: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            name, url = part.split("=", 1)
            out.append((name.strip(), url.strip()))
        else:
            out.append((part, part))
    return out


def _dist_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return gps2dist_azimuth(lat1, lon1, lat2, lon2)[0] / 1000.0


def _best_from_catalog(cat, sisbra_lat: float, sisbra_lon: float, sisbra_time: UTCDateTime, sisbra_mag: float | None):
    scored = []
    for ev in cat.events:
        o = ev.preferred_origin() or (ev.origins[0] if ev.origins else None)
        if o is None:
            continue
        m = ev.preferred_magnitude() or (ev.magnitudes[0] if ev.magnitudes else None)
        dt_s = abs(float(o.time - sisbra_time))
        dist_km = _dist_km(sisbra_lat, sisbra_lon, float(o.latitude), float(o.longitude))
        if sisbra_mag is not None and m is not None and m.mag is not None:
            mag_diff = abs(float(m.mag) - sisbra_mag)
        else:
            mag_diff = float("inf")
        key = (dt_s, dist_km, mag_diff)
        rid = str(ev.resource_id) if ev.resource_id else ""
        scored.append((key, rid, o, m))
    if not scored:
        return None
    scored.sort(key=lambda x: x[0])
    key, rid, o, m = scored[0]
    event_id = rid.split("/")[-1] if "/" in rid else rid
    return {
        "event_id": event_id,
        "resource_id": rid,
        "origin_time": o.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "lat": float(o.latitude),
        "lon": float(o.longitude),
        "depth_km": (float(o.depth) / 1000.0) if o.depth is not None else "",
        "mag": float(m.mag) if (m is not None and m.mag is not None) else "",
        "dt_s": key[0],
        "dist_km": key[1],
        "mag_diff": "" if key[2] == float("inf") else key[2],
        "candidate_count": len(scored),
    }


def _iter_no_match_rows(path: str) -> Iterable[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("match_status") == "no_match":
                yield row


def _query_once(
    *,
    client: Client,
    row: dict,
    time_window_s: float,
    maxradius_deg: float,
    mag_pad: float,
):
    lat = float(row["sisbra_lat"])
    lon = float(row["sisbra_lon"])
    sisbra_mag = float(row["sisbra_mag"]) if row.get("sisbra_mag") not in ("", None) else None
    t0 = UTCDateTime(row["sisbra_time"])
    q = {
        "starttime": t0 - time_window_s,
        "endtime": t0 + time_window_s,
        "latitude": lat,
        "longitude": lon,
        "maxradius": maxradius_deg,
        "includearrivals": True,
    }
    if sisbra_mag is not None:
        q["minmagnitude"] = max(0.0, sisbra_mag - mag_pad)
        q["maxmagnitude"] = sisbra_mag + mag_pad

    try:
        cat = client.get_events(**q)
    except FDSNNoDataException:
        return {"status": "no_data", "query": q}
    except Exception as e:
        return {"status": "error", "error": str(e), "query": q}

    best = _best_from_catalog(cat, lat, lon, t0, sisbra_mag)
    if best is None:
        return {"status": "no_scored", "query": q}
    return {"status": "found", "query": q, "best": best}


def main() -> int:
    ap = argparse.ArgumentParser(description="Check no_match rows against multiple FDSN endpoints.")
    ap.add_argument("--input-csv", default="outputs/sisbra_assoc_random100.csv")
    ap.add_argument(
        "--endpoints",
        default=(
            "seisarc=http://127.0.0.1:28080,"
            "rsbr=http://rsbr.on.br:8081,"
            "seisrequest=http://seisrequest.iag.usp.br"
        ),
        help="Comma-separated name=url list.",
    )
    ap.add_argument("--time-window-s", type=float, default=120.0)
    ap.add_argument("--maxradius-deg", type=float, default=1.0)
    ap.add_argument("--mag-pad", type=float, default=0.7)
    ap.add_argument("--relaxed-time-window-s", type=float, default=600.0)
    ap.add_argument("--relaxed-maxradius-deg", type=float, default=2.0)
    ap.add_argument("--relaxed-mag-pad", type=float, default=1.5)
    ap.add_argument("--skip-relaxed", action="store_true")
    ap.add_argument("--out-csv", default="outputs/no_match_endpoint_check.csv")
    args = ap.parse_args()

    no_rows = list(_iter_no_match_rows(args.input_csv))
    if not no_rows:
        raise SystemExit(f"No no_match rows found in: {args.input_csv}")

    endpoints = _parse_endpoints(args.endpoints)
    if not endpoints:
        raise SystemExit("No endpoints parsed from --endpoints")

    clients: dict[str, Client] = {}
    for name, url in endpoints:
        try:
            clients[name] = Client(url)
            print(f"[ok] endpoint {name} -> {url}")
        except FDSNNoServiceException as e:
            print(f"[skip] endpoint {name} unavailable: {e}")
        except Exception as e:
            print(f"[skip] endpoint {name} init error: {e}")

    if not clients:
        raise SystemExit("No reachable endpoints.")

    out_rows: list[dict] = []
    summary = defaultdict(Counter)

    stages = [("strict", args.time_window_s, args.maxradius_deg, args.mag_pad)]
    if not args.skip_relaxed:
        stages.append(("relaxed", args.relaxed_time_window_s, args.relaxed_maxradius_deg, args.relaxed_mag_pad))

    total = len(no_rows)
    for i, row in enumerate(no_rows, start=1):
        print(f"[{i}/{total}] {row['sisbra_time']} {row['sisbra_localities']} ({row['sisbra_source_comments']})")
        for ep_name, _url in endpoints:
            if ep_name not in clients:
                continue
            c = clients[ep_name]
            for stage_name, tw, rd, mp in stages:
                res = _query_once(client=c, row=row, time_window_s=tw, maxradius_deg=rd, mag_pad=mp)
                status = res["status"]
                summary[(ep_name, stage_name)][status] += 1
                o = {
                    "sample_index": row.get("sample_index", ""),
                    "sisbra_rownum": row.get("sisbra_rownum", ""),
                    "sisbra_time": row.get("sisbra_time", ""),
                    "sisbra_lat": row.get("sisbra_lat", ""),
                    "sisbra_lon": row.get("sisbra_lon", ""),
                    "sisbra_mag": row.get("sisbra_mag", ""),
                    "sisbra_state": row.get("sisbra_state", ""),
                    "sisbra_localities": row.get("sisbra_localities", ""),
                    "sisbra_source_comments": row.get("sisbra_source_comments", ""),
                    "endpoint": ep_name,
                    "stage": stage_name,
                    "status": status,
                    "candidate_count": "",
                    "event_id": "",
                    "origin_time": "",
                    "lat": "",
                    "lon": "",
                    "mag": "",
                    "dt_s": "",
                    "dist_km": "",
                    "mag_diff": "",
                    "error": res.get("error", ""),
                }
                if status == "found":
                    b = res["best"]
                    o.update(
                        {
                            "candidate_count": b["candidate_count"],
                            "event_id": b["event_id"],
                            "origin_time": b["origin_time"],
                            "lat": b["lat"],
                            "lon": b["lon"],
                            "mag": b["mag"],
                            "dt_s": f"{b['dt_s']:.3f}",
                            "dist_km": f"{b['dist_km']:.3f}",
                            "mag_diff": "" if b["mag_diff"] == "" else f"{b['mag_diff']:.3f}",
                        }
                    )
                out_rows.append(o)

    # write CSV
    if out_rows:
        with open(args.out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
            w.writeheader()
            w.writerows(out_rows)
    print(f"wrote: {args.out_csv}")

    print("\nSummary:")
    for (ep, stg), c in sorted(summary.items()):
        print(
            f"- {ep} [{stg}] found={c.get('found',0)} no_data={c.get('no_data',0)} "
            f"no_scored={c.get('no_scored',0)} error={c.get('error',0)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

