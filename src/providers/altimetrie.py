"""Altimétrie IGN — RGE ALTI / MNT."""
import httpx
from typing import Optional
from src.schemas import AltimetrieResult

BASE_URL = "https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json"
TIMEOUT = 10.0


async def get_altitude(lat: float, lon: float) -> Optional[AltimetrieResult]:
    params = {"lon": lon, "lat": lat, "resource": "ign_rge_alti_wld", "zonly": "true"}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(BASE_URL, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    elevations = data.get("elevations", [])
    if not elevations:
        return None

    alt = elevations[0].get("z")
    if alt is None or alt == -99999:
        return None

    return AltimetrieResult(
        altitude=round(float(alt), 2),
        precision="RGE ALTI 1m (IGN)",
    )
