"""Géoportail de l'Urbanisme (GPU) — zonage PLU via API Carto IGN."""
import httpx
import json
from typing import Optional
from src.schemas import GpuResult, GpuZonage

BASE_URL = "https://apicarto.ign.fr/api/gpu"
TIMEOUT = 10.0


async def get_urbanisme(lat: float, lon: float) -> Optional[GpuResult]:
    geom = json.dumps({"type": "Point", "coordinates": [lon, lat]})
    params = {"geom": geom}

    zonages = await _get_zonages(params)
    prescriptions = await _get_prescriptions(params)
    info_surf = await _get_info_surf(params)

    if zonages is None and prescriptions is None:
        return None

    return GpuResult(
        zonages=zonages or [],
        prescriptions=prescriptions or [],
        info_surf=info_surf or [],
    )


async def _get_zonages(params: dict) -> Optional[list]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/zone-urba", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    zones = []
    for feat in data.get("features", []):
        p = feat.get("properties", {})
        zones.append(GpuZonage(
            libelle=p.get("libelle"),
            libelong=p.get("libelong"),
            typezone=p.get("typezone"),
            urlfiche=p.get("urlfiche"),
        ))
    return zones or None


async def _get_prescriptions(params: dict) -> Optional[list]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/prescription-surf", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    return [
        {
            "libelle": f.get("properties", {}).get("libelle"),
            "type": f.get("properties", {}).get("typepsc"),
        }
        for f in data.get("features", [])
    ] or None


async def _get_info_surf(params: dict) -> Optional[list]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/info-surf", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    return [
        {
            "libelle": f.get("properties", {}).get("libelle"),
            "txt": f.get("properties", {}).get("txt"),
        }
        for f in data.get("features", [])
    ] or None
