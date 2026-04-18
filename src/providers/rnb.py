"""Référentiel National des Bâtiments (RNB) — beta.gouv.fr."""
import httpx
from typing import Optional
from src.schemas import RnbResult

BASE_URL = "https://rnb-api.beta.gouv.fr/api/alpha"
TIMEOUT = 10.0


async def get_rnb_by_coords(lat: float, lon: float) -> Optional[RnbResult]:
    params = {"lat": lat, "lng": lon, "radius": 30}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/buildings/", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    results = data.get("results", [])
    if not results:
        return None

    b = results[0]
    return _parse_rnb(b)


async def get_rnb_by_id(rnb_id: str) -> Optional[RnbResult]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/buildings/{rnb_id}/")
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    return _parse_rnb(data)


def _parse_rnb(b: dict) -> RnbResult:
    return RnbResult(
        rnb_id=b.get("rnb_id"),
        statut=b.get("status"),
        geometry=b.get("point") or b.get("shape"),
        adresses=b.get("addresses", []),
    )
