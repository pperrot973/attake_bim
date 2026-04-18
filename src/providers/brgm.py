"""BRGM — formation géologique via WMS GetFeatureInfo."""
import httpx
from typing import Optional
from src.schemas import BrgmResult

WMS_URL = "https://geoservices.brgm.fr/geologie"
TIMEOUT = 10.0


async def get_geologie(lat: float, lon: float) -> Optional[BrgmResult]:
    # GetFeatureInfo sur la couche GEOLOGIE (carte géologique 1/1 000 000)
    bbox_delta = 0.001
    bbox = f"{lon - bbox_delta},{lat - bbox_delta},{lon + bbox_delta},{lat + bbox_delta}"
    width, height = 100, 100
    x, y = 50, 50

    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetFeatureInfo",
        "LAYERS": "GEOLOGIE",
        "QUERY_LAYERS": "GEOLOGIE",
        "BBOX": bbox,
        "WIDTH": width,
        "HEIGHT": height,
        "X": x,
        "Y": y,
        "SRS": "EPSG:4326",
        "INFO_FORMAT": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(WMS_URL, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    features = data.get("features", [])
    if not features:
        return _fallback_text(lat, lon)

    props = features[0].get("properties", {})
    return BrgmResult(
        formation_geologique=props.get("FORMATION") or props.get("formation"),
        ere=props.get("AGE") or props.get("age"),
        lithologie=props.get("LITHOLOGIE") or props.get("lithologie"),
    )


async def _fallback_text(lat: float, lon: float) -> Optional[BrgmResult]:
    """Fallback avec format text/html parsé sommairement."""
    bbox_delta = 0.001
    bbox = f"{lon - bbox_delta},{lat - bbox_delta},{lon + bbox_delta},{lat + bbox_delta}"
    params = {
        "SERVICE": "WMS",
        "VERSION": "1.1.1",
        "REQUEST": "GetFeatureInfo",
        "LAYERS": "GEOLOGIE",
        "QUERY_LAYERS": "GEOLOGIE",
        "BBOX": bbox,
        "WIDTH": 100,
        "HEIGHT": 100,
        "X": 50,
        "Y": 50,
        "SRS": "EPSG:4326",
        "INFO_FORMAT": "text/plain",
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(WMS_URL, params=params)
            r.raise_for_status()
            text = r.text
    except Exception:
        return None

    if not text or "no features" in text.lower():
        return None

    return BrgmResult(formation_geologique=text[:200].strip())
