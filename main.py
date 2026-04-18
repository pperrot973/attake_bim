"""API Bâtiment — agrégateur de données géographiques sur un bâtiment."""
import asyncio
from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response

from src.schemas import BatimentResponse, Coordonnees
from src.providers import ban, cadastre, orthophoto, altimetrie, bdnb, rnb
from src.providers import georisques, dvf, gpu, meteo, hubeau, brgm, osm, edf_sei

app = FastAPI(
    title="API Bâtiment",
    description=(
        "Agrège des données gratuites sur un bâtiment : cadastre, orthophoto, "
        "altimétrie, BDNB, RNB, géorisques, urbanisme, DVF, météo, géologie, OSM, EDF SEI."
    ),
    version="1.0.0",
)


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/batiment", response_model=BatimentResponse)
async def get_batiment(
    adresse: Optional[str] = Query(None, description="Adresse texte libre"),
    lat: Optional[float] = Query(None, description="Latitude WGS84"),
    lon: Optional[float] = Query(None, description="Longitude WGS84"),
):
    """
    Retourne toutes les données disponibles sur un bâtiment.
    Fournir soit `adresse`, soit `lat` + `lon`.
    """
    if not adresse and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="Fournir 'adresse' ou 'lat'+'lon'.")

    sources_ok: list[str] = []
    sources_erreur: list[str] = []

    # --- 1. Résolution de l'adresse / coordonnées ---
    adresse_result = None
    coords: Optional[Coordonnees] = None

    if adresse:
        adresse_result = await ban.geocoder_adresse(adresse)
        if adresse_result and adresse_result.coordonnees:
            coords = adresse_result.coordonnees
            sources_ok.append("ban")
        else:
            sources_erreur.append("ban")
    else:
        coords = Coordonnees(lat=lat, lon=lon)
        adresse_result = await ban.reverse_geocoder(lat, lon)
        if adresse_result:
            sources_ok.append("ban")
        else:
            sources_erreur.append("ban")

    if coords is None:
        raise HTTPException(status_code=422, detail="Impossible de résoudre les coordonnées.")

    code_insee = adresse_result.code_insee if adresse_result else None
    _lat, _lon = coords.lat, coords.lon

    # --- 2. Appels parallèles à tous les providers ---
    (
        cadastre_result,
        rnb_result,
        bdnb_result,
        orthophoto_result,
        alti_result,
        geo_result,
        urba_result,
        risques_result,
        dvf_result,
        meteo_result,
        eau_result,
        osm_result,
        edf_result,
    ) = await asyncio.gather(
        cadastre.get_parcelle(_lat, _lon),
        rnb.get_rnb_by_coords(_lat, _lon),
        bdnb.get_bdnb(_lat, _lon),
        orthophoto.get_orthophoto(_lat, _lon),
        altimetrie.get_altitude(_lat, _lon),
        brgm.get_geologie(_lat, _lon),
        gpu.get_urbanisme(_lat, _lon),
        georisques.get_georisques(_lat, _lon, code_insee),
        dvf.get_dvf(_lat, _lon),
        meteo.get_meteo(_lat, _lon),
        hubeau.get_hubeau(_lat, _lon, code_insee),
        osm.get_osm(_lat, _lon),
        edf_sei.get_edf_sei(_lat, _lon),
    )

    # --- 3. Suivi des sources ---
    _track("cadastre", cadastre_result, sources_ok, sources_erreur)
    _track("rnb", rnb_result, sources_ok, sources_erreur)
    _track("bdnb", bdnb_result, sources_ok, sources_erreur)
    _track("orthophoto", orthophoto_result, sources_ok, sources_erreur)
    _track("altimetrie", alti_result, sources_ok, sources_erreur)
    _track("brgm", geo_result, sources_ok, sources_erreur)
    _track("gpu", urba_result, sources_ok, sources_erreur)
    _track("georisques", risques_result, sources_ok, sources_erreur)
    _track("dvf", dvf_result, sources_ok, sources_erreur)
    _track("meteo", meteo_result, sources_ok, sources_erreur)
    _track("hubeau", eau_result, sources_ok, sources_erreur)
    _track("osm", osm_result, sources_ok, sources_erreur)
    _track("edf_sei", edf_result, sources_ok, sources_erreur)

    return BatimentResponse(
        adresse=adresse_result,
        coordonnees=coords,
        cadastre=cadastre_result,
        rnb=rnb_result,
        bdnb=bdnb_result,
        orthophoto=orthophoto_result,
        altimetrie=alti_result,
        geologie=geo_result,
        urbanisme=urba_result,
        georisques=risques_result,
        dvf=dvf_result,
        meteo=meteo_result,
        eau=eau_result,
        osm=osm_result,
        edf_sei=edf_result,
        sources_ok=sources_ok,
        sources_erreur=sources_erreur,
    )


@app.get("/batiment/{id_rnb}", response_model=BatimentResponse)
async def get_batiment_by_rnb(id_rnb: str):
    """Recherche par identifiant RNB."""
    rnb_result = await rnb.get_rnb_by_id(id_rnb)
    if not rnb_result:
        raise HTTPException(status_code=404, detail=f"Bâtiment RNB '{id_rnb}' introuvable.")

    geom = rnb_result.geometry
    coords_raw = geom.get("coordinates") if geom else None
    if not coords_raw:
        raise HTTPException(status_code=422, detail="Bâtiment RNB sans coordonnées.")

    lon_r, lat_r = coords_raw[0], coords_raw[1]
    # Déléguer au endpoint principal
    return await get_batiment(lat=lat_r, lon=lon_r)


@app.get("/batiment/orthophoto/tuile")
async def get_orthophoto_tuile(
    lat: float = Query(...),
    lon: float = Query(...),
    zoom: int = Query(18, ge=1, le=20),
):
    """Retourne la tuile orthophoto en JPEG (binaire)."""
    import base64
    result = await orthophoto.get_orthophoto(lat, lon, zoom)
    if not result or not result.tuile_base64:
        raise HTTPException(status_code=503, detail="Tuile orthophoto indisponible.")
    img_bytes = base64.b64decode(result.tuile_base64)
    return Response(content=img_bytes, media_type="image/jpeg")


@app.get("/batiment/cadastre/svg")
async def get_cadastre_svg(
    lat: float = Query(...),
    lon: float = Query(...),
):
    """Retourne le contour de la parcelle cadastrale en SVG."""
    svg = await cadastre.get_parcelle_svg(lat, lon)
    if not svg:
        raise HTTPException(status_code=404, detail="Parcelle cadastrale introuvable.")
    return Response(content=svg, media_type="image/svg+xml")


def _track(name: str, result, ok: list, err: list):
    (ok if result is not None else err).append(name)
