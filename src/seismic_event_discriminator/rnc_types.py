"""Types used by RNC inference integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ModelMeta:
    """Model metadata persisted in event.json."""

    path: str
    source_commit: str
    sha256: str

    def to_dict(self) -> dict[str, str]:
        return {
            "path": self.path,
            "source_commit": self.source_commit,
            "sha256": self.sha256,
        }


@dataclass
class PickPrediction:
    """Prediction and diagnostics for one station-time triplet."""

    network: str
    station: str
    location: str
    pick_time_tag: str
    channels: list[str]
    component_paths: dict[str, str]
    status: str
    merged_path: str | None = None
    prob_nat: float | None = None
    prob_ant: float | None = None
    pred: int | None = None
    label: str | None = None
    cft_max: float | None = None
    warning: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "network": self.network,
            "station": self.station,
            "location": self.location,
            "pick_time_tag": self.pick_time_tag,
            "channels": list(self.channels),
            "component_paths": dict(self.component_paths),
            "merged_path": self.merged_path,
            "status": self.status,
            "prob_nat": self.prob_nat,
            "prob_ant": self.prob_ant,
            "pred": self.pred,
            "label": self.label,
            "cft_max": self.cft_max,
            "warning": self.warning,
            "error": self.error,
        }


@dataclass
class EventSummary:
    """Aggregated prediction for one event."""

    status: str
    event_prob_nat: float | None
    event_prob_ant: float | None
    event_pred: int | None
    event_label: str | None
    picks_total: int
    picks_valid: int
    picks_error: int
    picks_warning: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "event_prob_nat": self.event_prob_nat,
            "event_prob_ant": self.event_prob_ant,
            "event_pred": self.event_pred,
            "event_label": self.event_label,
            "picks_total": self.picks_total,
            "picks_valid": self.picks_valid,
            "picks_error": self.picks_error,
            "picks_warning": self.picks_warning,
        }


@dataclass
class EventPrediction:
    """Complete RNC block persisted inside event.json."""

    schema: str
    generated_at_utc: str
    model: ModelMeta
    params: dict[str, Any]
    summary: EventSummary
    pick_predictions: list[PickPrediction] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "generated_at_utc": self.generated_at_utc,
            "model": self.model.to_dict(),
            "params": dict(self.params),
            "summary": self.summary.to_dict(),
            "pick_predictions": [p.to_dict() for p in self.pick_predictions],
            "errors": list(self.errors),
        }
