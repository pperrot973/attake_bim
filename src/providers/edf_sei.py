"""EDF SEI Open Data — réseau électrique DOM (Guyane, Réunion, Martinique, Guadeloupe, Mayotte)."""
import httpx
from typing import Optional
from src.schemas import EdfSeiResult
from src.utils import haversine_m

# Endpoint CKAN d'EDF SEI (Open Data réseau de distribution)
BASE_URL = "https://opendata.edf-sei.re/api/3/action"
TIMEOUT = 10.0

# Jeu de données postes sources Guyane (ressource CKAN)
DATASET_POSTES = "postes-source-guyane"


async def get_edf_sei(lat: float, lon: float) -> Optional[EdfSeiResult]:
    """Cherche le poste source le plus proche et infère la disponibilité réseau."""
    postes = await _get_postes_sources()
    if not postes:
        # Fallback : on indique simplement que les données sont indisponibles
        return EdfSeiResult(reseau_disponible=None)

    plus_proche = None
    dist_min = float("inf")
    for p in postes:
        p_lat = _to_float(p.get("latitude") or p.get("lat"))
        p_lon = _to_float(p.get("longitude") or p.get("lon"))
        if p_lat is None or p_lon is None:
            continue
        d = haversine_m(lat, lon, p_lat, p_lon)
        if d < dist_min:
            dist_min = d
            plus_proche = p

    if plus_proche is None:
        return EdfSeiResult(reseau_disponible=None)

    # Considère le réseau disponible si dans 5 km d'un poste source
    disponible = dist_min < 5000

    return EdfSeiResult(
        reseau_disponible=disponible,
        tension=plus_proche.get("tension") or plus_proche.get("tension_hta"),
        poste_source=plus_proche.get("nom") or plus_proche.get("name"),
        distance_poste_m=round(dist_min, 0),
    )


async def _get_postes_sources() -> Optional[list]:
    """Récupère les postes sources depuis le portail Open Data EDF SEI."""
    params = {"id": DATASET_POSTES}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/package_show", params=params)
            r.raise_for_status()
            pkg = r.json()
    except Exception:
        return None

    resources = pkg.get("result", {}).get("resources", [])
    csv_url = next(
        (res["url"] for res in resources if res.get("format", "").upper() in ("CSV", "JSON")),
        None,
    )
    if not csv_url:
        return None

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(csv_url)
            r.raise_for_status()
            if csv_url.endswith(".json") or "json" in r.headers.get("content-type", ""):
                return r.json()
            # Parse CSV minimal
            lines = r.text.strip().splitlines()
            if len(lines) < 2:
                return None
            headers = [h.strip().lower() for h in lines[0].split(";")]
            return [
                dict(zip(headers, [v.strip() for v in line.split(";")]))
                for line in lines[1:]
            ]
    except Exception:
        return None


def _to_float(val) -> Optional[float]:
    try:
        return float(str(val).replace(",", "."))
    except (TypeError, ValueError):
        return None
