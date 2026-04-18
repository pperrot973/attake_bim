"""Géocodage via l'API Adresse BAN (Base Adresse Nationale)."""
import httpx
from typing import Optional
from src.schemas import AdresseResult, Coordonnees

BASE_URL = "https://api-adresse.data.gouv.fr"
TIMEOUT = 10.0


async def geocoder_adresse(adresse: str) -> Optional[AdresseResult]:
    params = {"q": adresse, "limit": 1}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/search/", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    features = data.get("features", [])
    if not features:
        return None

    feat = features[0]
    props = feat.get("properties", {})
    coords = feat.get("geometry", {}).get("coordinates", [None, None])

    return AdresseResult(
        adresse_complete=props.get("label"),
        numero=props.get("housenumber"),
        rue=props.get("street") or props.get("name"),
        commune=props.get("city"),
        code_postal=props.get("postcode"),
        code_insee=props.get("citycode"),
        departement=props.get("context", "").split(",")[0].strip() if props.get("context") else None,
        score=props.get("score"),
        coordonnees=Coordonnees(lat=coords[1], lon=coords[0]) if coords[0] else None,
    )


async def reverse_geocoder(lat: float, lon: float) -> Optional[AdresseResult]:
    params = {"lat": lat, "lon": lon}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/reverse/", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    features = data.get("features", [])
    if not features:
        return None

    feat = features[0]
    props = feat.get("properties", {})
    return AdresseResult(
        adresse_complete=props.get("label"),
        numero=props.get("housenumber"),
        rue=props.get("street") or props.get("name"),
        commune=props.get("city"),
        code_postal=props.get("postcode"),
        code_insee=props.get("citycode"),
        departement=props.get("context", "").split(",")[0].strip() if props.get("context") else None,
        score=props.get("score"),
        coordonnees=Coordonnees(lat=lat, lon=lon),
    )
