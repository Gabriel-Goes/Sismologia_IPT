#!/usr/bin/env python3
"""
Teste encapsulado: amostra aleatória de eventos SISBRA e associação com seisArc via FDSNWS.

Saída principal:
- CSV com uma linha por evento SISBRA testado e melhor candidato FDSN (se houver).

Exemplo:
  pyenv exec python scripts/test_assoc_random100.py \
    --client-url http://127.0.0.1:28080 \
    --sample-size 100 \
    --seed 42
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import random
import sys
from datetime import timezone
from pathlib import Path

from obspy import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.clients.fdsn.header import FDSNNoDataException, FDSNNoServiceException
from obspy.geodetics import gps2dist_azimuth

# Allow imports from src/ without installing package.
_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from seismic_event_discriminator.step01_catalogo_selecao import SisbraEvent, read_sisbra_clean_csv


def _utc_iso(dt):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _dist_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    dist_m, _az, _baz = gps2dist_azimuth(lat1, lon1, lat2, lon2)
    return dist_m / 1000.0


def _score_candidate(s: SisbraEvent, ev):
    o = ev.preferred_origin() or (ev.origins[0] if ev.origins else None)
    if o is None:
        return None
    dt_s = abs((o.time.datetime - s.origin_time).total_seconds())
    dist_km = _dist_km(s.latitude, s.longitude, o.latitude, o.longitude)

    m = ev.preferred_magnitude() or (ev.magnitudes[0] if ev.magnitudes else None)
    mag_diff = float("nan")
    if s.magnitude is not None and m is not None and m.mag is not None:
        mag_diff = abs(float(m.mag) - float(s.magnitude))
    mag_key = mag_diff if not math.isnan(mag_diff) else float("inf")
    key = (dt_s, dist_km, mag_key)
    return key, dt_s, dist_km, mag_diff


def _combined_score(
    *,
    dt_s: float,
    dist_km: float,
    mag_diff: float | None,
    norm_time_s: float,
    norm_dist_km: float,
    norm_mag: float,
) -> float:
    # Lower is better.
    # Missing magnitude gets a mild penalty by assuming "1.5 * norm_mag".
    md = (1.5 * norm_mag) if (mag_diff is None or math.isnan(mag_diff)) else mag_diff
    t = dt_s / max(norm_time_s, 1e-9)
    d = dist_km / max(norm_dist_km, 1e-9)
    m = md / max(norm_mag, 1e-9)
    return math.sqrt(t * t + d * d + m * m)


def _write_csv(path: str, rows: list[dict]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    if not rows:
        return
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description="Teste de associação SISBRA->FDSN para N eventos aleatórios.")
    ap.add_argument(
        "--sisbra-csv",
        default="catalogs/sisbra/sisbra_v2024May09/catalogo_CLEAN_v2024May09.csv",
        help="Caminho do catálogo SISBRA CLEAN CSV.",
    )
    ap.add_argument("--client-url", default="http://127.0.0.1:28080", help="Base URL FDSN (seisArc via túnel).")
    ap.add_argument("--sample-size", type=int, default=100, help="Quantidade de eventos aleatórios.")
    ap.add_argument("--seed", type=int, default=42, help="Seed da amostragem aleatória.")
    ap.add_argument("--min-year", type=int, default=2000, help="Ano mínimo SISBRA.")
    ap.add_argument("--time-window-s", type=float, default=120.0, help="Janela temporal (segundos).")
    ap.add_argument("--maxradius-deg", type=float, default=1.0, help="Raio espacial (graus).")
    ap.add_argument("--mag-pad", type=float, default=0.7, help="Tolerância de magnitude (+/-).")
    ap.add_argument(
        "--norm-time-s",
        type=float,
        default=120.0,
        help="Normalização de tempo (s) para score combinado.",
    )
    ap.add_argument(
        "--norm-dist-km",
        type=float,
        default=50.0,
        help="Normalização de distância (km) para score combinado.",
    )
    ap.add_argument(
        "--norm-mag",
        type=float,
        default=0.7,
        help="Normalização de magnitude para score combinado.",
    )
    ap.add_argument(
        "--confident-ratio-min",
        type=float,
        default=1.5,
        help="Mínimo de ratio(top2/top1) para classificar como match confiável.",
    )
    ap.add_argument(
        "--confident-delta-min",
        type=float,
        default=0.3,
        help="Mínimo de delta_score(top2-top1) para classificar como match confiável.",
    )
    ap.add_argument(
        "--ambiguous-ratio-max",
        type=float,
        default=1.2,
        help="Máximo de ratio(top2/top1) para classificar como ambíguo.",
    )
    ap.add_argument(
        "--out-csv",
        default="outputs/sisbra_assoc_random100.csv",
        help="CSV de saída com resultados do teste.",
    )
    args = ap.parse_args()

    sisbra = read_sisbra_clean_csv(args.sisbra_csv, min_year=args.min_year, require_utc=True)
    if not sisbra:
        raise SystemExit(f"Nenhum evento SISBRA lido de: {args.sisbra_csv}")

    k = min(args.sample_size, len(sisbra))
    rnd = random.Random(args.seed)
    sample = rnd.sample(sisbra, k=k)
    sample.sort(key=lambda e: e.origin_time)

    try:
        c = Client(args.client_url)
    except FDSNNoServiceException as e:
        raise SystemExit(
            f"Falha ao descobrir serviços FDSN em {args.client_url!r}. "
            f"Verifique túnel e WADL. Erro: {e}"
        )

    print(f"[assoc-random100] sisbra total={len(sisbra)} sample={len(sample)} seed={args.seed}")
    print(f"[assoc-random100] client={args.client_url}")

    rows: list[dict] = []
    counts = {
        "matched_confident": 0,
        "matched_doubtful": 0,
        "ambiguous": 0,
        "no_match": 0,
        "error": 0,
    }

    for idx, s in enumerate(sample, start=1):
        t0 = UTCDateTime(s.origin_time)
        q = {
            "starttime": t0 - args.time_window_s,
            "endtime": t0 + args.time_window_s,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "maxradius": args.maxradius_deg,
            "includearrivals": True,
        }
        if s.magnitude is not None:
            q["minmagnitude"] = max(0.0, float(s.magnitude) - args.mag_pad)
            q["maxmagnitude"] = float(s.magnitude) + args.mag_pad

        print(
            f"[{idx:03d}/{len(sample)}] {s.origin_time.isoformat()} "
            f"lat={s.latitude:.3f} lon={s.longitude:.3f} mag={s.magnitude}"
        )

        base_row = {
            "sample_index": idx,
            "sisbra_rownum": s.rownum,
            "sisbra_time": _utc_iso(s.origin_time),
            "sisbra_lat": s.latitude,
            "sisbra_lon": s.longitude,
            "sisbra_depth_km": s.depth_km,
            "sisbra_mag": s.magnitude,
            "sisbra_state": s.state,
            "sisbra_localities": s.localities,
            "sisbra_source_comments": s.source_comments,
            "match_status": "",
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
            "top2_event_id": "",
            "top2_dt_s": "",
            "top2_dist_km": "",
            "top2_mag_diff": "",
            "top1_score": "",
            "top2_score": "",
            "delta_score_12": "",
            "ratio_score_21": "",
            "error": "",
        }

        try:
            cat = c.get_events(**q)
        except FDSNNoDataException:
            row = dict(base_row)
            row["match_status"] = "no_match"
            counts["no_match"] += 1
            rows.append(row)
            print("  -> no_match (204 no data)")
            continue
        except Exception as e:
            row = dict(base_row)
            row["match_status"] = "error"
            row["error"] = str(e)
            counts["error"] += 1
            rows.append(row)
            print(f"  -> error: {e}")
            continue

        cands = []
        for ev in cat.events:
            scored = _score_candidate(s, ev)
            if scored is None:
                continue
            key, dt_s, dist_km, mag_diff = scored
            rid = str(ev.resource_id) if ev.resource_id else ""
            o = ev.preferred_origin() or ev.origins[0]
            m = ev.preferred_magnitude() or (ev.magnitudes[0] if ev.magnitudes else None)
            score = _combined_score(
                dt_s=dt_s,
                dist_km=dist_km,
                mag_diff=None if math.isnan(mag_diff) else mag_diff,
                norm_time_s=args.norm_time_s,
                norm_dist_km=args.norm_dist_km,
                norm_mag=args.norm_mag,
            )
            cands.append(
                {
                    "key": key,
                    "score": score,
                    "event_id": rid.split("/")[-1] if "/" in rid else rid,
                    "resource_id": rid,
                    "time": o.time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "lat": float(o.latitude),
                    "lon": float(o.longitude),
                    "depth_km": (float(o.depth) / 1000.0) if o.depth is not None else None,
                    "mag": float(m.mag) if (m is not None and m.mag is not None) else None,
                    "dt_s": dt_s,
                    "dist_km": dist_km,
                    "mag_diff": None if math.isnan(mag_diff) else mag_diff,
                }
            )
        cands.sort(key=lambda x: (x["score"], x["key"]))

        if not cands:
            row = dict(base_row)
            row["match_status"] = "no_match"
            row["candidate_count"] = len(cat.events)
            counts["no_match"] += 1
            rows.append(row)
            print(f"  -> no_match (candidates={len(cat.events)}, scored=0)")
            continue

        best = cands[0]
        status = "matched_confident"
        alt_event_id = ""
        top2 = cands[1] if len(cands) > 1 else None

        delta_score = ""
        ratio_score = ""
        top2_event_id = ""
        top2_dt_s = ""
        top2_dist_km = ""
        top2_mag_diff = ""
        top2_score = ""
        if top2 is not None:
            delta_score_val = top2["score"] - best["score"]
            ratio_score_val = (top2["score"] / best["score"]) if best["score"] > 0 else float("inf")
            delta_score = f"{delta_score_val:.6f}"
            ratio_score = f"{ratio_score_val:.6f}" if math.isfinite(ratio_score_val) else "inf"
            top2_event_id = top2["event_id"]
            top2_dt_s = f"{top2['dt_s']:.3f}"
            top2_dist_km = f"{top2['dist_km']:.3f}"
            top2_mag_diff = "" if top2["mag_diff"] is None else f"{top2['mag_diff']:.3f}"
            top2_score = f"{top2['score']:.6f}"

            # Decision quality based on separation between top1 and top2.
            if ratio_score_val <= args.ambiguous_ratio_max:
                status = "ambiguous"
                alt_event_id = top2["event_id"]
            elif (
                ratio_score_val >= args.confident_ratio_min
                and delta_score_val >= args.confident_delta_min
            ):
                status = "matched_confident"
            else:
                status = "matched_doubtful"

        row = dict(base_row)
        row.update(
            {
                "match_status": status,
                "candidate_count": len(cands),
                "fdsn_event_id": best["event_id"],
                "fdsn_time": best["time"],
                "fdsn_lat": best["lat"],
                "fdsn_lon": best["lon"],
                "fdsn_depth_km": best["depth_km"],
                "fdsn_mag": best["mag"],
                "dt_s": f"{best['dt_s']:.3f}",
                "dist_km": f"{best['dist_km']:.3f}",
                "mag_diff": "" if best["mag_diff"] is None else f"{best['mag_diff']:.3f}",
                "top1_score": f"{best['score']:.6f}",
                "alt_event_id": alt_event_id,
                "top2_event_id": top2_event_id,
                "top2_dt_s": top2_dt_s,
                "top2_dist_km": top2_dist_km,
                "top2_mag_diff": top2_mag_diff,
                "top2_score": top2_score,
                "delta_score_12": delta_score,
                "ratio_score_21": ratio_score,
            }
        )
        rows.append(row)
        counts[status] += 1
        if top2 is None:
            print(
                f"  -> {status} id={best['event_id']} dt={best['dt_s']:.3f}s dist={best['dist_km']:.3f}km "
                f"score={best['score']:.6f} cand={len(cands)}"
            )
        else:
            print(
                f"  -> {status} top1={best['event_id']} score={best['score']:.6f} "
                f"(dt={best['dt_s']:.3f}s dist={best['dist_km']:.3f}km) | "
                f"top2={top2['event_id']} score={top2['score']:.6f} "
                f"(dt={top2['dt_s']:.3f}s dist={top2['dist_km']:.3f}km) | "
                f"delta={float(delta_score):.6f} ratio={ratio_score} cand={len(cands)}"
            )

    _write_csv(args.out_csv, rows)
    print(f"[assoc-random100] wrote: {args.out_csv}")
    print(f"[assoc-random100] counts: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
