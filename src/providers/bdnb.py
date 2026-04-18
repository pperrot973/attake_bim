"""Base de Données Nationale des Bâtiments (BDNB)."""
import httpx
from typing import Optional
from src.schemas import BdnbResult

BASE_URL = "https://api.bdnb.io/v1"
TIMEOUT = 10.0


async def get_bdnb(lat: float, lon: float, rayon_m: int = 30) -> Optional[BdnbResult]:
    # Recherche géographique par point + rayon
    params = {
        "point": f"POINT({lon} {lat})",
        "dist": rayon_m,
        "limit": 1,
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/batiment_groupe", params=params)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    items = data if isinstance(data, list) else data.get("results", data.get("items", []))
    if not items:
        return None

    b = items[0]
    return BdnbResult(
        id_bdnb=b.get("batiment_groupe_id") or b.get("id"),
        annee_construction=b.get("annee_construction"),
        usage=b.get("usage_niveau_1_txt") or b.get("usage"),
        nb_logements=b.get("nb_log"),
        surface_shon=b.get("surface_shon"),
        dpe_classe=b.get("dpe_mix_arrete_classe"),
        dpe_conso=b.get("dpe_mix_arrete_conso_ener"),
        ges_classe=b.get("dpe_mix_arrete_classe_ges"),
        materiaux_structure=b.get("materiaux_structure_mur_txt"),
        hauteur=b.get("hauteur_mean"),
    )
