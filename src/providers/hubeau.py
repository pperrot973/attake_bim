"""Hub'Eau — eaux souterraines, qualité eau potable, hydrométrie."""
import httpx
from typing import Optional
from src.schemas import HubeauResult

TIMEOUT = 10.0


async def get_hubeau(lat: float, lon: float, code_insee: Optional[str] = None) -> Optional[HubeauResult]:
    piezo = await _get_piezo(lat, lon)
    qualite = await _get_qualite_eau(code_insee) if code_insee else None
    hydro = await _get_hydrologie(lat, lon)

    if piezo is None and qualite is None and hydro is None:
        return None

    return HubeauResult(
        stations_piezo_proches=piezo or [],
        qualite_eau_commune=qualite or [],
        stations_hydro_proches=hydro or [],
    )


async def _get_piezo(lat: float, lon: float, rayon_km: float = 5.0) -> Optional[list]:
    params = {
        "bbox": f"{lon - 0.05},{lat - 0.05},{lon + 0.05},{lat + 0.05}",
        "size": 5,
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(
                "https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/stations",
                params=params,
            )
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    return [
        {
            "code": s.get("code_bss"),
            "nom": s.get("nom_commune"),
            "profondeur_m": s.get("profondeur_investigation"),
            "nature": s.get("nature_station"),
        }
        for s in data.get("data", [])
    ] or None


async def _get_qualite_eau(code_insee: str) -> Optional[list]:
    params = {"code_commune": code_insee, "size": 10}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(
                "https://hubeau.eaufrance.fr/api/v1/qualite_eau_potable/resultats_dis",
                params=params,
            )
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    seen = set()
    result = []
    for m in data.get("data", []):
        param = m.get("libelle_parametre")
        if param and param not in seen:
            seen.add(param)
            result.append({
                "parametre": param,
                "valeur": m.get("resultat_numerique"),
                "unite": m.get("libelle_unite"),
                "conforme": m.get("conclusion_conformite_prelevement"),
                "date": m.get("date_prelevement"),
            })
    return result or None


async def _get_hydrologie(lat: float, lon: float) -> Optional[list]:
    params = {
        "bbox": f"{lon - 0.1},{lat - 0.1},{lon + 0.1},{lat + 0.1}",
        "size": 5,
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(
                "https://hubeau.eaufrance.fr/api/v2/hydrometrie/referentiel/stations",
                params=params,
            )
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    return [
        {
            "code": s.get("code_station"),
            "libelle": s.get("libelle_station"),
            "cours_eau": s.get("libelle_cours_eau"),
        }
        for s in data.get("data", [])
    ] or None
