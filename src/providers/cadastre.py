"""Données cadastrales via l'API Carto IGN."""
import httpx
import json
from typing import Optional
from src.schemas import CadastreResult

BASE_URL = "https://apicarto.ign.fr/api/cadastre"
TIMEOUT = 10.0


async def get_parcelle(lat: float, lon: float) -> Optional[CadastreResult]:
    geom = json.dumps({"type": "Point", "coordinates": [lon, lat]})
    params = {"geom": geom, "_limit": 1}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/parcelle", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    features = data.get("features", [])
    if not features:
        return None

    feat = features[0]
    props = feat.get("properties", {})
    return CadastreResult(
        prefixe=props.get("prefixe"),
        section=props.get("section"),
        numero=props.get("numero"),
        contenance=props.get("contenance"),
        idu=props.get("idu"),
        geometry=feat.get("geometry"),
    )


async def get_parcelle_svg(lat: float, lon: float) -> Optional[str]:
    """Retourne un SVG du contour de la parcelle."""
    parcelle = await get_parcelle(lat, lon)
    if not parcelle or not parcelle.geometry:
        return None

    geom = parcelle.geometry
    if geom.get("type") not in ("Polygon", "MultiPolygon"):
        return None

    rings = []
    if geom["type"] == "Polygon":
        rings = geom["coordinates"]
    else:
        for poly in geom["coordinates"]:
            rings.extend(poly)

    if not rings:
        return None

    coords = rings[0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]

    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    width = max(1.0, max_lon - min_lon)
    height = max(1.0, max_lat - min_lat)

    scale = 500.0 / max(width, height)

    def project(lon_c, lat_c):
        x = (lon_c - min_lon) * scale
        y = (max_lat - lat_c) * scale
        return x, y

    points = " ".join(f"{project(c[0], c[1])[0]:.2f},{project(c[0], c[1])[1]:.2f}" for c in coords)
    svg_w = (max_lon - min_lon) * scale + 20
    svg_h = (max_lat - min_lat) * scale + 20

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w:.0f}" height="{svg_h:.0f}">'
        f'<g transform="translate(10,10)">'
        f'<polygon points="{points}" fill="#f0e8c8" stroke="#8b6914" stroke-width="2"/>'
        f'</g></svg>'
    )
    return svg
