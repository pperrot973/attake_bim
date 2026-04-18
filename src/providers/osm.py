"""OpenStreetMap via l'API Overpass — bâtiment et POI proches."""
import httpx
from typing import Optional
from src.schemas import OsmResult, OsmBatiment

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
TIMEOUT = 15.0


async def get_osm(lat: float, lon: float, rayon_m: int = 200) -> Optional[OsmResult]:
    query = f"""
    [out:json][timeout:10];
    (
      way(around:{rayon_m},{lat},{lon})["building"];
      relation(around:{rayon_m},{lat},{lon})["building"];
    );
    out body geom;
    """
    batiment = await _query_overpass(query)
    batiment_parsed = _parse_building(batiment, lat, lon) if batiment else None

    poi_query = f"""
    [out:json][timeout:10];
    node(around:{rayon_m},{lat},{lon})["amenity"];
    out body;
    """
    poi_data = await _query_overpass(poi_query)
    poi_list = _parse_pois(poi_data) if poi_data else []

    if batiment_parsed is None and not poi_list:
        return None

    return OsmResult(batiment=batiment_parsed, poi_200m=poi_list)


async def _query_overpass(query: str) -> Optional[dict]:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(OVERPASS_URL, data={"data": query})
            r.raise_for_status()
            return r.json()
    except Exception:
        return None


def _parse_building(data: dict, lat: float, lon: float) -> Optional[OsmBatiment]:
    elements = data.get("elements", [])
    if not elements:
        return None

    el = elements[0]
    tags = el.get("tags", {})
    levels = tags.get("building:levels")

    geom = None
    if el.get("type") == "way" and el.get("geometry"):
        coords = [[g["lon"], g["lat"]] for g in el["geometry"]]
        geom = {"type": "Polygon", "coordinates": [coords]}

    return OsmBatiment(
        osm_id=el.get("id"),
        name=tags.get("name"),
        levels=int(levels) if levels and levels.isdigit() else None,
        material=tags.get("building:material"),
        amenity=tags.get("amenity"),
        geometry=geom,
    )


def _parse_pois(data: dict) -> list:
    return [
        {
            "osm_id": el.get("id"),
            "amenity": el.get("tags", {}).get("amenity"),
            "name": el.get("tags", {}).get("name"),
            "lat": el.get("lat"),
            "lon": el.get("lon"),
        }
        for el in data.get("elements", [])
        if el.get("type") == "node"
    ]
