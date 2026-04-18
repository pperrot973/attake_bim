"""Météo via Open-Meteo (gratuit, sans clé API)."""
import httpx
from typing import Optional
from src.schemas import MeteoResult, MeteoActuelle

BASE_URL = "https://api.open-meteo.com/v1"
TIMEOUT = 10.0


async def get_meteo(lat: float, lon: float) -> Optional[MeteoResult]:
    # Données actuelles + prévisions 7j + irradiation solaire annuelle
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,shortwave_radiation_sum",
        "timezone": "auto",
        "forecast_days": 7,
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/forecast", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    current_raw = data.get("current", {})
    actuelle = MeteoActuelle(
        temperature=current_raw.get("temperature_2m"),
        humidite=current_raw.get("relative_humidity_2m"),
        vitesse_vent=current_raw.get("wind_speed_10m"),
        precipitation=current_raw.get("precipitation"),
        code_meteo=current_raw.get("weather_code"),
    )

    daily = data.get("daily", {})
    previsions = []
    times = daily.get("time", [])
    for i, t in enumerate(times):
        previsions.append({
            "date": t,
            "t_max": daily.get("temperature_2m_max", [])[i] if i < len(daily.get("temperature_2m_max", [])) else None,
            "t_min": daily.get("temperature_2m_min", [])[i] if i < len(daily.get("temperature_2m_min", [])) else None,
            "pluie_mm": daily.get("precipitation_sum", [])[i] if i < len(daily.get("precipitation_sum", [])) else None,
            "irradiation_kwh_m2": daily.get("shortwave_radiation_sum", [])[i] if i < len(daily.get("shortwave_radiation_sum", [])) else None,
        })

    # Estimation irradiation annuelle via l'API climatologique
    irradiation_annuelle = await _get_irradiation_annuelle(lat, lon)

    return MeteoResult(
        actuelle=actuelle,
        previsions_7j=previsions,
        irradiation_annuelle_kwh_m2=irradiation_annuelle,
    )


async def _get_irradiation_annuelle(lat: float, lon: float) -> Optional[float]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "shortwave_radiation_sum",
        "timezone": "auto",
        "past_days": 365,
        "forecast_days": 0,
    }
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{BASE_URL}/forecast", params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    values = data.get("daily", {}).get("shortwave_radiation_sum", [])
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return round(sum(vals), 0)
