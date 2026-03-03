"""Deterministic MG geographic filtering helpers (point-in-polygon)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from shapely.geometry import Point

KEEP_IN_MG = "KEEP_IN_MG"
DROP_OUTSIDE_MG = "DROP_OUTSIDE_MG"
DROP_NO_VALID_COORDS = "DROP_NO_VALID_COORDS"

CONSISTENT_ST_MG_INSIDE = "CONSISTENT_ST_MG_INSIDE"
CONSISTENT_ST_NOT_MG_OUTSIDE = "CONSISTENT_ST_NOT_MG_OUTSIDE"
INCONSISTENT_ST_MG_OUTSIDE = "INCONSISTENT_ST_MG_OUTSIDE"
INCONSISTENT_ST_NOT_MG_INSIDE = "INCONSISTENT_ST_NOT_MG_INSIDE"
UNKNOWN_ST = "UNKNOWN_ST"
NOT_APPLICABLE_NO_COORDS = "NOT_APPLICABLE_NO_COORDS"

DEFAULT_MG_GPKG_LAYER = "ibge_mg_uf_2024"
FALLBACK_MG_GPKG_LAYER = "ibge_br_ufs_2024"
DEFAULT_MG_GPKG_PATH = "~/geodatabase.gpkg"


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        s = str(value).strip()
        if not s:
            return None
        return float(s)
    except Exception:
        return None


def _normalize_state(value: Any) -> str:
    return str(value or "").strip().upper()


def _safe_union(geometries):
    if hasattr(geometries, "union_all"):
        return geometries.union_all()
    return geometries.unary_union


def _resolve_gpkg_path(mg_polygon_gpkg_path: str | None) -> str | None:
    raw = str(mg_polygon_gpkg_path or "").strip()
    if not raw:
        raw = DEFAULT_MG_GPKG_PATH
    candidate = Path(raw).expanduser()
    if candidate.is_file():
        return str(candidate)
    return None


@lru_cache(maxsize=8)
def _load_mg_polygon_from_gpkg(
    mg_polygon_gpkg_path: str,
    mg_polygon_layer: str,
):
    try:
        import geopandas as gpd
    except Exception as exc:
        raise RuntimeError(
            "Dependencia obrigatoria ausente: geopandas/shapely para leitura do GeoPackage."
        ) from exc

    requested_layer = str(mg_polygon_layer or "").strip()
    layers_to_try: list[str] = []
    if requested_layer:
        layers_to_try.append(requested_layer)
    for fallback in (DEFAULT_MG_GPKG_LAYER, FALLBACK_MG_GPKG_LAYER):
        if fallback not in layers_to_try:
            layers_to_try.append(fallback)

    last_exc: Exception | None = None
    gdf = None
    loaded_layer = ""
    for layer in layers_to_try:
        try:
            candidate = gpd.read_file(mg_polygon_gpkg_path, layer=layer)
        except Exception as exc:
            last_exc = exc
            continue
        if candidate.empty:
            continue
        gdf = candidate
        loaded_layer = layer
        break

    if gdf is None:
        layer_info = requested_layer or f"{DEFAULT_MG_GPKG_LAYER}|{FALLBACK_MG_GPKG_LAYER}"
        if last_exc is not None:
            raise RuntimeError(
                f"Falha ao ler camadas ({layer_info}) no GeoPackage: {mg_polygon_gpkg_path}. "
                f"Erro final: {last_exc}"
            ) from last_exc
        raise RuntimeError(
            f"Nenhuma camada valida encontrada ({layer_info}) no GeoPackage: {mg_polygon_gpkg_path}."
        )

    # When loading the national states layer, keep only MG.
    if "SIGLA_UF" in gdf.columns:
        mg_only = gdf[gdf["SIGLA_UF"].astype(str).str.upper().str.strip() == "MG"]
        if not mg_only.empty:
            gdf = mg_only

    if gdf.empty:
        raise RuntimeError(
            f"Camada {loaded_layer} do GeoPackage nao contem geometria valida para MG."
        )

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4674")
    gdf = gdf.to_crs("EPSG:4326")

    mg_polygon = _safe_union(gdf.geometry)
    if mg_polygon.is_empty:
        raise RuntimeError(
            f"Poligono de MG vazio apos uniao (gpkg={mg_polygon_gpkg_path}, layer={loaded_layer})."
        )
    return mg_polygon


@lru_cache(maxsize=4)
def _load_mg_polygon_from_geobr(mg_polygon_year: int):
    try:
        import geobr
    except Exception as exc:
        raise RuntimeError(
            "Dependencia obrigatoria ausente: geobr. Instale geobr/geopandas/shapely."
        ) from exc

    try:
        gdf = geobr.read_state(code_state="MG", year=int(mg_polygon_year))
    except Exception as exc:
        raise RuntimeError(
            f"Falha ao carregar limite de MG via geobr (year={mg_polygon_year})."
        ) from exc

    if gdf.empty:
        raise RuntimeError(f"geobr retornou geometria vazia para MG (year={mg_polygon_year}).")

    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4674")
    gdf = gdf.to_crs("EPSG:4326")

    mg_polygon = _safe_union(gdf.geometry)
    if mg_polygon.is_empty:
        raise RuntimeError(f"Poligono de MG vazio apos uniao (year={mg_polygon_year}).")
    return mg_polygon


@lru_cache(maxsize=8)
def _load_mg_polygon(
    mg_polygon_year: int,
    mg_polygon_gpkg_path: str,
    mg_polygon_layer: str,
):
    gpkg_path = _resolve_gpkg_path(mg_polygon_gpkg_path)
    errors: list[str] = []
    if gpkg_path:
        try:
            return _load_mg_polygon_from_gpkg(gpkg_path, mg_polygon_layer)
        except Exception as exc:
            errors.append(f"GeoPackage({gpkg_path}): {exc}")
    try:
        return _load_mg_polygon_from_geobr(int(mg_polygon_year))
    except Exception as exc:
        errors.append(f"geobr(year={mg_polygon_year}): {exc}")
        raise RuntimeError(" ; ".join(errors)) from exc


def ensure_mg_polygon_loaded(
    *,
    mg_polygon_year: int = 2020,
    mg_polygon_gpkg_path: str | None = None,
    mg_polygon_layer: str = DEFAULT_MG_GPKG_LAYER,
) -> None:
    _load_mg_polygon(
        int(mg_polygon_year),
        str(mg_polygon_gpkg_path or ""),
        str(mg_polygon_layer or ""),
    )


def classify_st_geo(
    *,
    state_value: Any,
    state_target: str,
    has_valid_latlon: bool,
    inside_mg_polygon: bool,
) -> str:
    if not has_valid_latlon:
        return NOT_APPLICABLE_NO_COORDS

    st = _normalize_state(state_value)
    target = _normalize_state(state_target)
    if not st:
        return UNKNOWN_ST
    if st == target and inside_mg_polygon:
        return CONSISTENT_ST_MG_INSIDE
    if st == target and not inside_mg_polygon:
        return INCONSISTENT_ST_MG_OUTSIDE
    if st != target and inside_mg_polygon:
        return INCONSISTENT_ST_NOT_MG_INSIDE
    return CONSISTENT_ST_NOT_MG_OUTSIDE


def evaluate_mg_filter(
    *,
    latitude: Any,
    longitude: Any,
    state_value: Any = "",
    state_target: str = "MG",
    mg_polygon_year: int = 2020,
    mg_polygon_gpkg_path: str | None = None,
    mg_polygon_layer: str = DEFAULT_MG_GPKG_LAYER,
) -> dict[str, Any]:
    lat = _safe_float(latitude)
    lon = _safe_float(longitude)
    has_valid_latlon = (
        lat is not None
        and lon is not None
        and -90.0 <= float(lat) <= 90.0
        and -180.0 <= float(lon) <= 180.0
    )

    if not has_valid_latlon:
        inside_mg_polygon = False
        mg_filter_status = DROP_NO_VALID_COORDS
    else:
        mg_polygon = _load_mg_polygon(
            int(mg_polygon_year),
            str(mg_polygon_gpkg_path or ""),
            str(mg_polygon_layer or ""),
        )
        inside_mg_polygon = bool(mg_polygon.intersects(Point(float(lon), float(lat))))
        mg_filter_status = KEEP_IN_MG if inside_mg_polygon else DROP_OUTSIDE_MG

    st_geo_consistency = classify_st_geo(
        state_value=state_value,
        state_target=state_target,
        has_valid_latlon=has_valid_latlon,
        inside_mg_polygon=inside_mg_polygon,
    )

    return {
        "has_valid_latlon": has_valid_latlon,
        "inside_mg_polygon": inside_mg_polygon,
        "mg_filter_status": mg_filter_status,
        "st_geo_consistency": st_geo_consistency,
    }
