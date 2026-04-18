"""Orthophoto IGN via WMTS Géoportail (accès libre depuis 2024)."""
import httpx
import base64
from typing import Optional
from src.schemas import OrthophotoResult
from src.utils import lat_lon_to_tile

WMTS_URL = "https://data.geopf.fr/wmts"
TIMEOUT = 15.0
LAYER = "ORTHOIMAGERY.ORTHOPHOTOS"
TILE_MATRIX_SET = "PM"
FORMAT = "image/jpeg"


def build_wmts_url(x: int, y: int, zoom: int) -> str:
    params = (
        f"SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0"
        f"&LAYER={LAYER}&STYLE=normal&FORMAT={FORMAT}"
        f"&TILEMATRIXSET={TILE_MATRIX_SET}&TILEMATRIX={zoom}"
        f"&TILEROW={y}&TILECOL={x}"
    )
    return f"{WMTS_URL}?{params}"


async def get_orthophoto(lat: float, lon: float, zoom: int = 18) -> Optional[OrthophotoResult]:
    x, y = lat_lon_to_tile(lat, lon, zoom)
    url = build_wmts_url(x, y, zoom)
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(url)
            r.raise_for_status()
            img_bytes = r.content
    except Exception:
        return None

    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return OrthophotoResult(
        tuile_base64=b64,
        zoom=zoom,
        tile_x=x,
        tile_y=y,
        url_wmts=url,
    )
