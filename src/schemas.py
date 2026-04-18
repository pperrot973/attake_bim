from pydantic import BaseModel, Field
from typing import Optional, List, Any


class Coordonnees(BaseModel):
    lat: float
    lon: float


class AdresseResult(BaseModel):
    adresse_complete: Optional[str] = None
    numero: Optional[str] = None
    rue: Optional[str] = None
    commune: Optional[str] = None
    code_postal: Optional[str] = None
    code_insee: Optional[str] = None
    departement: Optional[str] = None
    score: Optional[float] = None
    coordonnees: Optional[Coordonnees] = None


class CadastreResult(BaseModel):
    prefixe: Optional[str] = None
    section: Optional[str] = None
    numero: Optional[str] = None
    contenance: Optional[int] = None  # en m²
    idu: Optional[str] = None         # identifiant unique parcelle
    geometry: Optional[Any] = None    # GeoJSON geometry


class OrthophotoResult(BaseModel):
    tuile_base64: Optional[str] = None
    zoom: Optional[int] = None
    tile_x: Optional[int] = None
    tile_y: Optional[int] = None
    url_wmts: Optional[str] = None


class AltimetrieResult(BaseModel):
    altitude: Optional[float] = None  # en mètres NGF
    precision: Optional[str] = None


class BdnbResult(BaseModel):
    id_bdnb: Optional[str] = None
    annee_construction: Optional[int] = None
    usage: Optional[str] = None
    nb_logements: Optional[int] = None
    surface_shon: Optional[float] = None
    dpe_classe: Optional[str] = None
    dpe_conso: Optional[float] = None
    ges_classe: Optional[str] = None
    materiaux_structure: Optional[str] = None
    hauteur: Optional[float] = None


class RnbResult(BaseModel):
    rnb_id: Optional[str] = None
    statut: Optional[str] = None
    geometry: Optional[Any] = None
    adresses: Optional[List[Any]] = None


class RisqueItem(BaseModel):
    type: str
    libelle: str
    presence: bool


class GeorisquesResult(BaseModel):
    commune: Optional[str] = None
    code_insee: Optional[str] = None
    risques: Optional[List[RisqueItem]] = None
    radon_classe: Optional[int] = None
    icpe_proches: Optional[List[Any]] = None
    cavites_proches: Optional[List[Any]] = None


class DvfTransaction(BaseModel):
    date_mutation: Optional[str] = None
    nature_mutation: Optional[str] = None
    valeur_fonciere: Optional[float] = None
    surface_bati: Optional[float] = None
    surface_terrain: Optional[float] = None
    type_local: Optional[str] = None
    nb_pieces: Optional[int] = None
    distance_m: Optional[float] = None


class DvfResult(BaseModel):
    transactions: Optional[List[DvfTransaction]] = None
    prix_moyen_m2: Optional[float] = None


class GpuZonage(BaseModel):
    libelle: Optional[str] = None
    libelong: Optional[str] = None
    typezone: Optional[str] = None
    urlfiche: Optional[str] = None


class GpuResult(BaseModel):
    zonages: Optional[List[GpuZonage]] = None
    prescriptions: Optional[List[Any]] = None
    info_surf: Optional[List[Any]] = None


class MeteoActuelle(BaseModel):
    temperature: Optional[float] = None
    humidite: Optional[int] = None
    vitesse_vent: Optional[float] = None
    precipitation: Optional[float] = None
    code_meteo: Optional[int] = None


class MeteoResult(BaseModel):
    actuelle: Optional[MeteoActuelle] = None
    previsions_7j: Optional[List[Any]] = None
    irradiation_annuelle_kwh_m2: Optional[float] = None


class HubeauResult(BaseModel):
    stations_piezo_proches: Optional[List[Any]] = None
    qualite_eau_commune: Optional[List[Any]] = None
    stations_hydro_proches: Optional[List[Any]] = None


class BrgmResult(BaseModel):
    formation_geologique: Optional[str] = None
    ere: Optional[str] = None
    lithologie: Optional[str] = None


class OsmBatiment(BaseModel):
    osm_id: Optional[int] = None
    name: Optional[str] = None
    levels: Optional[int] = None
    material: Optional[str] = None
    amenity: Optional[str] = None
    geometry: Optional[Any] = None


class OsmResult(BaseModel):
    batiment: Optional[OsmBatiment] = None
    poi_200m: Optional[List[Any]] = None


class EdfSeiResult(BaseModel):
    reseau_disponible: Optional[bool] = None
    tension: Optional[str] = None
    poste_source: Optional[str] = None
    distance_poste_m: Optional[float] = None


class BatimentResponse(BaseModel):
    # Données d'entrée résolues
    adresse: Optional[AdresseResult] = None
    coordonnees: Optional[Coordonnees] = None

    # Données foncières & géographiques
    cadastre: Optional[CadastreResult] = None
    rnb: Optional[RnbResult] = None
    bdnb: Optional[BdnbResult] = None

    # Données visuelles
    orthophoto: Optional[OrthophotoResult] = None

    # Données géophysiques
    altimetrie: Optional[AltimetrieResult] = None
    geologie: Optional[BrgmResult] = None

    # Données réglementaires & risques
    urbanisme: Optional[GpuResult] = None
    georisques: Optional[GeorisquesResult] = None

    # Données de marché
    dvf: Optional[DvfResult] = None

    # Données environnementales
    meteo: Optional[MeteoResult] = None
    eau: Optional[HubeauResult] = None

    # Données OpenStreetMap
    osm: Optional[OsmResult] = None

    # Données réseau énergie
    edf_sei: Optional[EdfSeiResult] = None

    # Métadonnées
    sources_ok: List[str] = Field(default_factory=list)
    sources_erreur: List[str] = Field(default_factory=list)
