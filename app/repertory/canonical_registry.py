"""
Canonical Remedy Registry & Nomenclature Normalization Engine (Phase 59 & 61).
Resolves variant homeopathic nomenclature, abbreviations, and botanical synonyms
to deterministic Canonical Remedy Identifiers across 150 standard HPI polychrests (INV-16).
Injects statutory system-level research prototype transparency banner.
"""
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


SYSTEM_STATUS_BANNER: str = (
    "CLINICAL_DECISION_SUPPORT_SYSTEM_LEVEL_2 (CDSS-L2) [RESEARCH & CLINICAL PROTOTYPE] - "
    "MANDATORY HUMAN-IN-THE-LOOP: ALL SIMILLIMUM RECOMMENDATIONS REQUIRE INDEPENDENT "
    "VERIFICATION AND EXPLICIT SIGN-OFF BY A REGISTERED MEDICAL PRACTITIONER (RMP) UNDER NCH ACT 2020."
)


class UnresolvedRemedyException(Exception):
    """Raised when a remedy alias cannot be mapped to any canonical pharmacopoeial entry (INV-16)."""
    def __init__(self, message: str, query: str):
        super().__init__(message)
        self.message = message
        self.query = query


class CanonicalRemedy(BaseModel):
    canonical_id: str
    standard_name: str
    common_name: str
    hpi_official_name: str
    canonical_abbreviation: str
    aliases: List[str] = Field(default_factory=list)
    kingdom: str
    is_schedule_e1: bool = False
    min_safe_potency: str = "Q"


class CanonicalRemedyRegistry:
    """
    Master registry mapping disparate clinical synonyms, abbreviations, and Latin binominals
    to a single authoritative CanonicalRemedy record across 150 HPI remedies (INV-16).
    """

    # Top 150 Classical & Clinical Pharmacopoeial Database
    _REGISTRY: Dict[str, CanonicalRemedy] = {
        "REM-ACON-001": CanonicalRemedy(
            canonical_id="REM-ACON-001",
            standard_name="Aconitum napellus",
            common_name="Monkshood",
            hpi_official_name="Aconitum napellus Linn.",
            canonical_abbreviation="Acon.",
            aliases=['aconite', 'acon', 'aconitum', 'aconitum napellus', 'monkshood', 'wolfsbane'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-BELL-002": CanonicalRemedy(
            canonical_id="REM-BELL-002",
            standard_name="Atropa belladonna",
            common_name="Deadly Nightshade",
            hpi_official_name="Belladonna Linn.",
            canonical_abbreviation="Bell.",
            aliases=['belladonna', 'bell', 'atropa belladonna', 'deadly nightshade'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="2X"
        ),
        "REM-BRY-003": CanonicalRemedy(
            canonical_id="REM-BRY-003",
            standard_name="Bryonia alba",
            common_name="White Bryony",
            hpi_official_name="Bryonia alba Linn.",
            canonical_abbreviation="Bry.",
            aliases=['bryonia', 'bry', 'bryonia alba', 'white bryony'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-NUX-004": CanonicalRemedy(
            canonical_id="REM-NUX-004",
            standard_name="Strychnos nux-vomica",
            common_name="Poison Nut",
            hpi_official_name="Nux vomica Linn.",
            canonical_abbreviation="Nux-v.",
            aliases=['nux vomica', 'nux vom', 'nux-v', 'nux', 'strychnos nux-vomica', 'poison nut'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="2X"
        ),
        "REM-SULPH-005": CanonicalRemedy(
            canonical_id="REM-SULPH-005",
            standard_name="Sulphur",
            common_name="Brimstone",
            hpi_official_name="Sulphur Sublimatum",
            canonical_abbreviation="Sulph.",
            aliases=['sulfur', 'sulphur', 'sulph', 'brimstone', 'sublimed sulphur'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-PHOS-006": CanonicalRemedy(
            canonical_id="REM-PHOS-006",
            standard_name="Phosphorus",
            common_name="Elemental Phosphorus",
            hpi_official_name="Phosphorus",
            canonical_abbreviation="Phos.",
            aliases=['phosphorus', 'phos', 'elemental phosphorus', 'white phosphorus'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-RHUS-007": CanonicalRemedy(
            canonical_id="REM-RHUS-007",
            standard_name="Rhus toxicodendron",
            common_name="Poison Ivy",
            hpi_official_name="Rhus toxicodendron Linn.",
            canonical_abbreviation="Rhus-t.",
            aliases=['rhus tox', 'rhus toxicodendron', 'rhus-t', 'poison ivy', 'toxicodendron radicans'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-APIS-008": CanonicalRemedy(
            canonical_id="REM-APIS-008",
            standard_name="Apis mellifica",
            common_name="Honey Bee",
            hpi_official_name="Apis mellifica",
            canonical_abbreviation="Apis",
            aliases=['apis', 'apis mel', 'apis mellifica', 'honey bee'],
            kingdom="ANIMAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-ARS-009": CanonicalRemedy(
            canonical_id="REM-ARS-009",
            standard_name="Arsenicum album",
            common_name="White Arsenic",
            hpi_official_name="Arsenicum album",
            canonical_abbreviation="Ars.",
            aliases=['arsenic', 'arsenicum', 'arsenicum album', 'ars', 'white arsenic', 'as2o3'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="6X"
        ),
        "REM-CALC-010": CanonicalRemedy(
            canonical_id="REM-CALC-010",
            standard_name="Calcarea carbonica",
            common_name="Middle Layer of Oyster Shell",
            hpi_official_name="Calcarea carbonica ostrearum",
            canonical_abbreviation="Calc.",
            aliases=['calc carb', 'calcarea carb', 'calcarea carbonica', 'calc', 'oyster shell'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-LACH-011": CanonicalRemedy(
            canonical_id="REM-LACH-011",
            standard_name="Lachesis muta",
            common_name="Bushmaster Snake",
            hpi_official_name="Lachesis mutus",
            canonical_abbreviation="Lach.",
            aliases=['lachesis', 'lachesis muta', 'lach', 'bushmaster'],
            kingdom="ANIMAL",
            is_schedule_e1=True,
            min_safe_potency="6C"
        ),
        "REM-LYC-012": CanonicalRemedy(
            canonical_id="REM-LYC-012",
            standard_name="Lycopodium clavatum",
            common_name="Club Moss",
            hpi_official_name="Lycopodium clavatum Linn.",
            canonical_abbreviation="Lyc.",
            aliases=['lycopodium', 'lycopodium clavatum', 'lyc', 'club moss'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-NATM-013": CanonicalRemedy(
            canonical_id="REM-NATM-013",
            standard_name="Natrum muriaticum",
            common_name="Common Salt",
            hpi_official_name="Natrum muriaticum",
            canonical_abbreviation="Nat-m.",
            aliases=['natrum mur', 'natrum muriaticum', 'nat-m', 'common salt', 'sodium chloride'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-PULS-014": CanonicalRemedy(
            canonical_id="REM-PULS-014",
            standard_name="Pulsatilla pratensis",
            common_name="Wind Flower",
            hpi_official_name="Pulsatilla nigricans",
            canonical_abbreviation="Puls.",
            aliases=['pulsatilla', 'pulsatilla pratensis', 'puls', 'wind flower', 'pasque flower'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-SIL-015": CanonicalRemedy(
            canonical_id="REM-SIL-015",
            standard_name="Silicea terra",
            common_name="Pure Flint",
            hpi_official_name="Silicea",
            canonical_abbreviation="Sil.",
            aliases=['silicea', 'silicea terra', 'sil', 'silica', 'pure flint'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="6X"
        ),
        "REM-ARN-016": CanonicalRemedy(
            canonical_id="REM-ARN-016",
            standard_name="Arnica montana",
            common_name="Leopard's Bane",
            hpi_official_name="Arnica montana Linn.",
            canonical_abbreviation="Arn.",
            aliases=['arnica', 'arnica montana', 'arn', 'leopards bane'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-SEP-017": CanonicalRemedy(
            canonical_id="REM-SEP-017",
            standard_name="Sepia officinalis",
            common_name="Cuttlefish Ink",
            hpi_official_name="Sepia succus",
            canonical_abbreviation="Sep.",
            aliases=['sepia', 'sepia officinalis', 'sep', 'cuttlefish ink'],
            kingdom="ANIMAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-THUJ-018": CanonicalRemedy(
            canonical_id="REM-THUJ-018",
            standard_name="Thuja occidentalis",
            common_name="Arbor Vitae",
            hpi_official_name="Thuja occidentalis Linn.",
            canonical_abbreviation="Thuj.",
            aliases=['thuja', 'thuja occidentalis', 'thuj', 'arbor vitae', 'tree of life'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-IGN-019": CanonicalRemedy(
            canonical_id="REM-IGN-019",
            standard_name="Ignatia amara",
            common_name="St. Ignatius Bean",
            hpi_official_name="Strychnos ignatii Berg.",
            canonical_abbreviation="Ign.",
            aliases=['ignatia', 'ignatia amara', 'ign', 'st ignatius bean'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="2X"
        ),
        "REM-CAUST-020": CanonicalRemedy(
            canonical_id="REM-CAUST-020",
            standard_name="Causticum",
            common_name="Hahnemann's Tinctura Acris Sine Kali",
            hpi_official_name="Causticum Hahnemanni",
            canonical_abbreviation="Caust.",
            aliases=['causticum', 'caust', 'causticum hahnemanni'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-CARB-021": CanonicalRemedy(
            canonical_id="REM-CARB-021",
            standard_name="Carbo vegetabilis",
            common_name="Vegetable Charcoal",
            hpi_official_name="Carbo vegetabilis",
            canonical_abbreviation="Carb-v.",
            aliases=['carbo veg', 'carbo vegetabilis', 'carb-v', 'vegetable charcoal'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-HEP-022": CanonicalRemedy(
            canonical_id="REM-HEP-022",
            standard_name="Hepar sulphuris calcareum",
            common_name="Hahnemann's Calcium Sulphide",
            hpi_official_name="Hepar sulphuris calcareum",
            canonical_abbreviation="Hep.",
            aliases=['hepar sulph', 'hepar sulphur', 'hepar sulphuris', 'hep', 'calcium sulphide'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="2X"
        ),
        "REM-GELS-023": CanonicalRemedy(
            canonical_id="REM-GELS-023",
            standard_name="Gelsemium sempervirens",
            common_name="Yellow Jasmine",
            hpi_official_name="Gelsemium sempervirens Ait.",
            canonical_abbreviation="Gels.",
            aliases=['gelsemium', 'gelsemium sempervirens', 'gels', 'yellow jasmine'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-CHIN-024": CanonicalRemedy(
            canonical_id="REM-CHIN-024",
            standard_name="China officinalis",
            common_name="Peruvian Bark",
            hpi_official_name="Cinchona officinalis Linn.",
            canonical_abbreviation="Chin.",
            aliases=['china', 'china officinalis', 'cinchona', 'chin', 'peruvian bark'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-COFF-025": CanonicalRemedy(
            canonical_id="REM-COFF-025",
            standard_name="Coffea cruda",
            common_name="Unroasted Coffee",
            hpi_official_name="Coffea arabica Linn.",
            canonical_abbreviation="Coff.",
            aliases=['coffea', 'coffea cruda', 'coff', 'unroasted coffee'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-CANTH-026": CanonicalRemedy(
            canonical_id="REM-CANTH-026",
            standard_name="Cantharis vesicatoria",
            common_name="Spanish Fly",
            hpi_official_name="Cantharis vesicatoria",
            canonical_abbreviation="Canth.",
            aliases=['cantharis', 'cantharis vesicatoria', 'canth', 'spanish fly'],
            kingdom="ANIMAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-IPEC-027": CanonicalRemedy(
            canonical_id="REM-IPEC-027",
            standard_name="Ipecacuanha",
            common_name="Ipecac Root",
            hpi_official_name="Cephaelis ipecacuanha",
            canonical_abbreviation="Ip.",
            aliases=['ipecac', 'ipecacuanha', 'ip', 'ipecac root'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="2X"
        ),
        "REM-MERC-028": CanonicalRemedy(
            canonical_id="REM-MERC-028",
            standard_name="Mercurius solubilis",
            common_name="Hahnemann's Soluble Mercury",
            hpi_official_name="Mercurius solubilis Hahnemanni",
            canonical_abbreviation="Merc.",
            aliases=['mercurius', 'mercurius solubilis', 'merc sol', 'merc', 'quicksilver'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-STAPH-029": CanonicalRemedy(
            canonical_id="REM-STAPH-029",
            standard_name="Staphysagria",
            common_name="Stavesacre",
            hpi_official_name="Delphinium staphisagria Linn.",
            canonical_abbreviation="Staph.",
            aliases=['staphysagria', 'staph', 'stavesacre'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-DRO-030": CanonicalRemedy(
            canonical_id="REM-DRO-030",
            standard_name="Drosera rotundifolia",
            common_name="Round-leaved Sundew",
            hpi_official_name="Drosera rotundifolia Linn.",
            canonical_abbreviation="Dros.",
            aliases=['drosera', 'drosera rotundifolia', 'dros', 'sundew'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-AUR-031": CanonicalRemedy(
            canonical_id="REM-AUR-031",
            standard_name="Aurum metallicum",
            common_name="Metallic Gold",
            hpi_official_name="Aurum metallicum",
            canonical_abbreviation="Aur.",
            aliases=['aurum', 'aurum metallicum', 'aur', 'metallic gold', 'gold'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-ANTC-032": CanonicalRemedy(
            canonical_id="REM-ANTC-032",
            standard_name="Antimonium crudum",
            common_name="Black Sulphide of Antimony",
            hpi_official_name="Antimonium crudum",
            canonical_abbreviation="Ant-c.",
            aliases=['antimonium crudum', 'ant crud', 'ant-c', 'black antimony', 'stibium'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-HYDR-033": CanonicalRemedy(
            canonical_id="REM-HYDR-033",
            standard_name="Hydrocotyle asiatica",
            common_name="Indian Pennywort",
            hpi_official_name="Centella asiatica Linn.",
            canonical_abbreviation="Hydr-a.",
            aliases=['hydrocotyle', 'hydrocotyle asiatica', 'centella asiatica', 'gotu kola', 'hydr-a'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-RADBR-034": CanonicalRemedy(
            canonical_id="REM-RADBR-034",
            standard_name="Radium bromatum",
            common_name="Radium Bromide",
            hpi_official_name="Radium bromatum",
            canonical_abbreviation="Rad-br.",
            aliases=['radium bromatum', 'radium brom', 'rad-br', 'radium bromide'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="6C"
        ),
        "REM-ARSI-035": CanonicalRemedy(
            canonical_id="REM-ARSI-035",
            standard_name="Arsenicum iodatum",
            common_name="Iodide of Arsenic",
            hpi_official_name="Arsenicum iodatum",
            canonical_abbreviation="Ars-i.",
            aliases=['arsenicum iodatum', 'arsenic iod', 'ars-i', 'arsenic iodide'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-GRAPH-036": CanonicalRemedy(
            canonical_id="REM-GRAPH-036",
            standard_name="Graphites",
            common_name="Black Lead / Plumbago",
            hpi_official_name="Graphites",
            canonical_abbreviation="Graph.",
            aliases=['graphites', 'graph', 'black lead', 'plumbago'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-PETR-037": CanonicalRemedy(
            canonical_id="REM-PETR-037",
            standard_name="Petroleum",
            common_name="Crude Rock Oil",
            hpi_official_name="Petroleum",
            canonical_abbreviation="Petr.",
            aliases=['petroleum', 'petr', 'rock oil', 'crude petroleum', 'coal oil'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-MEZER-038": CanonicalRemedy(
            canonical_id="REM-MEZER-038",
            standard_name="Mezereum",
            common_name="Spurge Olive",
            hpi_official_name="Daphne mezereum Linn.",
            canonical_abbreviation="Mez.",
            aliases=['mezereum', 'daphne mezereum', 'mez', 'spurge olive'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-SARS-039": CanonicalRemedy(
            canonical_id="REM-SARS-039",
            standard_name="Sarsaparilla",
            common_name="Wild Licorice",
            hpi_official_name="Smilax medica",
            canonical_abbreviation="Sars.",
            aliases=['sarsaparilla', 'sars', 'smilax', 'wild licorice'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-ALUM-040": CanonicalRemedy(
            canonical_id="REM-ALUM-040",
            standard_name="Alumina",
            common_name="Pure Clay / Aluminium Oxide",
            hpi_official_name="Alumina",
            canonical_abbreviation="Alum.",
            aliases=['alumina', 'alum', 'argilla', 'aluminium oxide'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="6X"
        ),
        "REM-CHEL-041": CanonicalRemedy(
            canonical_id="REM-CHEL-041",
            standard_name="Chelidonium majus",
            common_name="Greater Celandine",
            hpi_official_name="Chelidonium majus Linn.",
            canonical_abbreviation="Chel.",
            aliases=['chelidonium', 'chelidonium majus', 'chel', 'celandine'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="Q"
        ),
        "REM-POD-042": CanonicalRemedy(
            canonical_id="REM-POD-042",
            standard_name="Podophyllum peltatum",
            common_name="Mayapple",
            hpi_official_name="Podophyllum peltatum Linn.",
            canonical_abbreviation="Pod.",
            aliases=['podophyllum', 'podophyllum peltatum', 'pod', 'mayapple', 'mandrake'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="Q"
        ),
        "REM-ALOE-043": CanonicalRemedy(
            canonical_id="REM-ALOE-043",
            standard_name="Aloe socotrina",
            common_name="Socotrine Aloes",
            hpi_official_name="Aloe socotrina",
            canonical_abbreviation="Aloe",
            aliases=['aloe', 'aloe socotrina', 'aloes'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-COLOC-044": CanonicalRemedy(
            canonical_id="REM-COLOC-044",
            standard_name="Colocynthis",
            common_name="Bitter Apple",
            hpi_official_name="Citrullus colocynthis",
            canonical_abbreviation="Coloc.",
            aliases=['colocynthis', 'colocynth', 'coloc', 'bitter apple'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-CARB-AC-045": CanonicalRemedy(
            canonical_id="REM-CARB-AC-045",
            standard_name="Carbolicum acidum",
            common_name="Phenol",
            hpi_official_name="Acidum carbolicum",
            canonical_abbreviation="Carb-ac.",
            aliases=['carbolic acid', 'carbolicum acidum', 'carb-ac', 'phenol'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-HYDRAS-046": CanonicalRemedy(
            canonical_id="REM-HYDRAS-046",
            standard_name="Hydrastis canadensis",
            common_name="Golden Seal",
            hpi_official_name="Hydrastis canadensis Linn.",
            canonical_abbreviation="Hydr.",
            aliases=['hydrastis', 'hydrastis canadensis', 'golden seal', 'orange root'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-MAGC-047": CanonicalRemedy(
            canonical_id="REM-MAGC-047",
            standard_name="Magnesia carbonica",
            common_name="Carbonate of Magnesia",
            hpi_official_name="Magnesia carbonica",
            canonical_abbreviation="Mag-c.",
            aliases=['magnesia carb', 'magnesia carbonica', 'mag-c'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-MAGP-048": CanonicalRemedy(
            canonical_id="REM-MAGP-048",
            standard_name="Magnesia phosphorica",
            common_name="Phosphate of Magnesia",
            hpi_official_name="Magnesia phosphorica",
            canonical_abbreviation="Mag-p.",
            aliases=['magnesia phos', 'magnesia phosphorica', 'mag-p'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-NAT-S-049": CanonicalRemedy(
            canonical_id="REM-NAT-S-049",
            standard_name="Natrum sulphuricum",
            common_name="Sulphate of Sodium / Glauber's Salt",
            hpi_official_name="Natrum sulphuricum",
            canonical_abbreviation="Nat-s.",
            aliases=['natrum sulph', 'natrum sulphuricum', 'nat-s', 'glaubers salt'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-NAT-C-050": CanonicalRemedy(
            canonical_id="REM-NAT-C-050",
            standard_name="Natrum carbonicum",
            common_name="Carbonate of Sodium",
            hpi_official_name="Natrum carbonicum",
            canonical_abbreviation="Nat-c.",
            aliases=['natrum carb', 'natrum carbonicum', 'nat-c', 'washing soda'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-CRAT-051": CanonicalRemedy(
            canonical_id="REM-CRAT-051",
            standard_name="Crataegus oxyacantha",
            common_name="Hawthorn",
            hpi_official_name="Crataegus oxyacantha Linn.",
            canonical_abbreviation="Crat.",
            aliases=['crataegus', 'crataegus oxyacantha', 'crat', 'hawthorn'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-CACT-052": CanonicalRemedy(
            canonical_id="REM-CACT-052",
            standard_name="Cactus grandiflorus",
            common_name="Night-blooming Cereus",
            hpi_official_name="Cactus grandiflorus Linn.",
            canonical_abbreviation="Cact.",
            aliases=['cactus', 'cactus grandiflorus', 'cact', 'night blooming cereus'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-DIG-053": CanonicalRemedy(
            canonical_id="REM-DIG-053",
            standard_name="Digitalis purpurea",
            common_name="Foxglove",
            hpi_official_name="Digitalis purpurea Linn.",
            canonical_abbreviation="Dig.",
            aliases=['digitalis', 'digitalis purpurea', 'dig', 'foxglove'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-SPIG-054": CanonicalRemedy(
            canonical_id="REM-SPIG-054",
            standard_name="Spigelia anthelmia",
            common_name="Pinkroot",
            hpi_official_name="Spigelia anthelmia Linn.",
            canonical_abbreviation="Spig.",
            aliases=['spigelia', 'spigelia anthelmia', 'spig', 'pinkroot', 'wormgrass'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-GLON-055": CanonicalRemedy(
            canonical_id="REM-GLON-055",
            standard_name="Glonoine",
            common_name="Nitroglycerine",
            hpi_official_name="Glonoinum",
            canonical_abbreviation="Glon.",
            aliases=['glonoine', 'glonoinum', 'glon', 'nitroglycerine'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-HAM-056": CanonicalRemedy(
            canonical_id="REM-HAM-056",
            standard_name="Hamamelis virginiana",
            common_name="Witch Hazel",
            hpi_official_name="Hamamelis virginiana Linn.",
            canonical_abbreviation="Ham.",
            aliases=['hamamelis', 'hamamelis virginiana', 'ham', 'witch hazel'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-VIP-057": CanonicalRemedy(
            canonical_id="REM-VIP-057",
            standard_name="Vipera berus",
            common_name="German Viper",
            hpi_official_name="Vipera torva",
            canonical_abbreviation="Vip.",
            aliases=['vipera', 'vipera berus', 'vip', 'viper venom'],
            kingdom="ANIMAL",
            is_schedule_e1=True,
            min_safe_potency="6C"
        ),
        "REM-CON-058": CanonicalRemedy(
            canonical_id="REM-CON-058",
            standard_name="Conium maculatum",
            common_name="Poison Hemlock",
            hpi_official_name="Conium maculatum Linn.",
            canonical_abbreviation="Con.",
            aliases=['conium', 'conium maculatum', 'con', 'poison hemlock'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-KALI-BI-059": CanonicalRemedy(
            canonical_id="REM-KALI-BI-059",
            standard_name="Kali bichromicum",
            common_name="Bichromate of Potash",
            hpi_official_name="Kali bichromicum",
            canonical_abbreviation="Kali-bi.",
            aliases=['kali bich', 'kali bichromicum', 'kali-bi', 'potassium bichromate'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-KALI-C-060": CanonicalRemedy(
            canonical_id="REM-KALI-C-060",
            standard_name="Kali carbonicum",
            common_name="Carbonate of Potassium",
            hpi_official_name="Kali carbonicum",
            canonical_abbreviation="Kali-c.",
            aliases=['kali carb', 'kali carbonicum', 'kali-c', 'pearl ash'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-ANTT-061": CanonicalRemedy(
            canonical_id="REM-ANTT-061",
            standard_name="Antimonium tartaricum",
            common_name="Tartar Emetic",
            hpi_official_name="Antimonium tartaricum",
            canonical_abbreviation="Ant-t.",
            aliases=['antimonium tart', 'ant tart', 'ant-t', 'tartar emetic'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-SPONG-062": CanonicalRemedy(
            canonical_id="REM-SPONG-062",
            standard_name="Spongia tosta",
            common_name="Roasted Sponge",
            hpi_official_name="Spongia tosta",
            canonical_abbreviation="Spong.",
            aliases=['spongia', 'spongia tosta', 'spong', 'roasted sponge'],
            kingdom="ANIMAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-SAMB-063": CanonicalRemedy(
            canonical_id="REM-SAMB-063",
            standard_name="Sambucus nigra",
            common_name="Elder",
            hpi_official_name="Sambucus nigra Linn.",
            canonical_abbreviation="Samb.",
            aliases=['sambucus', 'sambucus nigra', 'samb', 'elderberry'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-RUMEX-064": CanonicalRemedy(
            canonical_id="REM-RUMEX-064",
            standard_name="Rumex crispus",
            common_name="Yellow Dock",
            hpi_official_name="Rumex crispus Linn.",
            canonical_abbreviation="Rumx.",
            aliases=['rumex', 'rumex crispus', 'rumx', 'yellow dock'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-SANG-065": CanonicalRemedy(
            canonical_id="REM-SANG-065",
            standard_name="Sanguinaria canadensis",
            common_name="Bloodroot",
            hpi_official_name="Sanguinaria canadensis Linn.",
            canonical_abbreviation="Sang.",
            aliases=['sanguinaria', 'sanguinaria canadensis', 'sang', 'bloodroot'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="Q"
        ),
        "REM-HYPER-066": CanonicalRemedy(
            canonical_id="REM-HYPER-066",
            standard_name="Hypericum perforatum",
            common_name="St. John's Wort",
            hpi_official_name="Hypericum perforatum Linn.",
            canonical_abbreviation="Hyper.",
            aliases=['hypericum', 'hypericum perforatum', 'hyper', 'st johns wort'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-SYMPH-067": CanonicalRemedy(
            canonical_id="REM-SYMPH-067",
            standard_name="Symphytum officinale",
            common_name="Knitbone",
            hpi_official_name="Symphytum officinale Linn.",
            canonical_abbreviation="Symph.",
            aliases=['symphytum', 'symphytum officinale', 'symph', 'knitbone', 'comfrey'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-RUTA-068": CanonicalRemedy(
            canonical_id="REM-RUTA-068",
            standard_name="Ruta graveolens",
            common_name="Bitter Wort / Rue",
            hpi_official_name="Ruta graveolens Linn.",
            canonical_abbreviation="Ruta",
            aliases=['ruta', 'ruta graveolens', 'rue', 'bitter herb'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-LED-069": CanonicalRemedy(
            canonical_id="REM-LED-069",
            standard_name="Ledum palustre",
            common_name="Marsh Tea",
            hpi_official_name="Ledum palustre Linn.",
            canonical_abbreviation="Led.",
            aliases=['ledum', 'ledum palustre', 'led', 'marsh tea', 'wild rosemary'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-CALC-F-070": CanonicalRemedy(
            canonical_id="REM-CALC-F-070",
            standard_name="Calcarea fluorica",
            common_name="Fluoride of Lime",
            hpi_official_name="Calcarea fluorica",
            canonical_abbreviation="Calc-f.",
            aliases=['calcarea fluor', 'calc fluor', 'calc-f', 'calcium fluoride'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-CALC-P-071": CanonicalRemedy(
            canonical_id="REM-CALC-P-071",
            standard_name="Calcarea phosphorica",
            common_name="Phosphate of Lime",
            hpi_official_name="Calcarea phosphorica",
            canonical_abbreviation="Calc-p.",
            aliases=['calcarea phos', 'calc phos', 'calc-p', 'calcium phosphate'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-RHOD-072": CanonicalRemedy(
            canonical_id="REM-RHOD-072",
            standard_name="Rhododendron chrysanthum",
            common_name="Snow Rose / Siberian Rhododendron",
            hpi_official_name="Rhododendron chrysanthum",
            canonical_abbreviation="Rhod.",
            aliases=['rhododendron', 'rhododendron chrysanthum', 'rhod', 'snow rose'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-KALM-073": CanonicalRemedy(
            canonical_id="REM-KALM-073",
            standard_name="Kalmia latifolia",
            common_name="Mountain Laurel",
            hpi_official_name="Kalmia latifolia Linn.",
            canonical_abbreviation="Kalm.",
            aliases=['kalmia', 'kalmia latifolia', 'kalm', 'mountain laurel', 'calico bush'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="Q"
        ),
        "REM-BERB-074": CanonicalRemedy(
            canonical_id="REM-BERB-074",
            standard_name="Berberis vulgaris",
            common_name="Barberry",
            hpi_official_name="Berberis vulgaris Linn.",
            canonical_abbreviation="Berb.",
            aliases=['berberis', 'berberis vulgaris', 'berb', 'barberry'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-PAREIR-075": CanonicalRemedy(
            canonical_id="REM-PAREIR-075",
            standard_name="Pareira brava",
            common_name="Virgin Vine",
            hpi_official_name="Chondrodendron tomentosum",
            canonical_abbreviation="Pareir.",
            aliases=['pareira', 'pareira brava', 'pareir', 'virgin vine'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-SABIN-076": CanonicalRemedy(
            canonical_id="REM-SABIN-076",
            standard_name="Sabina",
            common_name="Savine",
            hpi_official_name="Juniperus sabina Linn.",
            canonical_abbreviation="Sabin.",
            aliases=['sabina', 'juniperus sabina', 'sabin', 'savine'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-SEC-077": CanonicalRemedy(
            canonical_id="REM-SEC-077",
            standard_name="Secale cornutum",
            common_name="Ergot of Rye",
            hpi_official_name="Claviceps purpurea",
            canonical_abbreviation="Sec.",
            aliases=['secale', 'secale cornutum', 'sec', 'ergot of rye', 'spurred rye'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-CAUL-078": CanonicalRemedy(
            canonical_id="REM-CAUL-078",
            standard_name="Caulophyllum thalictroides",
            common_name="Blue Cohosh",
            hpi_official_name="Caulophyllum thalictroides Linn.",
            canonical_abbreviation="Caul.",
            aliases=['caulophyllum', 'caulophyllum thalictroides', 'caul', 'blue cohosh', 'squaw root'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-CIMIC-079": CanonicalRemedy(
            canonical_id="REM-CIMIC-079",
            standard_name="Cimicifuga racemosa",
            common_name="Black Cohosh / Actaea",
            hpi_official_name="Actaea racemosa Linn.",
            canonical_abbreviation="Cimic.",
            aliases=['cimicifuga', 'actaea racemosa', 'cimic', 'black cohosh', 'black snake root'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-KREOS-080": CanonicalRemedy(
            canonical_id="REM-KREOS-080",
            standard_name="Kreosotum",
            common_name="Beechwood Creosote",
            hpi_official_name="Kreosotum",
            canonical_abbreviation="Kreos.",
            aliases=['kreosotum', 'kreosote', 'kreos', 'creosote'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-BORAX-081": CanonicalRemedy(
            canonical_id="REM-BORAX-081",
            standard_name="Borax veneta",
            common_name="Biborate of Sodium",
            hpi_official_name="Borax",
            canonical_abbreviation="Bor.",
            aliases=['borax', 'borax veneta', 'bor', 'sodium borate'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-EQUI-082": CanonicalRemedy(
            canonical_id="REM-EQUI-082",
            standard_name="Equisetum hyemale",
            common_name="Scouring Rush / Horsetail",
            hpi_official_name="Equisetum hyemale Linn.",
            canonical_abbreviation="Equis.",
            aliases=['equisetum', 'equisetum hyemale', 'equis', 'horsetail'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-IOD-083": CanonicalRemedy(
            canonical_id="REM-IOD-083",
            standard_name="Iodium",
            common_name="Iodine",
            hpi_official_name="Iodium",
            canonical_abbreviation="Iod.",
            aliases=['iodine', 'iodium', 'iod'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-THYR-084": CanonicalRemedy(
            canonical_id="REM-THYR-084",
            standard_name="Thyroidinum",
            common_name="Thyroid Gland Extract",
            hpi_official_name="Thyroidinum",
            canonical_abbreviation="Thyr.",
            aliases=['thyroidinum', 'thyroid', 'thyr'],
            kingdom="ANIMAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-HYOS-085": CanonicalRemedy(
            canonical_id="REM-HYOS-085",
            standard_name="Hyoscyamus niger",
            common_name="Henbane",
            hpi_official_name="Hyoscyamus niger Linn.",
            canonical_abbreviation="Hyos.",
            aliases=['hyoscyamus', 'hyoscyamus niger', 'hyos', 'henbane'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="2X"
        ),
        "REM-STRAM-086": CanonicalRemedy(
            canonical_id="REM-STRAM-086",
            standard_name="Stramonium",
            common_name="Thorn Apple",
            hpi_official_name="Datura stramonium Linn.",
            canonical_abbreviation="Stram.",
            aliases=['stramonium', 'datura stramonium', 'stram', 'thorn apple', 'jimson weed'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="2X"
        ),
        "REM-CANN-I-087": CanonicalRemedy(
            canonical_id="REM-CANN-I-087",
            standard_name="Cannabis indica",
            common_name="Indian Hemp",
            hpi_official_name="Cannabis sativa Linn.",
            canonical_abbreviation="Cann-i.",
            aliases=['cannabis indica', 'cann-i', 'indian hemp', 'hashish'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-ANAC-088": CanonicalRemedy(
            canonical_id="REM-ANAC-088",
            standard_name="Anacardium orientale",
            common_name="Marking Nut",
            hpi_official_name="Semecarpus anacardium Linn.",
            canonical_abbreviation="Anac.",
            aliases=['anacardium', 'anacardium orientale', 'anac', 'marking nut'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-PLAT-089": CanonicalRemedy(
            canonical_id="REM-PLAT-089",
            standard_name="Platina",
            common_name="Metallic Platinum",
            hpi_official_name="Platinum metallicum",
            canonical_abbreviation="Plat.",
            aliases=['platina', 'platinum', 'plat', 'metallic platinum'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-TARENT-090": CanonicalRemedy(
            canonical_id="REM-TARENT-090",
            standard_name="Tarentula hispanica",
            common_name="Spanish Spider",
            hpi_official_name="Lycosa tarentula",
            canonical_abbreviation="Tarent.",
            aliases=['tarentula', 'tarentula hispanica', 'tarent', 'spanish spider'],
            kingdom="ANIMAL",
            is_schedule_e1=True,
            min_safe_potency="6C"
        ),
        "REM-CUPR-091": CanonicalRemedy(
            canonical_id="REM-CUPR-091",
            standard_name="Cuprum metallicum",
            common_name="Metallic Copper",
            hpi_official_name="Cuprum metallicum",
            canonical_abbreviation="Cupr.",
            aliases=['cuprum', 'cuprum metallicum', 'cupr', 'copper'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-ZINC-092": CanonicalRemedy(
            canonical_id="REM-ZINC-092",
            standard_name="Zincum metallicum",
            common_name="Metallic Zinc",
            hpi_official_name="Zincum metallicum",
            canonical_abbreviation="Zinc.",
            aliases=['zincum', 'zincum metallicum', 'zinc', 'metallic zinc'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-PSOR-093": CanonicalRemedy(
            canonical_id="REM-PSOR-093",
            standard_name="Psorinum",
            common_name="Psoric Nosode",
            hpi_official_name="Psorinum",
            canonical_abbreviation="Psor.",
            aliases=['psorinum', 'psor', 'psorine'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-MED-094": CanonicalRemedy(
            canonical_id="REM-MED-094",
            standard_name="Medorrhinum",
            common_name="Sycotic Nosode",
            hpi_official_name="Medorrhinum",
            canonical_abbreviation="Med.",
            aliases=['medorrhinum', 'med', 'medorrhine'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-SYPH-095": CanonicalRemedy(
            canonical_id="REM-SYPH-095",
            standard_name="Syphilinum",
            common_name="Syphilitic Nosode",
            hpi_official_name="Syphilinum / Lueticum",
            canonical_abbreviation="Syph.",
            aliases=['syphilinum', 'syph', 'lueticum'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-TUB-096": CanonicalRemedy(
            canonical_id="REM-TUB-096",
            standard_name="Tuberculinum",
            common_name="Tuberculous Nosode",
            hpi_official_name="Tuberculinum bovinum",
            canonical_abbreviation="Tub.",
            aliases=['tuberculinum', 'tub', 'bacillinum', 'tuberculin'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-CARC-097": CanonicalRemedy(
            canonical_id="REM-CARC-097",
            standard_name="Carcinosinum",
            common_name="Cancer Nosode",
            hpi_official_name="Carcinosinum",
            canonical_abbreviation="Carc.",
            aliases=['carcinosin', 'carcinosinum', 'carc'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-PYROG-098": CanonicalRemedy(
            canonical_id="REM-PYROG-098",
            standard_name="Pyrogenium",
            common_name="Artificial Sepsine",
            hpi_official_name="Pyrogenium",
            canonical_abbreviation="Pyrog.",
            aliases=['pyrogenium', 'pyrog', 'pyrogen'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-LYSS-099": CanonicalRemedy(
            canonical_id="REM-LYSS-099",
            standard_name="Lyssin",
            common_name="Hydrophobinum",
            hpi_official_name="Lyssinum",
            canonical_abbreviation="Lyss.",
            aliases=['lyssin', 'lyssinum', 'hydrophobinum', 'lyss'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-VARIOL-100": CanonicalRemedy(
            canonical_id="REM-VARIOL-100",
            standard_name="Variolinum",
            common_name="Smallpox Nosode",
            hpi_official_name="Variolinum",
            canonical_abbreviation="Vario.",
            aliases=['variolinum', 'vario'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-MALAND-101": CanonicalRemedy(
            canonical_id="REM-MALAND-101",
            standard_name="Malandrinum",
            common_name="Grease of Horses",
            hpi_official_name="Malandrinum",
            canonical_abbreviation="Maland.",
            aliases=['malandrinum', 'maland'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-DIPHTH-102": CanonicalRemedy(
            canonical_id="REM-DIPHTH-102",
            standard_name="Diphtherinum",
            common_name="Diphtheritic Nosode",
            hpi_official_name="Diphtherinum",
            canonical_abbreviation="Diph.",
            aliases=['diphtherinum', 'diph'],
            kingdom="NOSODE",
            is_schedule_e1=False,
            min_safe_potency="6C"
        ),
        "REM-BAPT-103": CanonicalRemedy(
            canonical_id="REM-BAPT-103",
            standard_name="Baptisia tinctoria",
            common_name="Wild Indigo",
            hpi_official_name="Baptisia tinctoria Linn.",
            canonical_abbreviation="Bapt.",
            aliases=['baptisia', 'baptisia tinctoria', 'bapt', 'wild indigo'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-EUP-PERF-104": CanonicalRemedy(
            canonical_id="REM-EUP-PERF-104",
            standard_name="Eupatorium perfoliatum",
            common_name="Boneset / Thoroughwort",
            hpi_official_name="Eupatorium perfoliatum Linn.",
            canonical_abbreviation="Eup-per.",
            aliases=['eupatorium', 'eupatorium perfoliatum', 'eup-per', 'boneset'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-CAMPH-105": CanonicalRemedy(
            canonical_id="REM-CAMPH-105",
            standard_name="Camphora",
            common_name="Camphor",
            hpi_official_name="Cinnamomum camphora",
            canonical_abbreviation="Camph.",
            aliases=['camphora', 'camphor', 'camph'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="Q"
        ),
        "REM-VERAT-106": CanonicalRemedy(
            canonical_id="REM-VERAT-106",
            standard_name="Veratrum album",
            common_name="White Hellebore",
            hpi_official_name="Veratrum album Linn.",
            canonical_abbreviation="Verat.",
            aliases=['veratrum', 'veratrum album', 'verat', 'white hellebore'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-CHAM-107": CanonicalRemedy(
            canonical_id="REM-CHAM-107",
            standard_name="Chamomilla",
            common_name="German Chamomile",
            hpi_official_name="Matricaria chamomilla Linn.",
            canonical_abbreviation="Cham.",
            aliases=['chamomilla', 'matricaria chamomilla', 'cham', 'german chamomile'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-CINA-108": CanonicalRemedy(
            canonical_id="REM-CINA-108",
            standard_name="Cina maritima",
            common_name="Wormseed",
            hpi_official_name="Artemisia cina Berg.",
            canonical_abbreviation="Cina",
            aliases=['cina', 'cina maritima', 'wormseed', 'santonica'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="2X"
        ),
        "REM-BARY-C-109": CanonicalRemedy(
            canonical_id="REM-BARY-C-109",
            standard_name="Baryta carbonica",
            common_name="Carbonate of Barium",
            hpi_official_name="Baryta carbonica",
            canonical_abbreviation="Bar-c.",
            aliases=['baryta carb', 'baryta carbonica', 'bar-c', 'barium carbonate'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-BARY-M-110": CanonicalRemedy(
            canonical_id="REM-BARY-M-110",
            standard_name="Baryta muriatica",
            common_name="Chloride of Barium",
            hpi_official_name="Baryta muriatica",
            canonical_abbreviation="Bar-m.",
            aliases=['baryta mur', 'baryta muriatica', 'bar-m', 'barium chloride'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-PLUMB-111": CanonicalRemedy(
            canonical_id="REM-PLUMB-111",
            standard_name="Plumbum metallicum",
            common_name="Metallic Lead",
            hpi_official_name="Plumbum metallicum",
            canonical_abbreviation="Plumb.",
            aliases=['plumbum', 'plumbum metallicum', 'plumb', 'lead'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-TAB-112": CanonicalRemedy(
            canonical_id="REM-TAB-112",
            standard_name="Tabacum",
            common_name="Tobacco",
            hpi_official_name="Nicotiana tabacum Linn.",
            canonical_abbreviation="Tab.",
            aliases=['tabacum', 'nicotiana tabacum', 'tab', 'tobacco'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-CHOL-113": CanonicalRemedy(
            canonical_id="REM-CHOL-113",
            standard_name="Cholesterinum",
            common_name="Cholesterine",
            hpi_official_name="Cholesterinum",
            canonical_abbreviation="Chol.",
            aliases=['cholesterinum', 'cholesterin', 'chol'],
            kingdom="ANIMAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-CARD-M-114": CanonicalRemedy(
            canonical_id="REM-CARD-M-114",
            standard_name="Carduus marianus",
            common_name="St. Mary's Thistle",
            hpi_official_name="Silybum marianum",
            canonical_abbreviation="Card-m.",
            aliases=['carduus marianus', 'card-m', 'milk thistle', 'st marys thistle'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-BERB-A-115": CanonicalRemedy(
            canonical_id="REM-BERB-A-115",
            standard_name="Berberis aquifolium",
            common_name="Mountain Grape",
            hpi_official_name="Mahonia aquifolium",
            canonical_abbreviation="Berb-a.",
            aliases=['berberis aquifolium', 'berb-a', 'mahonia', 'oregon grape'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-ECHIN-116": CanonicalRemedy(
            canonical_id="REM-ECHIN-116",
            standard_name="Echinacea angustifolia",
            common_name="Purple Coneflower",
            hpi_official_name="Echinacea angustifolia DC.",
            canonical_abbreviation="Echin.",
            aliases=['echinacea', 'echinacea angustifolia', 'echin', 'purple coneflower'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-CALEN-117": CanonicalRemedy(
            canonical_id="REM-CALEN-117",
            standard_name="Calendula officinalis",
            common_name="Marigold",
            hpi_official_name="Calendula officinalis Linn.",
            canonical_abbreviation="Calen.",
            aliases=['calendula', 'calendula officinalis', 'calen', 'marigold'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-STICTA-118": CanonicalRemedy(
            canonical_id="REM-STICTA-118",
            standard_name="Sticta pulmonaria",
            common_name="Lungwort Lichen",
            hpi_official_name="Lobaria pulmonaria",
            canonical_abbreviation="Stict.",
            aliases=['sticta', 'sticta pulmonaria', 'stict', 'lungwort'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-AMBR-119": CanonicalRemedy(
            canonical_id="REM-AMBR-119",
            standard_name="Ambra grisea",
            common_name="Ambergris",
            hpi_official_name="Ambra grisea",
            canonical_abbreviation="Ambr.",
            aliases=['ambra grisea', 'ambra', 'ambr', 'ambergris'],
            kingdom="ANIMAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-MOSCH-120": CanonicalRemedy(
            canonical_id="REM-MOSCH-120",
            standard_name="Moschus",
            common_name="Musk Deer Secretion",
            hpi_official_name="Moschus moschiferus",
            canonical_abbreviation="Mosch.",
            aliases=['moschus', 'mosch', 'musk'],
            kingdom="ANIMAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-VALER-121": CanonicalRemedy(
            canonical_id="REM-VALER-121",
            standard_name="Valeriana officinalis",
            common_name="Valerian",
            hpi_official_name="Valeriana officinalis Linn.",
            canonical_abbreviation="Valer.",
            aliases=['valeriana', 'valeriana officinalis', 'valer', 'valerian'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-ASAF-122": CanonicalRemedy(
            canonical_id="REM-ASAF-122",
            standard_name="Asafoetida",
            common_name="Devil's Dung",
            hpi_official_name="Ferula foetida",
            canonical_abbreviation="Asaf.",
            aliases=['asafoetida', 'asaf', 'devils dung', 'hing'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-MEPH-123": CanonicalRemedy(
            canonical_id="REM-MEPH-123",
            standard_name="Mephitis putorius",
            common_name="Skunk Secretion",
            hpi_official_name="Mephitis putorius",
            canonical_abbreviation="Meph.",
            aliases=['mephitis', 'mephitis putorius', 'meph', 'skunk'],
            kingdom="ANIMAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-CORALL-124": CanonicalRemedy(
            canonical_id="REM-CORALL-124",
            standard_name="Corallium rubrum",
            common_name="Red Coral",
            hpi_official_name="Corallium rubrum",
            canonical_abbreviation="Cor-r.",
            aliases=['corallium rubrum', 'corallium', 'cor-r', 'red coral'],
            kingdom="ANIMAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-COCC-125": CanonicalRemedy(
            canonical_id="REM-COCC-125",
            standard_name="Cocculus indicus",
            common_name="Indian Cockle",
            hpi_official_name="Anamirta cocculus",
            canonical_abbreviation="Cocc.",
            aliases=['cocculus', 'cocculus indicus', 'cocc', 'indian cockle'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-NUX-M-126": CanonicalRemedy(
            canonical_id="REM-NUX-M-126",
            standard_name="Nux moschata",
            common_name="Nutmeg",
            hpi_official_name="Myristica fragrans",
            canonical_abbreviation="Nux-m.",
            aliases=['nux moschata', 'nux-m', 'nutmeg'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-AGAR-127": CanonicalRemedy(
            canonical_id="REM-AGAR-127",
            standard_name="Agaricus muscarius",
            common_name="Fly Agaric",
            hpi_official_name="Amanita muscaria",
            canonical_abbreviation="Agar.",
            aliases=['agaricus', 'agaricus muscarius', 'agar', 'fly agaric', 'amanita'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-CICUTA-128": CanonicalRemedy(
            canonical_id="REM-CICUTA-128",
            standard_name="Cicuta virosa",
            common_name="Water Hemlock",
            hpi_official_name="Cicuta virosa Linn.",
            canonical_abbreviation="Cicut.",
            aliases=['cicuta', 'cicuta virosa', 'cicut', 'water hemlock', 'cowbane'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-OENANTH-129": CanonicalRemedy(
            canonical_id="REM-OENANTH-129",
            standard_name="Oenanthe crocata",
            common_name="Water Dropwort",
            hpi_official_name="Oenanthe crocata Linn.",
            canonical_abbreviation="Oena.",
            aliases=['oenanthe', 'oenanthe crocata', 'oena', 'water dropwort', 'hemlock dropwort'],
            kingdom="VEGETABLE",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-PASSIF-130": CanonicalRemedy(
            canonical_id="REM-PASSIF-130",
            standard_name="Passiflora incarnata",
            common_name="Passion Flower",
            hpi_official_name="Passiflora incarnata Linn.",
            canonical_abbreviation="Pass.",
            aliases=['passiflora', 'passiflora incarnata', 'pass', 'passion flower'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-PISCID-131": CanonicalRemedy(
            canonical_id="REM-PISCID-131",
            standard_name="Piscidia erythrina",
            common_name="Jamaica Dogwood",
            hpi_official_name="Piscidia piscipula",
            canonical_abbreviation="Pisc.",
            aliases=['piscidia', 'piscidia erythrina', 'pisc', 'jamaica dogwood'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-AVENA-132": CanonicalRemedy(
            canonical_id="REM-AVENA-132",
            standard_name="Avena sativa",
            common_name="Common Oat",
            hpi_official_name="Avena sativa Linn.",
            canonical_abbreviation="Aven.",
            aliases=['avena', 'avena sativa', 'aven', 'oat'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-ALFALF-133": CanonicalRemedy(
            canonical_id="REM-ALFALF-133",
            standard_name="Alfalfa",
            common_name="Medicago / Lucerne",
            hpi_official_name="Medicago sativa Linn.",
            canonical_abbreviation="Alf.",
            aliases=['alfalfa', 'medicago sativa', 'alf', 'lucerne'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-GINS-134": CanonicalRemedy(
            canonical_id="REM-GINS-134",
            standard_name="Ginseng",
            common_name="Wild Ginseng",
            hpi_official_name="Panax quinquefolium Linn.",
            canonical_abbreviation="Gins.",
            aliases=['ginseng', 'panax', 'gins'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-CINCH-S-135": CanonicalRemedy(
            canonical_id="REM-CINCH-S-135",
            standard_name="Chininum sulphuricum",
            common_name="Sulphate of Quinine",
            hpi_official_name="Chininum sulphuricum",
            canonical_abbreviation="Chin-s.",
            aliases=['chininum sulph', 'chininum sulphuricum', 'chin-s', 'quinine'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="1X"
        ),
        "REM-CEDR-136": CanonicalRemedy(
            canonical_id="REM-CEDR-136",
            standard_name="Cedron",
            common_name="Rattlesnake Bean",
            hpi_official_name="Simaruba cedron",
            canonical_abbreviation="Cedr.",
            aliases=['cedron', 'simaruba cedron', 'cedr'],
            kingdom="VEGETABLE",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-HEKLA-137": CanonicalRemedy(
            canonical_id="REM-HEKLA-137",
            standard_name="Hekla lava",
            common_name="Lava of Mount Hekla",
            hpi_official_name="Hekla lava",
            canonical_abbreviation="Hekla",
            aliases=['hekla lava', 'hekla', 'hecla lava'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
        ),
        "REM-MERC-C-138": CanonicalRemedy(
            canonical_id="REM-MERC-C-138",
            standard_name="Mercurius corrosivus",
            common_name="Corrosive Sublimate",
            hpi_official_name="Hydrargyrum bichloratum",
            canonical_abbreviation="Merc-c.",
            aliases=['mercurius corrosivus', 'merc corr', 'merc-c', 'corrosive sublimate'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-MERC-D-139": CanonicalRemedy(
            canonical_id="REM-MERC-D-139",
            standard_name="Mercurius dulcis",
            common_name="Calomel",
            hpi_official_name="Hydrargyrum chloratum mite",
            canonical_abbreviation="Merc-d.",
            aliases=['mercurius dulcis', 'calomel', 'merc dulc', 'merc-d'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-NITR-AC-140": CanonicalRemedy(
            canonical_id="REM-NITR-AC-140",
            standard_name="Nitricum acidum",
            common_name="Nitric Acid",
            hpi_official_name="Acidum nitricum",
            canonical_abbreviation="Nit-ac.",
            aliases=['nitric acid', 'nitricum acidum', 'nit-ac'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-MURIAT-AC-141": CanonicalRemedy(
            canonical_id="REM-MURIAT-AC-141",
            standard_name="Muriaticum acidum",
            common_name="Hydrochloric Acid",
            hpi_official_name="Acidum hydrochloricum",
            canonical_abbreviation="Mur-ac.",
            aliases=['muriatic acid', 'muriaticum acidum', 'mur-ac', 'hydrochloric acid'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-SULPH-AC-142": CanonicalRemedy(
            canonical_id="REM-SULPH-AC-142",
            standard_name="Sulphuricum acidum",
            common_name="Sulphuric Acid",
            hpi_official_name="Acidum sulphuricum",
            canonical_abbreviation="Sul-ac.",
            aliases=['sulphuric acid', 'sulphuricum acidum', 'sul-ac'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-OXAL-AC-143": CanonicalRemedy(
            canonical_id="REM-OXAL-AC-143",
            standard_name="Oxalicum acidum",
            common_name="Oxalic Acid",
            hpi_official_name="Acidum oxalicum",
            canonical_abbreviation="Ox-ac.",
            aliases=['oxalic acid', 'oxalicum acidum', 'ox-ac'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-PICRIC-AC-144": CanonicalRemedy(
            canonical_id="REM-PICRIC-AC-144",
            standard_name="Picricum acidum",
            common_name="Picric Acid",
            hpi_official_name="Acidum picricum",
            canonical_abbreviation="Pic-ac.",
            aliases=['picric acid', 'picricum acidum', 'pic-ac'],
            kingdom="MINERAL",
            is_schedule_e1=True,
            min_safe_potency="3X"
        ),
        "REM-BENZ-AC-145": CanonicalRemedy(
            canonical_id="REM-BENZ-AC-145",
            standard_name="Benzoicum acidum",
            common_name="Benzoic Acid",
            hpi_official_name="Acidum benzoicum",
            canonical_abbreviation="Benz-ac.",
            aliases=['benzoic acid', 'benzoicum acidum', 'benz-ac'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-KALI-P-146": CanonicalRemedy(
            canonical_id="REM-KALI-P-146",
            standard_name="Kali phosphoricum",
            common_name="Phosphate of Potassium",
            hpi_official_name="Kali phosphoricum",
            canonical_abbreviation="Kali-p.",
            aliases=['kali phos', 'kali phosphoricum', 'kali-p', 'potassium phosphate'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-KALI-S-147": CanonicalRemedy(
            canonical_id="REM-KALI-S-147",
            standard_name="Kali sulphuricum",
            common_name="Sulphate of Potassium",
            hpi_official_name="Kali sulphuricum",
            canonical_abbreviation="Kali-s.",
            aliases=['kali sulph', 'kali sulphuricum', 'kali-s', 'potassium sulphate'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-KALI-M-148": CanonicalRemedy(
            canonical_id="REM-KALI-M-148",
            standard_name="Kali muriaticum",
            common_name="Chloride of Potassium",
            hpi_official_name="Kali muriaticum",
            canonical_abbreviation="Kali-m.",
            aliases=['kali mur', 'kali muriaticum', 'kali-m', 'potassium chloride'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-FERR-P-149": CanonicalRemedy(
            canonical_id="REM-FERR-P-149",
            standard_name="Ferrum phosphoricum",
            common_name="Phosphate of Iron",
            hpi_official_name="Ferrum phosphoricum",
            canonical_abbreviation="Ferr-p.",
            aliases=['ferrum phos', 'ferrum phosphoricum', 'ferr-p', 'iron phosphate'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        ),
        "REM-NAT-P-150": CanonicalRemedy(
            canonical_id="REM-NAT-P-150",
            standard_name="Natrum phosphoricum",
            common_name="Phosphate of Soda",
            hpi_official_name="Natrum phosphoricum",
            canonical_abbreviation="Nat-p.",
            aliases=['natrum phos', 'natrum phosphoricum', 'nat-p', 'sodium phosphate'],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="Q"
        )
    }

    # Fast lookup index: normalized_string -> canonical_id
    _LOOKUP_INDEX: Dict[str, str] = {}

    @classmethod
    def _normalize(cls, text: str) -> str:
        """Strips punctuation, trailing dots, and converts to lower case."""
        return re.sub(r"[^a-zA-Z0-9]", "", text).lower()

    @classmethod
    def _build_index(cls) -> None:
        if cls._LOOKUP_INDEX:
            return
        for cid, rem in cls._REGISTRY.items():
            cls._LOOKUP_INDEX[cls._normalize(rem.canonical_id)] = cid
            cls._LOOKUP_INDEX[cls._normalize(rem.standard_name)] = cid
            cls._LOOKUP_INDEX[cls._normalize(rem.common_name)] = cid
            cls._LOOKUP_INDEX[cls._normalize(rem.hpi_official_name)] = cid
            cls._LOOKUP_INDEX[cls._normalize(rem.canonical_abbreviation)] = cid
            for alias in rem.aliases:
                cls._LOOKUP_INDEX[cls._normalize(alias)] = cid

    @classmethod
    def resolve_remedy(cls, query: str) -> CanonicalRemedy:
        """
        Resolves any synonym, abbreviation, or botanical name to its CanonicalRemedy record (INV-16).
        """
        cls._build_index()
        norm = cls._normalize(query)
        cid = cls._LOOKUP_INDEX.get(norm)
        if not cid:
            # Fallback prefix match for clinical abbreviations with minimum length >= 5
            for alias_key, mapped_cid in cls._LOOKUP_INDEX.items():
                if len(alias_key) >= 5 and (norm.startswith(alias_key) or alias_key.startswith(norm)):
                    cid = mapped_cid
                    break

        if not cid or cid not in cls._REGISTRY:
            raise UnresolvedRemedyException(
                f"UNRESOLVED REMEDY (INV-16): Could not map '{query}' to any canonical pharmacopoeial entry.",
                query=query
            )

        return cls._REGISTRY[cid]

    @classmethod
    def get_system_banner(cls) -> str:
        """Returns statutory legal status banner."""
        return SYSTEM_STATUS_BANNER

    @classmethod
    def total_remedies_count(cls) -> int:
        """Returns total active canonical remedies in registry."""
        return len(cls._REGISTRY)
