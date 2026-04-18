import math
from typing import Tuple


def lat_lon_to_tile(lat: float, lon: float, zoom: int) -> Tuple[int, int]:
    """Convertit lat/lon en numéro de tuile XYZ (standard OSM/WMTS)."""
    n = 2 ** zoom
    x = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y = int((1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return x, y


def tile_to_bbox(x: int, y: int, zoom: int) -> Tuple[float, float, float, float]:
    """Retourne la bbox (lon_min, lat_min, lon_max, lat_max) d'une tuile."""
    n = 2 ** zoom

    def tile_to_lon(xt):
        return xt / n * 360.0 - 180.0

    def tile_to_lat(yt):
        sinh_val = math.sinh(math.pi * (1 - 2 * yt / n))
        return math.degrees(math.atan(sinh_val))

    lon_min = tile_to_lon(x)
    lon_max = tile_to_lon(x + 1)
    lat_max = tile_to_lat(y)
    lat_min = tile_to_lat(y + 1)
    return lon_min, lat_min, lon_max, lat_max


def bbox_to_wgs84_geojson(lon: float, lat: float, radius_m: float = 50) -> dict:
    """Crée un point GeoJSON WGS84 avec buffer approximatif en degrés."""
    deg_per_m = 1 / 111320.0
    delta = radius_m * deg_per_m
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon - delta, lat - delta],
            [lon + delta, lat - delta],
            [lon + delta, lat + delta],
            [lon - delta, lat + delta],
            [lon - delta, lat - delta],
        ]]
    }


def point_geojson(lon: float, lat: float) -> dict:
    return {"type": "Point", "coordinates": [lon, lat]}


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance en mètres entre deux points WGS84."""
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
