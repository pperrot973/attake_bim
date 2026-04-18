"""Demandes de Valeur Foncière (DVF) — transactions immobilières."""
import httpx
from typing import Optional, List
from src.schemas import DvfResult, DvfTransaction
from src.utils import haversine_m

BASE_URL = "https://api.cquest.org/dvf"
TIMEOUT = 10.0


async def get_dvf(lat: float, lon: float, rayon_m: int = 300) -> Optional[DvfResult]:
    params = {"lat": lat, "lon": lon, "dist": rayon_m}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(BASE_URL, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    features = data.get("resultats", data.get("features", []))
    if not features:
        return None

    transactions: List[DvfTransaction] = []
    prix_m2_list: List[float] = []

    for feat in features[:20]:
        props = feat if not feat.get("properties") else feat["properties"]
        surf_bati = _to_float(props.get("surface_reelle_bati"))
        valeur = _to_float(props.get("valeur_fonciere"))

        lat_t = _to_float(props.get("latitude"))
        lon_t = _to_float(props.get("longitude"))
        dist = haversine_m(lat, lon, lat_t, lon_t) if lat_t and lon_t else None

        transactions.append(DvfTransaction(
            date_mutation=props.get("date_mutation"),
            nature_mutation=props.get("nature_mutation"),
            valeur_fonciere=valeur,
            surface_bati=surf_bati,
            surface_terrain=_to_float(props.get("surface_terrain")),
            type_local=props.get("type_local"),
            nb_pieces=props.get("nombre_pieces_principales"),
            distance_m=round(dist, 0) if dist else None,
        ))

        if valeur and surf_bati and surf_bati > 0:
            prix_m2_list.append(valeur / surf_bati)

    prix_moyen = round(sum(prix_m2_list) / len(prix_m2_list), 0) if prix_m2_list else None

    return DvfResult(transactions=transactions, prix_moyen_m2=prix_moyen)


def _to_float(val) -> Optional[float]:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
