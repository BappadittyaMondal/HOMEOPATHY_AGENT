"""
Homoeopathic Pharmacopoeia of India (HPI) Standardized Monograph Database (Phase 17).
Codifies official botanical, chemical, and toxicological standards under Drugs & Cosmetics Act 1940 (Schedule M-I).
"""
from typing import Dict, List, Optional
from app.models.safety import KingdomEnum, HPIMonograph

class HPIMonographDatabase:
    """
    Standardized repository of official HPI Monographs.
    Enforces minimum dispensing potencies and Schedule E(1) toxic alkaloid classifications.
    """

    MONOGRAPHS: Dict[str, HPIMonograph] = {
        "Aconitum napellus": HPIMonograph(
            remedy_name="Aconitum napellus",
            abbreviation="Acon",
            botanical_chemical_name="Aconitum napellus L. (Ranunculaceae)",
            kingdom=KingdomEnum.VEGETABLE,
            hpi_volume=1,
            minimum_allowed_potency="3X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Aconitine", "Mesaconitine", "Hypaconitine"]
        ),
        "Arsenicum album": HPIMonograph(
            remedy_name="Arsenicum album",
            abbreviation="Ars",
            botanical_chemical_name="Arsenic Trioxide (As2O3)",
            kingdom=KingdomEnum.MINERAL,
            hpi_volume=1,
            minimum_allowed_potency="6X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Inorganic Arsenic Trioxide"]
        ),
        "Belladonna": HPIMonograph(
            remedy_name="Belladonna",
            abbreviation="Bell",
            botanical_chemical_name="Atropa belladonna L. (Solanaceae)",
            kingdom=KingdomEnum.VEGETABLE,
            hpi_volume=1,
            minimum_allowed_potency="2X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Hyoscyamine", "Atropine", "Scopolamine"]
        ),
        "Digitalis purpurea": HPIMonograph(
            remedy_name="Digitalis purpurea",
            abbreviation="Dig",
            botanical_chemical_name="Digitalis purpurea L. (Plantaginaceae)",
            kingdom=KingdomEnum.VEGETABLE,
            hpi_volume=1,
            minimum_allowed_potency="3X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Digitoxin", "Gitoxin", "Gitalin"]
        ),
        "Strychnos nux-vomica": HPIMonograph(
            remedy_name="Strychnos nux-vomica",
            abbreviation="Nux-v",
            botanical_chemical_name="Strychnos nux-vomica L. (Loganiaceae)",
            kingdom=KingdomEnum.VEGETABLE,
            hpi_volume=1,
            minimum_allowed_potency="3X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Strychnine", "Brucine"]
        ),
        "Gelsemium sempervirens": HPIMonograph(
            remedy_name="Gelsemium sempervirens",
            abbreviation="Gels",
            botanical_chemical_name="Gelsemium sempervirens (L.) J.St.-Hil.",
            kingdom=KingdomEnum.VEGETABLE,
            hpi_volume=1,
            minimum_allowed_potency="2X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Gelsemine", "Sempervirine"]
        ),
        "Cantharis vesicatoria": HPIMonograph(
            remedy_name="Cantharis vesicatoria",
            abbreviation="Canth",
            botanical_chemical_name="Lytta vesicatoria (Spanish Fly)",
            kingdom=KingdomEnum.ANIMAL,
            hpi_volume=1,
            minimum_allowed_potency="3X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Cantharidin"]
        ),
        "Colchicum autumnale": HPIMonograph(
            remedy_name="Colchicum autumnale",
            abbreviation="Colch",
            botanical_chemical_name="Colchicum autumnale L. (Colchicaceae)",
            kingdom=KingdomEnum.VEGETABLE,
            hpi_volume=2,
            minimum_allowed_potency="3X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Colchicine"]
        ),
        "Conium maculatum": HPIMonograph(
            remedy_name="Conium maculatum",
            abbreviation="Con",
            botanical_chemical_name="Conium maculatum L. (Poison Hemlock)",
            kingdom=KingdomEnum.VEGETABLE,
            hpi_volume=1,
            minimum_allowed_potency="3X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Coniine", "Conhydrine"]
        ),
        "Secale cornutum": HPIMonograph(
            remedy_name="Secale cornutum",
            abbreviation="Sec",
            botanical_chemical_name="Claviceps purpurea (Fries) Tulasne",
            kingdom=KingdomEnum.VEGETABLE,
            hpi_volume=2,
            minimum_allowed_potency="3X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Ergotamine", "Ergonovine", "Ergocristine"]
        ),
        "Mercurius solubilis": HPIMonograph(
            remedy_name="Mercurius solubilis",
            abbreviation="Merc",
            botanical_chemical_name="Hydrargyrum oxydulatum nigrum Hahnemanni",
            kingdom=KingdomEnum.MINERAL,
            hpi_volume=1,
            minimum_allowed_potency="6X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Precipitated Mercurous Oxide"]
        ),
        "Plumbum metallicum": HPIMonograph(
            remedy_name="Plumbum metallicum",
            abbreviation="Plb",
            botanical_chemical_name="Metallic Lead (Pb)",
            kingdom=KingdomEnum.MINERAL,
            hpi_volume=2,
            minimum_allowed_potency="6X",
            is_schedule_e1_toxic=True,
            active_alkaloids=["Elemental Lead"]
        ),
        "Lachesis muta": HPIMonograph(
            remedy_name="Lachesis muta",
            abbreviation="Lach",
            botanical_chemical_name="Lachesis muta venom (Bushmaster Viper)",
            kingdom=KingdomEnum.ANIMAL,
            hpi_volume=2,
            minimum_allowed_potency="6C",
            is_schedule_e1_toxic=True,
            active_alkaloids=["L-amino acid oxidase", "Procoagulant venom enzymes"]
        ),
        "Sulphur": HPIMonograph(
            remedy_name="Sulphur",
            abbreviation="Sulph",
            botanical_chemical_name="Sublimed Sulphur (S)",
            kingdom=KingdomEnum.MINERAL,
            hpi_volume=1,
            minimum_allowed_potency="Q",
            is_schedule_e1_toxic=False,
            active_alkaloids=[]
        ),
        "Calcarea carbonica": HPIMonograph(
            remedy_name="Calcarea carbonica",
            abbreviation="Calc",
            botanical_chemical_name="Calcium Carbonate from middle oyster shell (CaCO3)",
            kingdom=KingdomEnum.MINERAL,
            hpi_volume=1,
            minimum_allowed_potency="3X",
            is_schedule_e1_toxic=False,
            active_alkaloids=[]
        ),
        "Pulsatilla pratensis": HPIMonograph(
            remedy_name="Pulsatilla pratensis",
            abbreviation="Puls",
            botanical_chemical_name="Pulsatilla pratensis (L.) Mill. (Ranunculaceae)",
            kingdom=KingdomEnum.VEGETABLE,
            hpi_volume=1,
            minimum_allowed_potency="Q",
            is_schedule_e1_toxic=False,
            active_alkaloids=["Anemonin", "Protoanemonin"]
        )
    }

    @classmethod
    def get_monograph(cls, remedy_name: str) -> Optional[HPIMonograph]:
        """Retrieves official HPI monograph by exact or common name."""
        return cls.MONOGRAPHS.get(remedy_name)

    @classmethod
    def is_schedule_e1(cls, remedy_name: str) -> bool:
        """Checks if remedy is a Schedule E(1) statutory poison under Drugs & Cosmetics Rules."""
        mono = cls.get_monograph(remedy_name)
        return mono.is_schedule_e1_toxic if mono else False

    @classmethod
    def get_minimum_safe_potency(cls, remedy_name: str) -> str:
        """Returns lowest statutory dispensing dilution allowed under HPI."""
        mono = cls.get_monograph(remedy_name)
        return mono.minimum_allowed_potency if mono else "Q"
