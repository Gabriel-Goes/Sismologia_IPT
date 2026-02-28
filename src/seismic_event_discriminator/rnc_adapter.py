"""Adapter from eventos_compativeis waveforms to RNC 3C inputs."""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass
from typing import Any


_MSEED_DOTTED_RE = re.compile(
    r"^(?P<network>[^.]+)\.(?P<station>[^.]+)\.(?P<location>[^.]+)\.(?P<channel>[^_]+)_(?P<pick_time>[^.]+)\.mseed$"
)
_MSEED_SIMPLE_RE = re.compile(
    r"^(?P<network>[^_]+)_(?P<station>[^_]+)_(?P<pick_time>[^.]+)\.mseed$"
)


@dataclass(frozen=True)
class TripletInput:
    """One station-time 3C input consumed by the classifier."""

    network: str
    station: str
    location: str
    pick_time_tag: str
    component_paths: dict[str, str]
    merged_path: str | None = None


def list_event_dirs(compatible_root: str) -> list[str]:
    """List event directories under compatible root."""
    out = [p for p in glob.glob(os.path.join(compatible_root, "*")) if os.path.isdir(p)]
    out.sort(key=os.path.basename)
    return out


def _parse_waveform_name(base: str) -> dict[str, str] | None:
    m = _MSEED_DOTTED_RE.match(base)
    if m:
        return {
            "kind": "dotted",
            "network": m.group("network"),
            "station": m.group("station"),
            "location": m.group("location"),
            "channel": m.group("channel").upper(),
            "pick_time": m.group("pick_time"),
        }
    m = _MSEED_SIMPLE_RE.match(base)
    if m:
        return {
            "kind": "simple",
            "network": m.group("network"),
            "station": m.group("station"),
            "location": "",
            "channel": "",
            "pick_time": m.group("pick_time"),
        }
    return None


def discover_triplets(
    *,
    event_dir: str,
    waveforms_subdir: str,
    required_channels: list[str],
) -> tuple[list[TripletInput], list[dict[str, Any]]]:
    """
    Build 3C groups from:
    - legacy: NET.STA.LOC.CHA_DATETIME.mseed
    - current merged: NET_STA_DATETIME.mseed
    """
    files = sorted(glob.glob(os.path.join(event_dir, waveforms_subdir, "*.mseed")))
    required = [c.upper() for c in required_channels]
    grouped: dict[tuple[str, str, str, str], dict[str, str]] = {}
    merged_candidates: dict[tuple[str, str, str, str], str] = {}
    errors: list[dict[str, Any]] = []

    for fp in files:
        base = os.path.basename(fp)
        meta = _parse_waveform_name(base)
        if not meta:
            errors.append(
                {
                    "scope": "discovery",
                    "kind": "invalid_filename",
                    "file": fp,
                    "message": f"invalid waveform filename: {base}",
                }
            )
            continue
        network = meta["network"]
        station = meta["station"]
        location = meta["location"]
        channel = meta["channel"]
        pick_time_tag = meta["pick_time"]
        key = (network, station, location, pick_time_tag)
        if meta["kind"] == "dotted" and channel in required:
            grouped.setdefault(key, {})[channel] = fp
        else:
            prev = merged_candidates.get(key)
            if prev and prev != fp:
                errors.append(
                    {
                        "scope": "discovery",
                        "kind": "duplicate_merged_candidate",
                        "network": network,
                        "station": station,
                        "location": location,
                        "pick_time_tag": pick_time_tag,
                        "file": fp,
                        "message": f"multiple merged candidates for key: {key}",
                    }
                )
                continue
            merged_candidates[key] = fp

    triplets: list[TripletInput] = []
    keys = set(grouped.keys()) | set(merged_candidates.keys())
    for (network, station, location, pick_time_tag) in sorted(keys):
        channel_map = grouped.get((network, station, location, pick_time_tag), {})
        missing = [ch for ch in required if ch not in channel_map]
        if missing:
            merged_path = merged_candidates.get((network, station, location, pick_time_tag))
            if merged_path:
                triplets.append(
                    TripletInput(
                        network=network,
                        station=station,
                        location=location,
                        pick_time_tag=pick_time_tag,
                        component_paths={},
                        merged_path=merged_path,
                    )
                )
            else:
                errors.append(
                    {
                        "scope": "discovery",
                        "kind": "incomplete_triplet",
                        "network": network,
                        "station": station,
                        "location": location,
                        "pick_time_tag": pick_time_tag,
                        "channels_present": sorted(channel_map.keys()),
                        "channels_missing": missing,
                        "message": f"incomplete triplet, missing channels: {','.join(missing)}",
                    }
                )
                continue
        else:
            triplets.append(
                TripletInput(
                    network=network,
                    station=station,
                    location=location,
                    pick_time_tag=pick_time_tag,
                    component_paths={ch: channel_map[ch] for ch in required},
                    merged_path=None,
                )
            )
    return triplets, errors
