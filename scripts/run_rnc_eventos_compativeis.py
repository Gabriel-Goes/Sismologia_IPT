#!/usr/bin/env python3
"""
Run RNC inference over data/eventos_compativeis and persist results in event.json.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Allow imports from src/ without package installation.
_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from seismic_event_discriminator.rnc_adapter import discover_triplets, list_event_dirs
from seismic_event_discriminator.rnc_types import EventPrediction, EventSummary, ModelMeta, PickPrediction


DEFAULT_MODEL_COMMIT = "ffb74a81d0c9c5ece0e6700ec45e11791e4bbbe8"
DEFAULT_MODEL_PATH = "models/rnc/model_2021354T1554.h5"
DEFAULT_EVENTS_CSV = "outputs/rnc_prediction_events.csv"
DEFAULT_PICKS_CSV = "outputs/rnc_prediction_picks.csv"
DEFAULT_ERRORS_CSV = "outputs/rnc_prediction_errors.csv"


EVENT_FIELDS = [
    "event_id",
    "event_dir",
    "status",
    "event_prob_nat",
    "event_prob_ant",
    "event_pred",
    "event_label",
    "picks_total",
    "picks_valid",
    "picks_error",
    "picks_warning",
    "errors_count",
    "message",
]

PICK_FIELDS = [
    "event_id",
    "network",
    "station",
    "location",
    "pick_time_tag",
    "status",
    "prob_nat",
    "prob_ant",
    "pred",
    "label",
    "cft_max",
    "channels",
    "component_paths",
    "merged_path",
    "warning",
    "error",
]

ERROR_FIELDS = [
    "event_id",
    "scope",
    "kind",
    "network",
    "station",
    "location",
    "pick_time_tag",
    "file",
    "message",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json_atomic(path: str, payload: dict[str, Any]) -> None:
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=True, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_csv(path: str, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        if rows:
            w.writerows(rows)


def _existing_prediction_status(event_json_path: str) -> str | None:
    if not os.path.exists(event_json_path):
        return None
    try:
        payload = _load_json(event_json_path)
        summary = ((payload.get("rnc_prediction") or {}).get("summary") or {})
        status = str(summary.get("status") or "")
        return status or None
    except Exception:
        return None


def _process_event(
    *,
    event_dir: str,
    waveforms_subdir: str,
    required_channels: list[str],
    target_hz: float,
    cft_min: float,
    model_path: str,
    model_source_commit: str,
    model_sha256: str,
    dry_run: bool,
) -> dict[str, Any]:
    event_id = os.path.basename(event_dir)
    event_json_path = os.path.join(event_dir, "event.json")
    event_payload = _load_json(event_json_path) if os.path.exists(event_json_path) else {}

    discovery_errors_rows: list[dict[str, Any]] = []
    pick_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []
    prediction_errors: list[str] = []
    predictions: list[PickPrediction] = []

    try:
        triplets, discovery_errors = discover_triplets(
            event_dir=event_dir,
            waveforms_subdir=waveforms_subdir,
            required_channels=required_channels,
        )
    except Exception as e:
        msg = f"failed to discover triplets: {e}"
        row = {
            "event_id": event_id,
            "event_dir": event_dir,
            "status": "error",
            "event_prob_nat": None,
            "event_prob_ant": None,
            "event_pred": None,
            "event_label": None,
            "picks_total": 0,
            "picks_valid": 0,
            "picks_error": 1,
            "picks_warning": 0,
            "errors_count": 1,
            "message": msg,
        }
        return {"event_row": row, "pick_rows": [], "error_rows": [{"event_id": event_id, "scope": "event", "kind": "triplet_discovery_failed", "network": "", "station": "", "location": "", "pick_time_tag": "", "file": "", "message": msg}]}

    for err in discovery_errors:
        message = str(err.get("message") or "")
        prediction_errors.append(message)
        row = {
            "event_id": event_id,
            "scope": str(err.get("scope") or "discovery"),
            "kind": str(err.get("kind") or "error"),
            "network": str(err.get("network") or ""),
            "station": str(err.get("station") or ""),
            "location": str(err.get("location") or ""),
            "pick_time_tag": str(err.get("pick_time_tag") or ""),
            "file": str(err.get("file") or ""),
            "message": message,
        }
        discovery_errors_rows.append(row)
    error_rows.extend(discovery_errors_rows)

    # Lazy import keeps --help usable even without ObsPy/TensorFlow installed.
    from seismic_event_discriminator.rnc_infer import InferenceError, predict_spectrogram, preprocess_triplet

    for t in triplets:
        location_norm = "" if t.location == "--" else t.location
        component_paths_rel = {ch: os.path.relpath(p, event_dir) for ch, p in t.component_paths.items()}
        merged_path_rel = os.path.relpath(t.merged_path, event_dir) if t.merged_path else None
        status = "ok"
        warning = None
        error = None
        cft_max = None
        prob_nat = None
        prob_ant = None
        pred = None
        label = None

        try:
            pre = preprocess_triplet(
                component_paths=t.component_paths,
                merged_path=t.merged_path,
                required_channels=required_channels,
                target_hz=target_hz,
                cft_min=cft_min,
            )
            cft_max = pre.cft_max
            if pre.warning:
                status = "warning_low_cft"
                warning = pre.warning
            elif pre.spectrogram is None:
                status = "error_preprocess"
                error = "preprocess returned no spectrogram"
            else:
                prob_nat, prob_ant, pred, label = predict_spectrogram(
                    model_path=model_path,
                    spectrogram=pre.spectrogram,
                )
                status = "ok"
        except (InferenceError, ModuleNotFoundError) as e:
            status = "error_preprocess"
            error = str(e)
        except Exception as e:
            status = "error_inference"
            error = str(e)

        if warning:
            prediction_errors.append(f"{t.network}.{t.station}.{location_norm}.{t.pick_time_tag}: {warning}")
        if error:
            prediction_errors.append(f"{t.network}.{t.station}.{location_norm}.{t.pick_time_tag}: {error}")
            error_rows.append(
                {
                    "event_id": event_id,
                    "scope": "pick",
                    "kind": status,
                    "network": t.network,
                    "station": t.station,
                    "location": location_norm,
                    "pick_time_tag": t.pick_time_tag,
                    "file": "",
                    "message": error,
                }
            )

        pick_prediction = PickPrediction(
            network=t.network,
            station=t.station,
            location=location_norm,
            pick_time_tag=t.pick_time_tag,
            channels=list(required_channels),
            component_paths=component_paths_rel,
            merged_path=merged_path_rel,
            status=status,
            prob_nat=prob_nat,
            prob_ant=prob_ant,
            pred=pred,
            label=label,
            cft_max=cft_max,
            warning=warning,
            error=error,
        )
        predictions.append(pick_prediction)
        pick_rows.append(
            {
                "event_id": event_id,
                "network": t.network,
                "station": t.station,
                "location": location_norm,
                "pick_time_tag": t.pick_time_tag,
                "status": status,
                "prob_nat": prob_nat,
                "prob_ant": prob_ant,
                "pred": pred,
                "label": label,
                "cft_max": cft_max,
                "channels": ",".join(required_channels),
                "component_paths": ";".join(
                    f"{ch}:{component_paths_rel[ch]}" for ch in required_channels if ch in component_paths_rel
                ),
                "merged_path": merged_path_rel,
                "warning": warning,
                "error": error,
            }
        )

    valid = [p for p in predictions if p.status == "ok" and p.prob_nat is not None and p.prob_ant is not None]
    picks_total = len(predictions)
    picks_valid = len(valid)
    picks_error = sum(1 for p in predictions if p.status.startswith("error"))
    picks_warning = sum(1 for p in predictions if p.status.startswith("warning"))

    event_prob_nat = None
    event_prob_ant = None
    event_pred = None
    event_label = None
    if picks_valid > 0:
        event_prob_nat = float(sum(float(p.prob_nat) for p in valid) / picks_valid)
        event_prob_ant = float(sum(float(p.prob_ant) for p in valid) / picks_valid)
        event_pred = 0 if event_prob_nat >= event_prob_ant else 1
        event_label = "Natural" if event_pred == 0 else "Anthropogenic"

    if picks_total == 0:
        status = "error"
    elif picks_valid == 0:
        status = "no_valid_pick"
    elif picks_valid == picks_total and picks_warning == 0 and picks_error == 0 and len(discovery_errors_rows) == 0:
        status = "ok"
    else:
        status = "partial"

    summary = EventSummary(
        status=status,
        event_prob_nat=event_prob_nat,
        event_prob_ant=event_prob_ant,
        event_pred=event_pred,
        event_label=event_label,
        picks_total=picks_total,
        picks_valid=picks_valid,
        picks_error=picks_error,
        picks_warning=picks_warning,
    )

    prediction = EventPrediction(
        schema="seismic_event_discriminator.rnc_prediction.v1",
        generated_at_utc=_utc_now_iso(),
        model=ModelMeta(
            path=model_path,
            source_commit=model_source_commit,
            sha256=model_sha256,
        ),
        params={
            "required_channels": list(required_channels),
            "target_hz": target_hz,
            "cft_min": cft_min,
            "waveforms_subdir": waveforms_subdir,
        },
        summary=summary,
        pick_predictions=predictions,
        errors=prediction_errors,
    )

    if not dry_run:
        event_payload["rnc_prediction"] = prediction.to_dict()
        _write_json_atomic(event_json_path, event_payload)

    message = ""
    if picks_total == 0:
        message = "no complete 3C triplet found"
    elif picks_valid == 0:
        message = "all triplets invalid for inference"

    event_row = {
        "event_id": event_id,
        "event_dir": event_dir,
        "status": status,
        "event_prob_nat": event_prob_nat,
        "event_prob_ant": event_prob_ant,
        "event_pred": event_pred,
        "event_label": event_label,
        "picks_total": picks_total,
        "picks_valid": picks_valid,
        "picks_error": picks_error,
        "picks_warning": picks_warning,
        "errors_count": len(prediction_errors),
        "message": message,
    }
    return {
        "event_row": event_row,
        "pick_rows": pick_rows,
        "error_rows": error_rows,
    }


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Run RNC inference over eventos_compativeis")
    ap.add_argument("--compatible-root", default="data/eventos_compativeis")
    ap.add_argument("--waveforms-subdir", default="waveforms")
    ap.add_argument("--model-path", default=DEFAULT_MODEL_PATH)
    ap.add_argument("--model-source-commit", default=DEFAULT_MODEL_COMMIT)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--limit-events", type=int, default=0, help="0 means all events.")
    ap.add_argument("--sample-random", action="store_true", help="Use random sampling when limit-events > 0.")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--required-channels", default="HHZ,HHN,HHE")
    ap.add_argument("--target-hz", type=float, default=100.0)
    ap.add_argument("--cft-min", type=float, default=1.5)
    ap.add_argument("--skip-existing", action="store_true", default=True)
    ap.add_argument("--no-skip-existing", action="store_false", dest="skip_existing")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--summary-events-csv", default=DEFAULT_EVENTS_CSV)
    ap.add_argument("--summary-picks-csv", default=DEFAULT_PICKS_CSV)
    ap.add_argument("--summary-errors-csv", default=DEFAULT_ERRORS_CSV)
    return ap.parse_args()


def main() -> int:
    args = _parse_args()
    required_channels = [x.strip().upper() for x in str(args.required_channels).split(",") if x.strip()]
    if required_channels != ["HHZ", "HHN", "HHE"]:
        print(f"warning: non-default channel order requested: {required_channels}")
    if not os.path.exists(args.model_path):
        raise SystemExit(f"model file not found: {args.model_path}")

    model_sha256 = _sha256_file(args.model_path)
    event_dirs = list_event_dirs(args.compatible_root)
    if not event_dirs:
        raise SystemExit(f"no event directories found under: {args.compatible_root}")

    if args.limit_events and args.limit_events > 0:
        n = min(args.limit_events, len(event_dirs))
        if args.sample_random:
            rnd = random.Random(args.seed)
            event_dirs = sorted(rnd.sample(event_dirs, k=n), key=os.path.basename)
        else:
            event_dirs = event_dirs[:n]

    process_event_dirs: list[str] = []
    event_rows: list[dict[str, Any]] = []
    skipped_existing = 0
    for d in event_dirs:
        event_id = os.path.basename(d)
        event_json_path = os.path.join(d, "event.json")
        if args.skip_existing:
            existing_status = _existing_prediction_status(event_json_path)
            if existing_status:
                skipped_existing += 1
                event_rows.append(
                    {
                        "event_id": event_id,
                        "event_dir": d,
                        "status": "skipped_existing",
                        "event_prob_nat": None,
                        "event_prob_ant": None,
                        "event_pred": None,
                        "event_label": None,
                        "picks_total": 0,
                        "picks_valid": 0,
                        "picks_error": 0,
                        "picks_warning": 0,
                        "errors_count": 0,
                        "message": f"existing_status={existing_status}",
                    }
                )
                continue
        process_event_dirs.append(d)

    print(f"compatible_root={args.compatible_root}")
    print(f"events_selected={len(event_dirs)}")
    print(f"events_to_process={len(process_event_dirs)}")
    print(f"events_skipped_existing={skipped_existing}")
    print(f"workers={args.workers}")
    print(f"model_path={args.model_path}")
    print(f"model_sha256={model_sha256}")

    pick_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []

    if process_event_dirs:
        if int(args.workers) <= 1:
            for idx, d in enumerate(process_event_dirs, start=1):
                result = _process_event(
                    event_dir=d,
                    waveforms_subdir=args.waveforms_subdir,
                    required_channels=required_channels,
                    target_hz=float(args.target_hz),
                    cft_min=float(args.cft_min),
                    model_path=args.model_path,
                    model_source_commit=args.model_source_commit,
                    model_sha256=model_sha256,
                    dry_run=bool(args.dry_run),
                )
                event_rows.append(result["event_row"])
                pick_rows.extend(result["pick_rows"])
                error_rows.extend(result["error_rows"])
                print(f"[{idx}/{len(process_event_dirs)}] {os.path.basename(d)} -> {result['event_row']['status']}")
        else:
            with concurrent.futures.ProcessPoolExecutor(max_workers=max(1, int(args.workers))) as ex:
                futures = [
                    ex.submit(
                        _process_event,
                        event_dir=d,
                        waveforms_subdir=args.waveforms_subdir,
                        required_channels=required_channels,
                        target_hz=float(args.target_hz),
                        cft_min=float(args.cft_min),
                        model_path=args.model_path,
                        model_source_commit=args.model_source_commit,
                        model_sha256=model_sha256,
                        dry_run=bool(args.dry_run),
                    )
                    for d in process_event_dirs
                ]
                done = 0
                total = len(futures)
                for fut in concurrent.futures.as_completed(futures):
                    done += 1
                    result = fut.result()
                    event_rows.append(result["event_row"])
                    pick_rows.extend(result["pick_rows"])
                    error_rows.extend(result["error_rows"])
                    print(f"[{done}/{total}] {result['event_row']['event_id']} -> {result['event_row']['status']}")

    event_rows.sort(key=lambda r: (r["event_id"], r["status"]))
    pick_rows.sort(key=lambda r: (r["event_id"], r["network"], r["station"], r["pick_time_tag"]))
    error_rows.sort(key=lambda r: (r["event_id"], r["scope"], r["kind"], r["station"], r["pick_time_tag"]))

    _write_csv(args.summary_events_csv, EVENT_FIELDS, event_rows)
    _write_csv(args.summary_picks_csv, PICK_FIELDS, pick_rows)
    _write_csv(args.summary_errors_csv, ERROR_FIELDS, error_rows)

    status_counts: dict[str, int] = {}
    for row in event_rows:
        st = str(row.get("status") or "")
        status_counts[st] = status_counts.get(st, 0) + 1

    print(f"summary_events_csv={args.summary_events_csv}")
    print(f"summary_picks_csv={args.summary_picks_csv}")
    print(f"summary_errors_csv={args.summary_errors_csv}")
    print(f"status_counts={status_counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
