#!/usr/bin/env python3
"""
Re-check matched SISBRA rows with UnB source comments against UnB FDSN endpoint,
and extract P picks within a max epicentral distance.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter

from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNNoDataException, FDSNNoServiceException
from obspy.geodetics import gps2dist_azimuth


def _dist_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return gps2dist_azimuth(lat1, lon1, lat2, lon2)[0] / 1000.0


def _is_unb_source(s: str) -> bool:
    return "unb" in (s or "").lower()


def _score_event(ev, sisbra_time: UTCDateTime, sisbra_lat: float, sisbra_lon: float, sisbra_mag: float | None):
    o = ev.preferred_origin() or (ev.origins[0] if ev.origins else None)
    if o is None:
        return None
    m = ev.preferred_magnitude() or (ev.magnitudes[0] if ev.magnitudes else None)
    dt_s = abs(float(o.time - sisbra_time))
    dist_km = _dist_km(sisbra_lat, sisbra_lon, float(o.latitude), float(o.longitude))
    if sisbra_mag is not None and m is not None and m.mag is not None:
        mag_diff = abs(float(m.mag) - sisbra_mag)
    else:
        mag_diff = float("inf")
    key = (dt_s, dist_km, mag_diff)
    rid = str(ev.resource_id) if ev.resource_id else ""
    event_id = rid.split("/")[-1] if "/" in rid else rid
    return {
        "key": key,
        "event": ev,
        "event_id": event_id,
        "resource_id": rid,
        "origin": o,
        "magnitude": m,
        "dt_s": dt_s,
        "dist_km": dist_km,
        "mag_diff": mag_diff,
    }


def _query_best(
    *,
    client: Client,
    sisbra_time: UTCDateTime,
    sisbra_lat: float,
    sisbra_lon: float,
    sisbra_mag: float | None,
    time_window_s: float,
    maxradius_deg: float,
    mag_pad: float,
):
    q = {
        "starttime": sisbra_time - time_window_s,
        "endtime": sisbra_time + time_window_s,
        "latitude": sisbra_lat,
        "longitude": sisbra_lon,
        "maxradius": maxradius_deg,
        "includearrivals": True,
    }
    if sisbra_mag is not None:
        q["minmagnitude"] = max(0.0, sisbra_mag - mag_pad)
        q["maxmagnitude"] = sisbra_mag + mag_pad

    cat = client.get_events(**q)
    scored = []
    for ev in cat.events:
        s = _score_event(ev, sisbra_time, sisbra_lat, sisbra_lon, sisbra_mag)
        if s is not None:
            scored.append(s)
    scored.sort(key=lambda x: x["key"])
    return q, scored


def _extract_p_picks_within(
    *,
    best_event,
    inventory,
    max_pick_dist_km: float,
):
    o = best_event.preferred_origin() or (best_event.origins[0] if best_event.origins else None)
    if o is None:
        return [], {"picks_total": 0, "picks_p": 0, "picks_meta_ok": 0, "picks_within_400": 0, "picks_meta_missing": 0}

    details = []
    picks_total = 0
    picks_p = 0
    picks_meta_ok = 0
    picks_within = 0
    picks_meta_missing = 0

    for p in best_event.picks or []:
        picks_total += 1
        phase = (getattr(p, "phase_hint", "") or "").upper()
        if not phase.startswith("P"):
            continue
        picks_p += 1

        wid = p.waveform_id
        net = getattr(wid, "network_code", "") or ""
        sta = getattr(wid, "station_code", "") or ""
        loc = getattr(wid, "location_code", "") or ""
        cha = getattr(wid, "channel_code", "") or ""
        seed_id = f"{net}.{sta}.{loc}.{cha}"

        rec = {
            "seed_id": seed_id,
            "phase_hint": phase,
            "pick_time": p.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if getattr(p, "time", None) else "",
            "station_lat": "",
            "station_lon": "",
            "dist_km": "",
            "within_max_dist": "0",
            "meta_error": "",
        }

        try:
            meta = inventory.get_channel_metadata(seed_id)
            slat = meta.get("latitude")
            slon = meta.get("longitude")
            if slat is None or slon is None:
                raise KeyError("missing station lat/lon")
            dist_km = _dist_km(float(o.latitude), float(o.longitude), float(slat), float(slon))
            picks_meta_ok += 1
            rec["station_lat"] = f"{float(slat):.6f}"
            rec["station_lon"] = f"{float(slon):.6f}"
            rec["dist_km"] = f"{dist_km:.3f}"
            if dist_km <= max_pick_dist_km:
                rec["within_max_dist"] = "1"
                picks_within += 1
        except Exception as e:
            picks_meta_missing += 1
            rec["meta_error"] = str(e)

        details.append(rec)

    counts = {
        "picks_total": picks_total,
        "picks_p": picks_p,
        "picks_meta_ok": picks_meta_ok,
        "picks_within_400": picks_within,
        "picks_meta_missing": picks_meta_missing,
    }
    return details, counts


def main() -> int:
    ap = argparse.ArgumentParser(description="Check UnB endpoint for matched rows and extract P picks <= 400 km.")
    ap.add_argument("--input-csv", default="outputs/sisbra_assoc_random100.csv")
    ap.add_argument("--unb-url", default="http://164.41.28.122:5831/fdsnws")
    ap.add_argument("--time-window-s", type=float, default=120.0)
    ap.add_argument("--maxradius-deg", type=float, default=1.0)
    ap.add_argument("--mag-pad", type=float, default=0.7)
    ap.add_argument("--relaxed-time-window-s", type=float, default=600.0)
    ap.add_argument("--relaxed-maxradius-deg", type=float, default=2.0)
    ap.add_argument("--relaxed-mag-pad", type=float, default=1.5)
    ap.add_argument("--no-relaxed", action="store_true")
    ap.add_argument("--max-pick-dist-km", type=float, default=400.0)
    ap.add_argument("--limit", type=int, default=0, help="Optional limit of rows to process (0=all).")
    ap.add_argument("--out-summary", default="outputs/unb_matches_summary.csv")
    ap.add_argument("--out-picks", default="outputs/unb_matches_picks_p_lt400.csv")
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.input_csv, newline="", encoding="utf-8")))
    sel = [
        r
        for r in rows
        if r.get("match_status") in ("matched_confident", "matched_doubtful")
        and _is_unb_source(r.get("sisbra_source_comments", ""))
    ]
    if args.limit and args.limit > 0:
        sel = sel[: args.limit]

    if not sel:
        raise SystemExit("No matched rows with UnB source found in input CSV.")

    raw_url = args.unb_url.rstrip("/")
    candidates = [raw_url]
    if raw_url.endswith("/fdsnws"):
        candidates.append(raw_url[: -len("/fdsnws")])
    else:
        candidates.append(raw_url + "/fdsnws")
    # preserve order but de-dup
    seen = set()
    url_candidates = []
    for u in candidates:
        if u and u not in seen:
            seen.add(u)
            url_candidates.append(u)

    c = None
    last_err = None
    for u in url_candidates:
        try:
            c = Client(u)
            print(f"endpoint_ok={u}")
            break
        except FDSNNoServiceException as e:
            last_err = e
            print(f"endpoint_fail={u} error={e}")
        except Exception as e:
            last_err = e
            print(f"endpoint_fail={u} error={e}")
    if c is None:
        raise SystemExit(f"UnB endpoint unavailable. Last error: {last_err}")

    inventory = c.get_stations(level="channel")

    print(f"selected_rows={len(sel)} unb_url={args.unb_url}")

    summary_rows = []
    pick_rows = []
    counts = Counter()

    for i, r in enumerate(sel, start=1):
        sis_t = UTCDateTime(r["sisbra_time"])
        sis_lat = float(r["sisbra_lat"])
        sis_lon = float(r["sisbra_lon"])
        sis_mag = float(r["sisbra_mag"]) if r.get("sisbra_mag") not in ("", None) else None

        print(f"[{i}/{len(sel)}] {r['sisbra_time']} {r['sisbra_localities']} source={r['sisbra_source_comments']}")

        stage = "strict"
        try:
            q, scored = _query_best(
                client=c,
                sisbra_time=sis_t,
                sisbra_lat=sis_lat,
                sisbra_lon=sis_lon,
                sisbra_mag=sis_mag,
                time_window_s=args.time_window_s,
                maxradius_deg=args.maxradius_deg,
                mag_pad=args.mag_pad,
            )
        except FDSNNoDataException:
            scored = []
            q = {}
        except Exception as e:
            counts["error"] += 1
            summary_rows.append(
                {
                    "sample_index": r.get("sample_index", ""),
                    "sisbra_time": r.get("sisbra_time", ""),
                    "sisbra_localities": r.get("sisbra_localities", ""),
                    "sisbra_source_comments": r.get("sisbra_source_comments", ""),
                    "orig_match_status": r.get("match_status", ""),
                    "orig_fdsn_event_id": r.get("fdsn_event_id", ""),
                    "unb_status": "error",
                    "unb_stage": stage,
                    "unb_event_id": "",
                    "unb_dt_s": "",
                    "unb_dist_km": "",
                    "unb_mag_diff": "",
                    "unb_candidate_count": "",
                    "picks_total": "",
                    "picks_p": "",
                    "picks_meta_ok": "",
                    "picks_within_400": "",
                    "picks_meta_missing": "",
                    "error": str(e),
                }
            )
            print(f"  -> error: {e}")
            continue

        if not scored and not args.no_relaxed:
            stage = "relaxed"
            try:
                q, scored = _query_best(
                    client=c,
                    sisbra_time=sis_t,
                    sisbra_lat=sis_lat,
                    sisbra_lon=sis_lon,
                    sisbra_mag=sis_mag,
                    time_window_s=args.relaxed_time_window_s,
                    maxradius_deg=args.relaxed_maxradius_deg,
                    mag_pad=args.relaxed_mag_pad,
                )
            except FDSNNoDataException:
                scored = []
                q = {}
            except Exception as e:
                counts["error"] += 1
                summary_rows.append(
                    {
                        "sample_index": r.get("sample_index", ""),
                        "sisbra_time": r.get("sisbra_time", ""),
                        "sisbra_localities": r.get("sisbra_localities", ""),
                        "sisbra_source_comments": r.get("sisbra_source_comments", ""),
                        "orig_match_status": r.get("match_status", ""),
                        "orig_fdsn_event_id": r.get("fdsn_event_id", ""),
                        "unb_status": "error",
                        "unb_stage": stage,
                        "unb_event_id": "",
                        "unb_dt_s": "",
                        "unb_dist_km": "",
                        "unb_mag_diff": "",
                        "unb_candidate_count": "",
                        "picks_total": "",
                        "picks_p": "",
                        "picks_meta_ok": "",
                        "picks_within_400": "",
                        "picks_meta_missing": "",
                        "error": str(e),
                    }
                )
                print(f"  -> error (relaxed): {e}")
                continue

        if not scored:
            counts["no_match"] += 1
            summary_rows.append(
                {
                    "sample_index": r.get("sample_index", ""),
                    "sisbra_time": r.get("sisbra_time", ""),
                    "sisbra_localities": r.get("sisbra_localities", ""),
                    "sisbra_source_comments": r.get("sisbra_source_comments", ""),
                    "orig_match_status": r.get("match_status", ""),
                    "orig_fdsn_event_id": r.get("fdsn_event_id", ""),
                    "unb_status": "no_match",
                    "unb_stage": stage,
                    "unb_event_id": "",
                    "unb_dt_s": "",
                    "unb_dist_km": "",
                    "unb_mag_diff": "",
                    "unb_candidate_count": "0",
                    "picks_total": "",
                    "picks_p": "",
                    "picks_meta_ok": "",
                    "picks_within_400": "",
                    "picks_meta_missing": "",
                    "error": "",
                }
            )
            print("  -> no_match")
            continue

        best = scored[0]
        details, pc = _extract_p_picks_within(
            best_event=best["event"],
            inventory=inventory,
            max_pick_dist_km=args.max_pick_dist_km,
        )

        counts["found"] += 1
        print(
            f"  -> found id={best['event_id']} dt={best['dt_s']:.3f}s dist={best['dist_km']:.3f}km "
            f"picksP<=400={pc['picks_within_400']}"
        )

        summary_rows.append(
            {
                "sample_index": r.get("sample_index", ""),
                "sisbra_time": r.get("sisbra_time", ""),
                "sisbra_localities": r.get("sisbra_localities", ""),
                "sisbra_source_comments": r.get("sisbra_source_comments", ""),
                "orig_match_status": r.get("match_status", ""),
                "orig_fdsn_event_id": r.get("fdsn_event_id", ""),
                "unb_status": "found",
                "unb_stage": stage,
                "unb_event_id": best["event_id"],
                "unb_dt_s": f"{best['dt_s']:.3f}",
                "unb_dist_km": f"{best['dist_km']:.3f}",
                "unb_mag_diff": "" if best["mag_diff"] == float("inf") else f"{best['mag_diff']:.3f}",
                "unb_candidate_count": str(len(scored)),
                "picks_total": str(pc["picks_total"]),
                "picks_p": str(pc["picks_p"]),
                "picks_meta_ok": str(pc["picks_meta_ok"]),
                "picks_within_400": str(pc["picks_within_400"]),
                "picks_meta_missing": str(pc["picks_meta_missing"]),
                "error": "",
            }
        )

        for d in details:
            if d["within_max_dist"] != "1":
                continue
            pick_rows.append(
                {
                    "sample_index": r.get("sample_index", ""),
                    "sisbra_time": r.get("sisbra_time", ""),
                    "sisbra_localities": r.get("sisbra_localities", ""),
                    "orig_fdsn_event_id": r.get("fdsn_event_id", ""),
                    "unb_event_id": best["event_id"],
                    "phase_hint": d["phase_hint"],
                    "pick_time": d["pick_time"],
                    "seed_id": d["seed_id"],
                    "station_lat": d["station_lat"],
                    "station_lon": d["station_lon"],
                    "dist_km": d["dist_km"],
                }
            )

    # write summary
    if summary_rows:
        with open(args.out_summary, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
            w.writeheader()
            w.writerows(summary_rows)

    # write picks
    if pick_rows:
        with open(args.out_picks, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(pick_rows[0].keys()))
            w.writeheader()
            w.writerows(pick_rows)
    else:
        # ensure file exists even when empty result
        with open(args.out_picks, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "sample_index",
                    "sisbra_time",
                    "sisbra_localities",
                    "orig_fdsn_event_id",
                    "unb_event_id",
                    "phase_hint",
                    "pick_time",
                    "seed_id",
                    "station_lat",
                    "station_lon",
                    "dist_km",
                ]
            )

    print(f"wrote summary: {args.out_summary}")
    print(f"wrote picks:   {args.out_picks}")
    print(f"counts: {dict(counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
