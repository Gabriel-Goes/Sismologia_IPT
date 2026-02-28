#!/usr/bin/env python3
"""
Quick live test against a FDSN endpoint for a single SISBRA-like event.

This does NOT write files. It prints:
- how many candidate events were returned
- basic ranking (dt/dist/mag diff) and resource_id
- pick counts within a max distance (requires station metadata)

Example:
  pyenv exec python scripts/legacy/run_step02_one.py \
    --client-url http://127.0.0.1:28080 \
    --time 2023-12-01T04:12:01Z --lat -18.58 --lon -45.14 --mag 3.1
"""

from __future__ import annotations

import argparse
import math

from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.geodetics import gps2dist_azimuth


def dist_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return gps2dist_azimuth(lat1, lon1, lat2, lon2)[0] / 1000.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--client-url", default="http://127.0.0.1:28080")
    ap.add_argument("--time", required=True, help="Origin time (ISO), e.g. 2023-12-01T04:12:01Z")
    ap.add_argument("--lat", type=float, required=True)
    ap.add_argument("--lon", type=float, required=True)
    ap.add_argument("--mag", type=float, default=None)
    ap.add_argument("--time-window-s", type=float, default=120.0)
    ap.add_argument("--maxradius-deg", type=float, default=1.0)
    ap.add_argument("--mag-pad", type=float, default=0.7)
    ap.add_argument("--max-pick-dist-km", type=float, default=400.0)
    args = ap.parse_args()

    c = Client(args.client_url)
    inv = c.get_stations(level="channel")

    t0 = UTCDateTime(args.time)
    q = dict(
        starttime=t0 - args.time_window_s,
        endtime=t0 + args.time_window_s,
        latitude=args.lat,
        longitude=args.lon,
        maxradius=args.maxradius_deg,
        includearrivals=True,
    )
    if args.mag is not None:
        q["minmagnitude"] = max(0.0, args.mag - args.mag_pad)
        q["maxmagnitude"] = args.mag + args.mag_pad

    print("client:", args.client_url)
    print("query:", {k: str(v) for k, v in q.items()})
    cat = c.get_events(**q)
    print("candidates:", len(cat.events))

    scored = []
    for ev in cat.events:
        o = ev.preferred_origin() or (ev.origins[0] if ev.origins else None)
        if o is None:
            continue
        dt_s = abs(o.time - t0)
        d_km = dist_km(args.lat, args.lon, o.latitude, o.longitude)

        m = ev.preferred_magnitude() or (ev.magnitudes[0] if ev.magnitudes else None)
        mag_diff = float("inf")
        if args.mag is not None and m is not None and m.mag is not None:
            mag_diff = abs(float(m.mag) - float(args.mag))

        key = (float(dt_s), float(d_km), float(mag_diff))
        scored.append((key, ev))

    scored.sort(key=lambda t: t[0])
    for i, (key, ev) in enumerate(scored[:10], start=1):
        o = ev.preferred_origin() or ev.origins[0]
        m = ev.preferred_magnitude() or (ev.magnitudes[0] if ev.magnitudes else None)
        rid = str(ev.resource_id) if ev.resource_id else ""
        print(
            f"- #{i} key(dt_s,dist_km,mag_diff)={key} origin={o.time} lat={o.latitude:.3f} lon={o.longitude:.3f}"
            f" mag={(m.mag if m else None)} id={rid}"
        )

    if not scored:
        return 0

    best = scored[0][1]
    o = best.preferred_origin() or best.origins[0]
    kept = 0
    total = len(best.picks or [])
    for p in best.picks or []:
        wid = p.waveform_id
        net = getattr(wid, "network_code", "") or ""
        sta = getattr(wid, "station_code", "") or ""
        loc = getattr(wid, "location_code", "") or ""
        cha = getattr(wid, "channel_code", "") or ""
        seed_id = f"{net}.{sta}.{loc}.{cha}"
        try:
            meta = inv.get_channel_metadata(seed_id)
            slat = meta.get("latitude")
            slon = meta.get("longitude")
            if slat is None or slon is None:
                continue
            if dist_km(o.latitude, o.longitude, float(slat), float(slon)) <= args.max_pick_dist_km:
                kept += 1
        except Exception:
            continue

    print("best_pick_total:", total)
    print(f"best_picks_within_{args.max_pick_dist_km}km:", kept)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
