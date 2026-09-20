"""
Canonical Remedy Registry & Nomenclature Normalization Engine (Phase 59).
Resolves variant homeopathic nomenclature, abbreviations, and botanical synonyms
to deterministic Canonical Remedy Identifiers (INV-16).
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
    to a single authoritative CanonicalRemedy record (INV-16).
    """

    # Top Polychrests & Statutory Classical Database
    _REGISTRY: Dict[str, CanonicalRemedy] = {
        "REM-ACON-001": CanonicalRemedy(
            canonical_id="REM-ACON-001",
            standard_name="Aconitum napellus",
            common_name="Monkshood",
            hpi_official_name="Aconitum napellus Linn.",
            canonical_abbreviation="Acon.",
            aliases=["aconite", "acon", "aconitum", "aconitum napellus", "monkshood", "wolfsbane"],
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
            aliases=["belladonna", "bell", "atropa belladonna", "deadly nightshade"],
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
            aliases=["bryonia", "bry", "bryonia alba", "white bryony"],
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
            aliases=["nux vomica", "nux vom", "nux-v", "nux", "strychnos nux-vomica", "poison nut"],
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
            aliases=["sulfur", "sulphur", "sulph", "brimstone", "sublimed sulphur"],
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
            aliases=["phosphorus", "phos", "elemental phosphorus", "white phosphorus"],
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
            aliases=["rhus tox", "rhus toxicodendron", "rhus-t", "poison ivy", "toxicodendron radicans"],
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
            aliases=["apis", "apis mel", "apis mellifica", "honey bee"],
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
            aliases=["arsenic", "arsenicum", "arsenicum album", "ars", "white arsenic", "as2o3"],
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
            aliases=["calc carb", "calcarea carb", "calcarea carbonica", "calc", "oyster shell"],
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
            aliases=["lachesis", "lachesis muta", "lach", "bushmaster"],
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
            aliases=["lycopodium", "lycopodium clavatum", "lyc", "club moss"],
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
            aliases=["natrum mur", "natrum muriaticum", "nat-m", "common salt", "sodium chloride"],
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
            aliases=["pulsatilla", "pulsatilla pratensis", "puls", "wind flower", "pasque flower"],
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
            aliases=["silicea", "silicea terra", "sil", "silica", "pure flint"],
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
            aliases=["arnica", "arnica montana", "arn", "leopards bane"],
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
            aliases=["sepia", "sepia officinalis", "sep", "cuttlefish ink"],
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
            aliases=["thuja", "thuja occidentalis", "thuj", "arbor vitae", "tree of life"],
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
            aliases=["ignatia", "ignatia amara", "ign", "st ignatius bean"],
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
            aliases=["causticum", "caust", "causticum hahnemanni"],
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
            aliases=["carbo veg", "carbo vegetabilis", "carb-v", "vegetable charcoal"],
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
            aliases=["hepar sulph", "hepar sulphur", "hepar sulphuris", "hep", "calcium sulphide"],
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
            aliases=["gelsemium", "gelsemium sempervirens", "gels", "yellow jasmine"],
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
            aliases=["china", "china officinalis", "cinchona", "chin", "peruvian bark"],
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
            aliases=["coffea", "coffea cruda", "coff", "unroasted coffee"],
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
            aliases=["cantharis", "cantharis vesicatoria", "canth", "spanish fly"],
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
            aliases=["ipecac", "ipecacuanha", "ip", "ipecac root"],
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
            aliases=["mercurius", "mercurius solubilis", "merc sol", "merc", "quicksilver"],
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
            aliases=["staphysagria", "staph", "stavesacre"],
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
            aliases=["drosera", "drosera rotundifolia", "dros", "sundew"],
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
            aliases=["aurum", "aurum metallicum", "aur", "metallic gold", "gold"],
            kingdom="MINERAL",
            is_schedule_e1=False,
            min_safe_potency="3X"
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
            # Fallback substring match
            for alias_key, mapped_cid in cls._LOOKUP_INDEX.items():
                if len(alias_key) >= 4 and (alias_key in norm or norm in alias_key):
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
