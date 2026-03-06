#!/usr/bin/env python3
"""
Step 02: SISBRA -> match FDSN (live, via ObsPy Client) -> export picks.

Goal:
- Start from SISBRA (static/citable) events.
- For each SISBRA event, query seisArc FDSNWS (via GeoServer tunnel) for candidate events.
- Select the best match (dt/dist/mag) and export:
  - data/YYYYMMDDTHHMMSS/event.xml  (QuakeML of the matched FDSN event)
  - data/YYYYMMDDTHHMMSS/event.json (SISBRA row + match info + picks < max distance)
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
import re
import sys
import threading
from pathlib import Path
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional

from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNNoDataException
from obspy.clients.fdsn.header import FDSNNoServiceException
from obspy.core.event import Catalog, Event
from obspy.geodetics import gps2dist_azimuth

# Allow running as a script without installing the package.
_SRC_DIR = Path(__file__).resolve().parents[1]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from seismic_event_discriminator.step01_catalogo_selecao import SisbraEvent, read_sisbra_csv


_THREAD_LOCAL = threading.local()
STEP03_FILENAME_PATTERN = "NET_STA_DATETIME.mseed"
STEP03_DATETIME_SOURCE = "event_origin_utc"
STEP03_DATETIME_FORMAT = "%Y%jT%H%M%S"


def _utc_iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _utcdatetime_iso(t: UTCDateTime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _json_sanitize(x):
    # Convert common types used in queries/metas to JSON-safe values.
    if isinstance(x, UTCDateTime):
        return _utcdatetime_iso(x)
    if isinstance(x, datetime):
        return _utc_iso(x)
    if isinstance(x, dict):
        return {str(k): _json_sanitize(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_json_sanitize(v) for v in x]
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None
    return x


def _get_thread_client(client_url: str) -> Client:
    # One ObsPy client per worker thread keeps network sessions isolated.
    client = getattr(_THREAD_LOCAL, "client", None)
    current_url = getattr(_THREAD_LOCAL, "client_url", None)
    if client is None or current_url != client_url:
        client = Client(client_url)
        _THREAD_LOCAL.client = client
        _THREAD_LOCAL.client_url = client_url
    return client


def _event_origin(ev: Event):
    o = ev.preferred_origin() or (ev.origins[0] if ev.origins else None)
    if o is None:
        raise ValueError("Event has no origin")
    return o


def _event_mag(ev: Event):
    m = ev.preferred_magnitude() or (ev.magnitudes[0] if ev.magnitudes else None)
    return m


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Use gps2dist_azimuth for accuracy and simplicity.
    dist_m, _az, _baz = gps2dist_azimuth(lat1, lon1, lat2, lon2)
    return dist_m / 1000.0


def _score_candidate(
    *,
    sisbra: SisbraEvent,
    ev: Event,
) -> tuple[tuple[float, float, float], dict]:
    o = _event_origin(ev)
    dt_s = abs((o.time.datetime - sisbra.origin_time).total_seconds())
    dist_km = _haversine_km(sisbra.latitude, sisbra.longitude, o.latitude, o.longitude)

    mag = _event_mag(ev)
    mag_diff = float("nan")
    if sisbra.magnitude is not None and mag is not None and mag.mag is not None:
        mag_diff = abs(float(mag.mag) - float(sisbra.magnitude))

    mag_key = mag_diff if not math.isnan(mag_diff) else float("inf")
    key = (dt_s, dist_km, mag_key)
    meta = {
        "dt_s": dt_s,
        "dist_km": dist_km,
        "mag_diff": None if math.isnan(mag_diff) else mag_diff,
        "fdsn_event_resource_id": str(ev.resource_id) if ev.resource_id else "",
    }
    return key, meta


def _safe_dirname_for_event(ev: Event) -> str:
    o = _event_origin(ev)
    tag = o.time.strftime("%Y%m%dT%H%M%S")

    # Keep the directory stable but avoid collisions when running in batch.
    base = tag
    if ev.resource_id and "/" in str(ev.resource_id):
        tail = str(ev.resource_id).split("/")[-1]
        if tail:
            base = f"{tag}_{tail}"
    return base


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
    if not critical_patterns:
        return False
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


def _target_root_for_status(
    *,
    match_status: str,
    out_root: str,
    non_matched_root: str,
    non_matched_split_status: bool,
) -> str:
    status = str(match_status or "").strip().lower()
    if status == "matched" or not str(non_matched_root or "").strip():
        return out_root
    if non_matched_split_status:
        return os.path.join(non_matched_root, status)
    return non_matched_root


def _extract_picks_json(
    *,
    ev: Event,
    inventory,
    max_dist_km: float,
) -> tuple[list[dict], list[dict]]:
    o = _event_origin(ev)
    picks_ok: list[dict] = []
    picks_skipped: list[dict] = []

    for p in ev.picks or []:
        wid = p.waveform_id
        net = getattr(wid, "network_code", "") or ""
        sta = getattr(wid, "station_code", "") or ""
        loc = getattr(wid, "location_code", "") or ""
        cha = getattr(wid, "channel_code", "") or ""

        seed_id = f"{net}.{sta}.{loc}.{cha}"
        try:
            meta = inventory.get_channel_metadata(seed_id)
            sta_lat = meta.get("latitude")
            sta_lon = meta.get("longitude")
            if sta_lat is None or sta_lon is None:
                raise KeyError("missing lat/lon")
            dist_km = _haversine_km(o.latitude, o.longitude, float(sta_lat), float(sta_lon))
        except Exception as e:
            picks_skipped.append(
                {
                    "seed_id": seed_id,
                    "phase_hint": getattr(p, "phase_hint", None),
                    "time": p.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if getattr(p, "time", None) else None,
                    "reason": f"no_station_metadata: {e}",
                }
            )
            continue

        if dist_km > max_dist_km:
            continue

        picks_ok.append(
            {
                "seed_id": seed_id,
                "network": net,
                "station": sta,
                "location": loc,
                "channel": cha,
                "phase_hint": getattr(p, "phase_hint", None),
                "time": p.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ") if getattr(p, "time", None) else None,
                "station_lat": float(sta_lat),
                "station_lon": float(sta_lon),
                "dist_km": dist_km,
            }
        )

    picks_ok.sort(key=lambda d: (d["time"] or "", d["seed_id"]))
    return picks_ok, picks_skipped


def _write_event_bundle(
    *,
    out_root: str,
    sisbra: SisbraEvent,
    match_status: str,
    match_meta: dict,
    ev: Optional[Event],
    picks_ok: list[dict],
    picks_skipped: list[dict],
    step03_output_mode: str,
    step03_component_channels: list[str],
) -> str:
    os.makedirs(out_root, exist_ok=True)

    if ev is None:
        # Keep datetime-style folder and add rownum for uniqueness on no-match rows.
        tag = f"{sisbra.origin_time.strftime('%Y%m%dT%H%M%S')}_row{sisbra.rownum}"
    else:
        tag = f"{_safe_dirname_for_event(ev)}_row{sisbra.rownum}"

    out_dir = os.path.join(out_root, tag)
    os.makedirs(out_dir, exist_ok=True)

    payload = {
        "schema": "seismic_event_discriminator.event_bundle.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "match_status": match_status,
        "match": match_meta,
        "sisbra": {
            **asdict(sisbra),
            "origin_time": _utc_iso(sisbra.origin_time),
        },
        "fdsn": None,
        "picks": picks_ok,
        "picks_skipped": picks_skipped,
        "waveform_download_contract": {
            "step03_output_mode": step03_output_mode,
            "step03_component_channels": step03_component_channels,
            "step03_filename_pattern": STEP03_FILENAME_PATTERN,
            "step03_datetime_source": STEP03_DATETIME_SOURCE,
            "step03_datetime_format": STEP03_DATETIME_FORMAT,
        },
    }

    if ev is not None:
        o = _event_origin(ev)
        m = _event_mag(ev)
        payload["fdsn"] = {
            "resource_id": str(ev.resource_id) if ev.resource_id else "",
            "origin_time": o.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "latitude": float(o.latitude),
            "longitude": float(o.longitude),
            "depth_m": float(o.depth) if o.depth is not None else None,
            "magnitude": float(m.mag) if (m is not None and m.mag is not None) else None,
            "magnitude_type": getattr(m, "magnitude_type", None) if m is not None else None,
            "agency_id": getattr(getattr(ev, "creation_info", None), "agency_id", None),
        }

        # QuakeML export (one-event catalog).
        xml_path = os.path.join(out_dir, "event.xml")
        Catalog(events=[ev]).write(xml_path, format="QUAKEML")

    json_path = os.path.join(out_dir, "event.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2, sort_keys=True)

    return out_dir


def _process_one_event(
    *,
    sisbra_event: SisbraEvent,
    idx: int,
    total: int,
    client_url: str,
    time_window_s: float,
    maxradius_deg: float,
    mag_pad: float,
    max_pick_dist_km: float,
    out_root: str,
    non_matched_root: str,
    non_matched_split_status: bool,
    critical_agency_patterns: list[str],
    inventory,
    step03_output_mode: str,
    step03_component_channels: list[str],
) -> str:
    s = sisbra_event
    t0 = UTCDateTime(s.origin_time)
    starttime = t0 - time_window_s
    endtime = t0 + time_window_s

    q = {
        "starttime": starttime,
        "endtime": endtime,
        "latitude": s.latitude,
        "longitude": s.longitude,
        "maxradius": maxradius_deg,
        "includearrivals": True,
    }
    if s.magnitude is not None:
        q["minmagnitude"] = max(0.0, float(s.magnitude) - mag_pad)
        q["maxmagnitude"] = float(s.magnitude) + mag_pad

    print(
        f"[{idx}/{total}] SISBRA {s.origin_time.isoformat()} lat={s.latitude:.3f} lon={s.longitude:.3f}"
        f" mag={s.magnitude} window=+/-{time_window_s}s r={maxradius_deg}deg"
    )

    sisbra_agency_tag_raw = _extract_agency_tag(s.source_comments)
    sisbra_agency_tag_normalized = _normalize_agency_tag(sisbra_agency_tag_raw)

    def _bundle_meta(status: str, extra_meta: dict | None = None) -> dict:
        meta = dict(extra_meta or {})
        is_critical = _is_critical_agency(
            sisbra_agency_tag_normalized,
            critical_patterns=critical_agency_patterns,
        )
        meta["sisbra_agency_tag_raw"] = sisbra_agency_tag_raw
        meta["sisbra_agency_tag_normalized"] = sisbra_agency_tag_normalized
        meta["is_critical_agency"] = bool(is_critical)
        meta["severity"] = _severity_for_status(status, is_critical)
        return meta

    try:
        c = _get_thread_client(client_url)
        cat = c.get_events(**q)
    except FDSNNoDataException as e:
        status = "no_match"
        target_root = _target_root_for_status(
            match_status=status,
            out_root=out_root,
            non_matched_root=non_matched_root,
            non_matched_split_status=non_matched_split_status,
        )
        out_dir = _write_event_bundle(
            out_root=target_root,
            sisbra=s,
            match_status=status,
            match_meta=_bundle_meta(status, {"error": f"no_data: {e}", "query": _json_sanitize(q)}),
            ev=None,
            picks_ok=[],
            picks_skipped=[],
            step03_output_mode=step03_output_mode,
            step03_component_channels=step03_component_channels,
        )
        print("NO_MATCH:", _utc_iso(s.origin_time), "->", out_dir)
        return status
    except Exception as e:
        status = "no_match"
        target_root = _target_root_for_status(
            match_status=status,
            out_root=out_root,
            non_matched_root=non_matched_root,
            non_matched_split_status=non_matched_split_status,
        )
        out_dir = _write_event_bundle(
            out_root=target_root,
            sisbra=s,
            match_status=status,
            match_meta=_bundle_meta(status, {"error": f"get_events_failed: {e}", "query": _json_sanitize(q)}),
            ev=None,
            picks_ok=[],
            picks_skipped=[],
            step03_output_mode=step03_output_mode,
            step03_component_channels=step03_component_channels,
        )
        print("NO_MATCH:", _utc_iso(s.origin_time), "->", out_dir)
        return status

    if not cat.events:
        status = "no_match"
        target_root = _target_root_for_status(
            match_status=status,
            out_root=out_root,
            non_matched_root=non_matched_root,
            non_matched_split_status=non_matched_split_status,
        )
        out_dir = _write_event_bundle(
            out_root=target_root,
            sisbra=s,
            match_status=status,
            match_meta=_bundle_meta(status, {"query": _json_sanitize(q), "candidate_count": 0}),
            ev=None,
            picks_ok=[],
            picks_skipped=[],
            step03_output_mode=step03_output_mode,
            step03_component_channels=step03_component_channels,
        )
        print("NO_MATCH:", _utc_iso(s.origin_time), "->", out_dir)
        return status

    scored = []
    for ev in cat.events:
        try:
            key, meta = _score_candidate(sisbra=s, ev=ev)
        except Exception:
            continue
        scored.append((key, meta, ev))
    scored.sort(key=lambda t: t[0])
    print(f"  candidates={len(cat.events)} scored={len(scored)}")

    if not scored:
        status = "no_match"
        target_root = _target_root_for_status(
            match_status=status,
            out_root=out_root,
            non_matched_root=non_matched_root,
            non_matched_split_status=non_matched_split_status,
        )
        out_dir = _write_event_bundle(
            out_root=target_root,
            sisbra=s,
            match_status=status,
            match_meta=_bundle_meta(status, {
                "query": _json_sanitize(q),
                "candidate_count": len(cat.events),
                "error": "no_scored_candidates",
            }),
            ev=None,
            picks_ok=[],
            picks_skipped=[],
            step03_output_mode=step03_output_mode,
            step03_component_channels=step03_component_channels,
        )
        print("NO_MATCH:", _utc_iso(s.origin_time), "->", out_dir)
        return status

    best_key, best_meta, best_ev = scored[0]
    second = scored[1] if len(scored) > 1 else None

    status = "matched"
    if second is not None:
        (dt1, d1, _m1) = best_key
        (dt2, d2, _m2), second_meta, _second_ev = second
        # Mark ambiguous if the runner-up is "too close" to the best match.
        if (dt2 - dt1) <= 2.0 and (d2 - d1) <= 10.0:
            status = "ambiguous"
            best_meta["alt_candidate"] = {
                "dt_s": second_meta["dt_s"],
                "dist_km": second_meta["dist_km"],
                "mag_diff": second_meta["mag_diff"],
                "fdsn_event_resource_id": second_meta["fdsn_event_resource_id"],
            }

    best_meta["query"] = _json_sanitize(q)
    best_meta["candidate_count"] = len(cat.events)
    best_meta["score_key"] = {"dt_s": best_key[0], "dist_km": best_key[1], "mag_key": best_key[2]}
    best_meta = _bundle_meta(status, best_meta)

    picks_ok, picks_skipped = _extract_picks_json(ev=best_ev, inventory=inventory, max_dist_km=max_pick_dist_km)
    print(
        f"  best={best_meta.get('fdsn_event_resource_id','')} dt_s={best_meta['dt_s']:.3f}"
        f" dist_km={best_meta['dist_km']:.3f} picks<={max_pick_dist_km}km={len(picks_ok)}"
    )
    target_root = _target_root_for_status(
        match_status=status,
        out_root=out_root,
        non_matched_root=non_matched_root,
        non_matched_split_status=non_matched_split_status,
    )
    out_dir = _write_event_bundle(
        out_root=target_root,
        sisbra=s,
        match_status=status,
        match_meta=best_meta,
        ev=best_ev,
        picks_ok=picks_ok,
        picks_skipped=picks_skipped,
        step03_output_mode=step03_output_mode,
        step03_component_channels=step03_component_channels,
    )
    print(status.upper() + ":", _utc_iso(s.origin_time), "->", out_dir, f"picks={len(picks_ok)}")
    return status


def main() -> int:
    ap = argparse.ArgumentParser(description="Consulta seisArc (FDSNWS) e exporta picks por evento.")
    ap.add_argument(
        "--sisbra-csv",
        default="outputs/catalogs/sisbra_v2024May09/sisbra_raw_mg_maglt4_depthlt10_yearge2020_v2024May09.csv",
        help="Caminho para o CSV SISBRA preparado pelo pipeline a partir do RAW.",
    )
    ap.add_argument("--min-year", type=int, default=2000, help="Ano mínimo do SISBRA para considerar.")
    ap.add_argument("--n-last", type=int, default=50, help="Número de eventos mais recentes do SISBRA a processar.")
    ap.add_argument("--client-url", default="http://127.0.0.1:28080", help="Base URL do FDSN (seisArc via túnel).")
    ap.add_argument("--time-window-s", type=float, default=120.0, help="Janela de tempo (s) em torno do origin_time SISBRA.")
    ap.add_argument("--maxradius-deg", type=float, default=1.0, help="Raio (graus) em torno da localização SISBRA.")
    ap.add_argument("--mag-pad", type=float, default=0.7, help="Tolerância de magnitude (SISBRA +/- mag-pad).")
    ap.add_argument("--max-pick-dist-km", type=float, default=400.0, help="Distância máxima (km) para reter picks.")
    ap.add_argument("--workers", type=int, default=1, help="Número de workers paralelos para consultas FDSN.")
    ap.add_argument("--out-root", default="data", help="Diretório raiz para bundles matched.")
    ap.add_argument(
        "--non-matched-root",
        default="",
        help="Diretório opcional para bundles non-matched (no_match/ambiguous).",
    )
    ap.add_argument(
        "--non-matched-split-status",
        action="store_true",
        default=True,
        help="Quando --non-matched-root for usado, separar por status em subdirs (default: true).",
    )
    ap.add_argument(
        "--no-non-matched-split-status",
        action="store_false",
        dest="non_matched_split_status",
        help="Quando --non-matched-root for usado, gravar todos os non-matched na mesma pasta.",
    )
    ap.add_argument(
        "--critical-agency-patterns",
        default="IAG,USP,IAG-USP",
        help="Padrões (CSV) para marcar no_match/ambiguous como severidade critical.",
    )
    ap.add_argument(
        "--step03-output-mode",
        default="triplet_single_file",
        choices=["triplet_single_file", "split_component_files"],
        help="Contrato esperado para o Step03 na etapa de download de formas de onda.",
    )
    ap.add_argument(
        "--step03-component-channels",
        default="HHZ,HHN,HHE",
        help="Canais alvo para Step03 (armazenados no event.json como contrato).",
    )

    args = ap.parse_args()
    step03_component_channels = [x.strip().upper() for x in str(args.step03_component_channels).split(",") if x.strip()]
    critical_agency_patterns = [
        _normalize_agency_tag(x) for x in str(args.critical_agency_patterns).split(",") if x.strip()
    ]

    sisbra = read_sisbra_csv(args.sisbra_csv, min_year=args.min_year, require_utc=True)
    if not sisbra:
        raise SystemExit(f"Nenhum evento SISBRA lido de: {args.sisbra_csv}")
    subset = sisbra[-args.n_last :] if args.n_last > 0 else sisbra

    try:
        c = Client(args.client_url)
    except FDSNNoServiceException as e:
        raise SystemExit(
            "Falha ao descobrir servicos FDSN em "
            f"{args.client_url!r}. Verifique o tunel e teste no host:\n"
            f"  curl -sS {args.client_url}/fdsnws/event/1/application.wadl | head\n"
            f"Erro: {e}"
        )
    inventory = c.get_stations(level="channel")

    os.makedirs(args.out_root, exist_ok=True)
    if str(args.non_matched_root or "").strip():
        os.makedirs(args.non_matched_root, exist_ok=True)

    counts: dict[str, int] = {"matched": 0, "no_match": 0, "ambiguous": 0, "error": 0}
    total = len(subset)
    workers = max(1, int(args.workers))
    print(f"Running with workers={workers} events={total}")

    if workers == 1:
        for idx, s in enumerate(subset, start=1):
            status = _process_one_event(
                sisbra_event=s,
                idx=idx,
                total=total,
                client_url=args.client_url,
                time_window_s=args.time_window_s,
                maxradius_deg=args.maxradius_deg,
                mag_pad=args.mag_pad,
                max_pick_dist_km=args.max_pick_dist_km,
                out_root=args.out_root,
                non_matched_root=args.non_matched_root,
                non_matched_split_status=bool(args.non_matched_split_status),
                critical_agency_patterns=critical_agency_patterns,
                inventory=inventory,
                step03_output_mode=args.step03_output_mode,
                step03_component_channels=step03_component_channels,
            )
            counts[status] = counts.get(status, 0) + 1
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            futs = []
            for idx, s in enumerate(subset, start=1):
                fut = ex.submit(
                    _process_one_event,
                    sisbra_event=s,
                    idx=idx,
                    total=total,
                    client_url=args.client_url,
                    time_window_s=args.time_window_s,
                    maxradius_deg=args.maxradius_deg,
                    mag_pad=args.mag_pad,
                    max_pick_dist_km=args.max_pick_dist_km,
                    out_root=args.out_root,
                    non_matched_root=args.non_matched_root,
                    non_matched_split_status=bool(args.non_matched_split_status),
                    critical_agency_patterns=critical_agency_patterns,
                    inventory=inventory,
                    step03_output_mode=args.step03_output_mode,
                    step03_component_channels=step03_component_channels,
                )
                futs.append(fut)

            for fut in concurrent.futures.as_completed(futs):
                try:
                    status = fut.result()
                except Exception as e:
                    counts["error"] += 1
                    print(f"ERROR: worker raised exception: {e}")
                    continue
                counts[status] = counts.get(status, 0) + 1

    print("Done. Counts:", counts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
