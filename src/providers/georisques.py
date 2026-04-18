"""Géorisques — risques naturels, radon, ICPE, cavités."""
import httpx
from typing import Optional, List
from src.schemas import GeorisquesResult, RisqueItem

BASE_URL = "https://www.georisques.gouv.fr/api/v1"
TIMEOUT = 10.0


async def get_georisques(lat: float, lon: float, code_insee: Optional[str] = None) -> Optional[GeorisquesResult]:
    risques = await _get_risques(lat, lon)
    radon = await _get_radon(lat, lon)
    icpe = await _get_icpe(lat, lon)
    cavites = await _get_cavites(lat, lon)

    if all(v is None for v in [risques, radon, icpe, cavites]):
        return None

    return GeorisquesResult(
        risques=risques,
        radon_classe=radon,
        icpe_proches=icpe or [],
        cavites_proches=cavites or [],
    )


async def _get_risques(lat: float, lon: float) -> Optional[List[RisqueItem]]:
    params = {"latlon": f"{lon},{lat}", "rayon": 0}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/gaspar/risques", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    items = []
    for risque in data.get("data", []):
        items.append(RisqueItem(
            type=risque.get("code_risque", ""),
            libelle=risque.get("libelle_risque_court", risque.get("libelle_risque", "")),
            presence=True,
        ))
    return items or None


async def _get_radon(lat: float, lon: float) -> Optional[int]:
    params = {"lon": lon, "lat": lat}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/radon", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    items = data.get("data", [])
    if not items:
        return None
    return items[0].get("classe_potentiel")


async def _get_icpe(lat: float, lon: float, rayon: int = 500) -> Optional[List[dict]]:
    params = {"latlon": f"{lon},{lat}", "rayon": rayon, "page": 1, "page_size": 10}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/installations_classees", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    return [
        {
            "nom": i.get("denomination"),
            "statut": i.get("etat_activite"),
            "regime": i.get("regime"),
            "distance_m": i.get("distance"),
        }
        for i in data.get("data", [])
    ] or None


async def _get_cavites(lat: float, lon: float, rayon: int = 500) -> Optional[List[dict]]:
    params = {"latlon": f"{lon},{lat}", "rayon": rayon}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/cavites", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    return [
        {
            "type": c.get("type_cavite"),
            "nom": c.get("nom_cavite"),
            "distance_m": c.get("distance"),
        }
        for c in data.get("data", [])
    ] or None
