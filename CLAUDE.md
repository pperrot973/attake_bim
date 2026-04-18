# API Bâtiment - Contexte projet

## Stack
- Python 3.11+, FastAPI, httpx (async), Pydantic v2

## Sources de données (toutes gratuites, sans clé API)
- **BAN** : https://api-adresse.data.gouv.fr/search/?q={adresse}
- **Cadastre** : https://apicarto.ign.fr/api/cadastre/parcelle
- **Orthophoto** : https://data.geopf.fr/wmts (WMTS, couche ORTHOIMAGERY.ORTHOPHOTOS)
- **Altimétrie** : https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json
- **BDNB** : https://api.bdnb.io/v1/ (Base Données Nationales Bâtiments)
- **RNB** : https://rnb-api.beta.gouv.fr/api/alpha/building/ (Référentiel National Bâtiments)
- **Géorisques** : https://www.georisques.gouv.fr/api/v1/
- **DVF** : https://api.cquest.org/dvf (Demandes de valeur foncière)
- **GPU/PLU** : https://apicarto.ign.fr/api/gpu/ (Géoportail de l'Urbanisme)
- **Open-Meteo** : https://api.open-meteo.com/v1/forecast
- **Hub'Eau** : https://hubeau.eaufrance.fr/api/
- **BRGM** : https://geoservices.brgm.fr/geologie (WMS géologie)
- **OSM/Overpass** : https://overpass-api.de/api/interpreter
- **EDF SEI** : https://opendata.edf-sei.re/ (réseau électrique Guyane/DOM)

## Conventions
- Toutes les requêtes HTTP sont async (httpx.AsyncClient)
- Timeout de 10s par provider, on retourne null si erreur
- Coordonnées en WGS84 (EPSG:4326)
- Contexte principal : Guyane française (EPSG:2972 pour projections locales)
- Les providers retournent None en cas d'erreur (jamais d'exception non gérée)

## Routes principales
- `GET /batiment?adresse=...` — recherche par adresse
- `GET /batiment?lat=...&lon=...` — recherche par coordonnées GPS
- `GET /batiment/{id_rnb}` — recherche par identifiant RNB
- `GET /batiment/orthophoto?lat=...&lon=...&zoom=18` — tuile aérienne base64
- `GET /batiment/cadastre/svg?lat=...&lon=...` — contour parcellaire SVG
- `GET /health` — health check

## Lancer le serveur
```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Tester
```bash
curl "http://localhost:8000/batiment?adresse=1+rue+des+palmistes+Cayenne"
curl "http://localhost:8000/health"
```
