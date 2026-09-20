"""
Bach-Paterson Bowel Nosodes Engine (Phase 25).
Codifies the 7 classical bowel nosode groups, non-lactose fermenting dysbiosis phenotypes,
constitutional remedy correlations, and 3-month repetition lockout gates per John Paterson.
"""
from typing import Dict, List, Optional
from app.models.safety import (
    BowelNosodeProfile,
    ToxicitySafetyStatus
)

class BowelNosodeEngine:
    """
    Knowledge and clinical safety engine for the Bach-Paterson Bowel Nosodes.
    """

    DATABASE: Dict[str, BowelNosodeProfile] = {
        "Morgan Pure": BowelNosodeProfile(
            nosode_name="Morgan Pure",
            bach_paterson_group="Morgan (B. morgani)",
            related_non_bowel_remedies=["Sulphur", "Lycopodium clavatum", "Calcarea carbonica", "Medorrhinum"],
            dysbiosis_symptoms=[
                "Venous and portal congestion",
                "Severe skin pruritus worse heat and bathing",
                "Bilious headaches and liver torpor",
                "Constipation with hemorrhoids"
            ],
            repeat_lockout_months=3
        ),
        "Proteus": BowelNosodeProfile(
            nosode_name="Proteus",
            bach_paterson_group="Proteus (B. proteus)",
            related_non_bowel_remedies=["Natrum muriaticum", "Ignatia amara", "Secale cornutum", "Aurum metallicum"],
            dysbiosis_symptoms=[
                "Sudden violent emotional storms and tantrums",
                "Peripheral angiospasm and Raynaud's phenomenon",
                "Duodenal ulceration with neuromuscular spasm",
                "Brain fatigue and mental strain"
            ],
            repeat_lockout_months=3
        ),
        "Bacillus No. 7": BowelNosodeProfile(
            nosode_name="Bacillus No. 7",
            bach_paterson_group="Non-Lactose Fermenter No. 7",
            related_non_bowel_remedies=["Kali carbonicum", "Kali bichromicum", "Arsenicum iodatum", "Iodum"],
            dysbiosis_symptoms=[
                "Profound mental and physical fatigue",
                "Muscular debility and slow capillary circulation",
                "Rheumatic stiffness worse cold damp",
                "Copious stringy catarrhal secretions"
            ],
            repeat_lockout_months=3
        ),
        "Gaertner": BowelNosodeProfile(
            nosode_name="Gaertner",
            bach_paterson_group="Gaertner (B. gaertner)",
            related_non_bowel_remedies=["Phosphorus", "Silicea terra", "Calcarea fluorica", "Pulsatilla pratensis"],
            dysbiosis_symptoms=[
                "Intestinal malabsorption and celiac syndrome",
                "Inability to digest fats and dairy",
                "Marked physical emaciation despite ravenous eating",
                "Overactive, nervous, precocious children with threadworms"
            ],
            repeat_lockout_months=3
        ),
        "Dysentery-Co": BowelNosodeProfile(
            nosode_name="Dysentery-Co",
            bach_paterson_group="Dysentery (B. dysenteriae)",
            related_non_bowel_remedies=["Arsenicum album", "Thuja occidentalis", "Argentum nitricum", "Veratrum album"],
            dysbiosis_symptoms=[
                "Anticipatory anxiety with gastrointestinal hypermotility",
                "Pyloric spasm and duodenal ulcers",
                "Nervous cardiac palpitations and choreiform tics",
                "Mucous colitis and tenesmus"
            ],
            repeat_lockout_months=3
        ),
        "Sycotic-Co": BowelNosodeProfile(
            nosode_name="Sycotic-Co",
            bach_paterson_group="Sycotic Bacillus",
            related_non_bowel_remedies=["Thuja occidentalis", "Medorrhinum", "Natrum sulphuricum", "Antimonium tartaricum"],
            dysbiosis_symptoms=[
                "Chronic sycotic catarrh of respiratory and mucous membranes",
                "Irritable bladder with nocturnal enuresis",
                "Synovial effusion and joint stiffness worse wet weather",
                "Profuse sour nighttime perspiration"
            ],
            repeat_lockout_months=3
        ),
        "Mutabile": BowelNosodeProfile(
            nosode_name="Mutabile",
            bach_paterson_group="Mutabile (B. mutabile)",
            related_non_bowel_remedies=["Pulsatilla pratensis", "Ferrum phosphoricum", "Kali phosphoricum"],
            dysbiosis_symptoms=[
                "Alternating erratic symptoms",
                "Recurrent urinary tract infection with altered bacterial motility",
                "Shifting pains and changing catarrhal conditions"
            ],
            repeat_lockout_months=3
        )
    }

    @classmethod
    def get_profile(cls, nosode_name: str) -> Optional[BowelNosodeProfile]:
        """Retrieves verified bowel nosode profile."""
        return cls.DATABASE.get(nosode_name)

    @classmethod
    def find_by_constitutional_remedy(cls, constitutional_remedy: str) -> List[BowelNosodeProfile]:
        """
        Finds corresponding bowel nosodes linked to a non-bowel constitutional remedy
        per Paterson's clinical concordances.
        """
        target = constitutional_remedy.strip().lower()
        matches = []
        for profile in cls.DATABASE.values():
            for rem in profile.related_non_bowel_remedies:
                if target in rem.lower() or rem.lower() in target:
                    matches.append(profile)
                    break
        return matches

    @classmethod
    def evaluate_prescription(
        cls,
        nosode_name: str,
        months_since_prior: Optional[int] = None
    ) -> Dict:
        """
        Validates safety of prescribing bowel nosode, enforcing the 3-month lockout gate.
        """
        profile = cls.DATABASE.get(nosode_name)
        if not profile:
            return {
                "nosode_name": nosode_name,
                "status": ToxicitySafetyStatus.APPROVED,
                "permitted": True,
                "message": "Remedy is not an indexed Bach-Paterson bowel nosode."
            }

        if months_since_prior is not None and months_since_prior < profile.repeat_lockout_months:
            return {
                "nosode_name": nosode_name,
                "status": ToxicitySafetyStatus.HARD_BLOCKED,
                "permitted": False,
                "message": (
                    f"PATERSION LOCKOUT VIOLATION: Bowel nosode {nosode_name} was administered {months_since_prior} "
                    f"months ago. Minimum safe inter-dose lockout is {profile.repeat_lockout_months} months. "
                    f"Frequent repetition destabilizes bowel microbiome and vital reaction."
                )
            }

        return {
            "nosode_name": nosode_name,
            "status": ToxicitySafetyStatus.APPROVED,
            "permitted": True,
            "group": profile.bach_paterson_group,
            "message": f"Bowel nosode {nosode_name} approved. Single dose in 30C or 200C indicated."
        }
