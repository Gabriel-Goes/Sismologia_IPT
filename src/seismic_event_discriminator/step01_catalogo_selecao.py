#!/usr/bin/env python3
"""
Etapas 1+2 (início): catalogo + seleção.

Neste arquivo, começamos do jeito mais simples e reproduzível:
- Ler o boletim SISBRA (v2024May09) em CSV (mais estruturado que o .dat).
- Filtrar eventos "modernos" (>= 2000) sem flag "L" (assumimos UTC).
- Pegar os últimos N eventos (por tempo) e associar com um catálogo FDSN
  (builder text / catalogs/query.txt) que contém EventID.

Objetivo prático desta etapa:
Transformar um boletim estático (sem EventID) em uma lista associada a EventID,
para então buscar detalhes (picks, etc) em serviços dinâmicos, quando necessário.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional


@dataclass(frozen=True)
class SisbraEvent:
    rownum: int
    origin_time: datetime
    latitude: float
    longitude: float
    depth_km: Optional[float]
    magnitude: Optional[float]
    state: str
    localities: str
    source_comments: str


@dataclass(frozen=True)
class FdsnEvent:
    event_id: str
    origin_time: datetime
    latitude: float
    longitude: float
    depth_km: Optional[float]
    magnitude: Optional[float]
    author: str
    location_name: str


def _safe_float(s: str) -> Optional[float]:
    try:
        s = s.strip()
        if s == "":
            return None
        return float(s)
    except Exception:
        return None


def _parse_iso_datetime(s: str) -> datetime:
    # query.txt uses ISO timestamps (sometimes with fractional seconds).
    # datetime.fromisoformat handles 1..6 fractional digits (and no trailing Z).
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1]
    return datetime.fromisoformat(s)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Good enough for matching at tens of km scale.
    r = 6371.0088  # mean Earth radius in km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def read_sisbra_clean_csv(path: str, *, min_year: int = 2000, require_utc: bool = True) -> list[SisbraEvent]:
    events: list[SisbraEvent] = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # header is line 1
            year = row.get("year", "").strip()
            if not year.isdigit():
                continue
            year_i = int(year)
            if year_i < min_year:
                continue

            lflag = (row.get("L", "") or "").strip()
            if require_utc and lflag != "":
                # Older entries sometimes have "L" indicating local time or
                # incomplete timestamp. For now, skip them for automation.
                continue

            mm = row.get("mm", "").strip()
            dd = row.get("dd", "").strip()
            hh = row.get("hh", "").strip()
            mi = row.get("min", "").strip()
            ss = (row.get("ss.s", "") or "").strip()
            if not (mm.isdigit() and dd.isdigit() and hh.isdigit() and mi.isdigit()):
                continue

            sec_f = _safe_float(ss)
            if sec_f is None:
                continue
            sec_i = int(sec_f)
            micro = int(round((sec_f - sec_i) * 1_000_000.0))
            # normalize microseconds in case of rounding to 1_000_000
            if micro >= 1_000_000:
                sec_i += 1
                micro -= 1_000_000

            try:
                ot = datetime(
                    year_i,
                    int(mm),
                    int(dd),
                    int(hh),
                    int(mi),
                    sec_i,
                    micro,
                )
            except Exception:
                continue

            lat = _safe_float(row.get("latit", "") or "")
            lon = _safe_float(row.get("longit", "") or "")
            if lat is None or lon is None:
                continue

            depth = _safe_float(row.get("depth", "") or "")
            mag = _safe_float(row.get("mag", "") or "")
            st = (row.get("ST", "") or "").strip()
            loc = (row.get("Localities", "") or "").strip()
            src = (row.get("(source) comments", "") or "").strip()

            events.append(
                SisbraEvent(
                    rownum=i,
                    origin_time=ot,
                    latitude=float(lat),
                    longitude=float(lon),
                    depth_km=depth,
                    magnitude=mag,
                    state=st,
                    localities=loc,
                    source_comments=src,
                )
            )

    events.sort(key=lambda e: e.origin_time)
    return events


def read_fdsn_query_txt(path: str) -> list[FdsnEvent]:
    # query.txt header starts with "#EventID|Time|...".
    with open(path, "r", encoding="utf-8", newline="") as f:
        first = f.readline()
        if not first:
            return []
        header = first.lstrip("#").rstrip("\n")
        cols = header.split("|")

        reader = csv.DictReader(f, fieldnames=cols, delimiter="|")
        events: list[FdsnEvent] = []
        for row in reader:
            event_id = (row.get("EventID", "") or "").strip()
            time_s = (row.get("Time", "") or "").strip()
            if event_id == "" or time_s == "":
                continue

            try:
                ot = _parse_iso_datetime(time_s)
            except Exception:
                continue

            lat = _safe_float(row.get("Latitude", "") or "")
            lon = _safe_float(row.get("Longitude", "") or "")
            if lat is None or lon is None:
                continue

            depth = _safe_float(row.get("Depth/km", "") or "")
            mag = _safe_float(row.get("Magnitude", "") or "")
            author = (row.get("Author", "") or "").strip()
            loc = (row.get("EventLocationName", "") or "").strip()

            events.append(
                FdsnEvent(
                    event_id=event_id,
                    origin_time=ot,
                    latitude=float(lat),
                    longitude=float(lon),
                    depth_km=depth,
                    magnitude=mag,
                    author=author,
                    location_name=loc,
                )
            )

    events.sort(key=lambda e: e.origin_time)
    return events


def _is_nan(x: Optional[float]) -> bool:
    if x is None:
        return True
    return math.isnan(x)


def match_sisbra_to_fdsn(
    sisbra_events: Iterable[SisbraEvent],
    fdsn_events: list[FdsnEvent],
    *,
    time_window_s: float,
    dist_window_km: float,
    relaxed_time_window_s: float,
    relaxed_dist_window_km: float,
) -> list[dict]:
    out_rows: list[dict] = []

    for s in sisbra_events:
        best: Optional[tuple[tuple[float, float, float], FdsnEvent, float, float, float]] = None
        second: Optional[tuple[tuple[float, float, float], FdsnEvent, float, float, float]] = None
        tried_relaxed = False

        def try_match(tw: float, dw: float) -> tuple[Optional[tuple], Optional[tuple], int]:
            nonlocal best, second
            count = 0
            best = None
            second = None
            for q in fdsn_events:
                dt_s = abs((q.origin_time - s.origin_time).total_seconds())
                if dt_s > tw:
                    continue
                dist_km = _haversine_km(s.latitude, s.longitude, q.latitude, q.longitude)
                if dist_km > dw:
                    continue

                mag_diff = float("nan")
                if s.magnitude is not None and q.magnitude is not None:
                    mag_diff = abs(q.magnitude - s.magnitude)

                # Primary sorting: time, then distance, then magnitude difference (if available).
                # If mag_diff is NaN, it will sort last by using +inf.
                mag_key = mag_diff if not math.isnan(mag_diff) else float("inf")
                key = (dt_s, dist_km, mag_key)

                count += 1
                if best is None or key < best[0]:
                    second = best
                    best = (key, q, dt_s, dist_km, mag_diff)
                elif second is None or key < second[0]:
                    second = (key, q, dt_s, dist_km, mag_diff)

            return best, second, count

        best, second, cand_count = try_match(time_window_s, dist_window_km)
        if best is None:
            tried_relaxed = True
            best, second, cand_count = try_match(relaxed_time_window_s, relaxed_dist_window_km)

        status = "no_match"
        if best is not None:
            status = "matched_relaxed" if tried_relaxed else "matched"

        ambiguous = False
        alt_event_id = ""
        if best is not None and second is not None:
            # If the second candidate is very close, mark ambiguous.
            _, _q1, dt1, d1, _ = best
            _, q2, dt2, d2, _ = second
            if (dt2 - dt1) <= 2.0 and (d2 - d1) <= 10.0:
                ambiguous = True
                alt_event_id = q2.event_id

        if ambiguous:
            status = "ambiguous"

        if best is None:
            out_rows.append(
                {
                    "sisbra_rownum": s.rownum,
                    "sisbra_time": s.origin_time.isoformat(),
                    "sisbra_lat": s.latitude,
                    "sisbra_lon": s.longitude,
                    "sisbra_depth_km": s.depth_km,
                    "sisbra_mag": s.magnitude,
                    "sisbra_state": s.state,
                    "sisbra_localities": s.localities,
                    "sisbra_source_comments": s.source_comments,
                    "match_status": status,
                    "candidate_count": 0,
                    "fdsn_event_id": "",
                    "fdsn_time": "",
                    "fdsn_lat": "",
                    "fdsn_lon": "",
                    "fdsn_depth_km": "",
                    "fdsn_mag": "",
                    "dt_s": "",
                    "dist_km": "",
                    "mag_diff": "",
                    "alt_event_id": "",
                }
            )
            continue

        _key, q, dt_s, dist_km, mag_diff = best
        out_rows.append(
            {
                "sisbra_rownum": s.rownum,
                "sisbra_time": s.origin_time.isoformat(),
                "sisbra_lat": s.latitude,
                "sisbra_lon": s.longitude,
                "sisbra_depth_km": s.depth_km,
                "sisbra_mag": s.magnitude,
                "sisbra_state": s.state,
                "sisbra_localities": s.localities,
                "sisbra_source_comments": s.source_comments,
                "match_status": status,
                "candidate_count": cand_count,
                "fdsn_event_id": q.event_id,
                "fdsn_time": q.origin_time.isoformat(),
                "fdsn_lat": q.latitude,
                "fdsn_lon": q.longitude,
                "fdsn_depth_km": q.depth_km,
                "fdsn_mag": q.magnitude,
                "dt_s": f"{dt_s:.3f}",
                "dist_km": f"{dist_km:.3f}",
                "mag_diff": "" if math.isnan(mag_diff) else f"{mag_diff:.3f}",
                "alt_event_id": alt_event_id,
            }
        )

    return out_rows


def _write_csv(path: str, rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if not rows:
        raise ValueError("No rows to write")

    fieldnames = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Associar eventos SISBRA (sem EventID) a eventos FDSN (com EventID) por tempo+distância."
    )
    ap.add_argument(
        "--sisbra-csv",
        default="catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv",
        help="Caminho para o SISBRA CLEAN CSV.",
    )
    ap.add_argument(
        "--fdsn-query",
        default="catalogs/query.txt",
        help="Caminho para o catalogo FDSN (builder text) com EventID.",
    )
    ap.add_argument("--min-year", type=int, default=2000, help="Ano mínimo do SISBRA para considerar.")
    ap.add_argument(
        "--n-last",
        type=int,
        default=100,
        help="Número de eventos mais recentes do SISBRA (por tempo) a associar.",
    )
    ap.add_argument(
        "--out",
        default="outputs/sisbra_to_fdsn_last100.csv",
        help="Arquivo CSV de saída com a associação SISBRA->FDSN.",
    )
    ap.add_argument("--time-window-s", type=float, default=120.0, help="Janela de tempo (s) para match.")
    ap.add_argument("--dist-window-km", type=float, default=50.0, help="Janela de distância (km) para match.")
    ap.add_argument("--relaxed-time-window-s", type=float, default=600.0, help="Janela relaxada de tempo (s).")
    ap.add_argument("--relaxed-dist-window-km", type=float, default=200.0, help="Janela relaxada de distância (km).")

    args = ap.parse_args()

    sisbra_events = read_sisbra_clean_csv(args.sisbra_csv, min_year=args.min_year, require_utc=True)
    if not sisbra_events:
        raise SystemExit(f"Nenhum evento SISBRA lido de: {args.sisbra_csv}")

    fdsn_events = read_fdsn_query_txt(args.fdsn_query)
    if not fdsn_events:
        raise SystemExit(f"Nenhum evento FDSN lido de: {args.fdsn_query}")

    subset = sisbra_events[-args.n_last :] if args.n_last > 0 else sisbra_events
    rows = match_sisbra_to_fdsn(
        subset,
        fdsn_events,
        time_window_s=args.time_window_s,
        dist_window_km=args.dist_window_km,
        relaxed_time_window_s=args.relaxed_time_window_s,
        relaxed_dist_window_km=args.relaxed_dist_window_km,
    )
    _write_csv(args.out, rows)

    # Print a compact summary for quick checks.
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["match_status"]] = counts.get(r["match_status"], 0) + 1
    print("Wrote:", args.out)
    print("SISBRA events:", len(subset))
    print("Match status counts:", dict(sorted(counts.items(), key=lambda kv: kv[0])))

    # show the last 5 associations (most recent events)
    print("Last 5 rows (most recent):")
    for r in rows[-5:]:
        print(
            f"- {r['sisbra_time']}  {r['sisbra_localities']:<24} -> {r['fdsn_event_id'] or 'NO_MATCH'}"
            f"  status={r['match_status']}  dt_s={r['dt_s']}  dist_km={r['dist_km']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
