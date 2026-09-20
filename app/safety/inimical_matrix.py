"""
Classical 26-Point Inimical Matrix & Antidotal Engine (Phase 20).
Codifies incompatible remedy sequences, temporal washout windows (14d, 45-60d, 180d),
and the Acute Intercurrent Override Exception per Gibson Miller, Hering, and Kent.
"""
from typing import Dict, List, Optional, Tuple
from app.models.safety import (
    InimicalRule,
    InimicalEvaluation,
    ToxicitySafetyStatus
)

class InimicalSafetyMatrix:
    """
    Evaluates remedy sequence compatibility against classical inimical pairs,
    enforcing temporal washout periods and safe antidoting protocols.
    """

    # 26 Classical Inimical Pairs (remedy_a, remedy_b, washout_days, hazard)
    RULES_26: List[InimicalRule] = [
        InimicalRule(
            remedy_a="Apis mellifica",
            remedy_b="Rhus toxicodendron",
            washout_days=14,
            pathogenetic_hazard="Violent erysipelatous inflammation, cellular edema, and intense restless aggravation."
        ),
        InimicalRule(
            remedy_a="Causticum",
            remedy_b="Phosphorus",
            washout_days=60,
            pathogenetic_hazard="Deep neuro-muscular exhaustion, paralytic weakness, and destruction of curative reaction."
        ),
        InimicalRule(
            remedy_a="Silicea terra",
            remedy_b="Mercurius solubilis",
            washout_days=60,
            pathogenetic_hazard="Violent glandular suppuration, bone necrosis, and profound systemic devastation."
        ),
        InimicalRule(
            remedy_a="Ignatia amara",
            remedy_b="Strychnos nux-vomica",
            washout_days=14,
            pathogenetic_hazard="Discordant strychnos alkaloid pathogenesis, irritable hyperesthesia, and nervous spasms."
        ),
        InimicalRule(
            remedy_a="Pulsatilla pratensis",
            remedy_b="Chamomilla",
            washout_days=14,
            pathogenetic_hazard="Severe emotional irritability, contradictory catarrhal symptoms, and therapeutic blockage."
        ),
        InimicalRule(
            remedy_a="Dulcamara",
            remedy_b="Atropa belladonna",
            washout_days=14,
            pathogenetic_hazard="Discordant vasomotor vascular reaction, violent cerebral congestion, and skin eruption."
        ),
        InimicalRule(
            remedy_a="China officinalis",
            remedy_b="Digitalis purpurea",
            washout_days=30,
            pathogenetic_hazard="Dangerous cardiac rhythm disturbance, extreme weakness, and arterial collapse."
        ),
        InimicalRule(
            remedy_a="Coffea cruda",
            remedy_b="Cantharis vesicatoria",
            washout_days=14,
            pathogenetic_hazard="Violent genitourinary tenesmus and uncontrollable nervous excitability."
        ),
        InimicalRule(
            remedy_a="Zincum metallicum",
            remedy_b="Strychnos nux-vomica",
            washout_days=30,
            pathogenetic_hazard="Neuro-muscular twitches, severe insomnia, and paralysis of nervous vitality."
        ),
        InimicalRule(
            remedy_a="Zincum metallicum",
            remedy_b="Chamomilla",
            washout_days=14,
            pathogenetic_hazard="Exaggerated sensory hyperesthesia and suppression of eruptive tendencies."
        ),
        InimicalRule(
            remedy_a="Psorinum",
            remedy_b="Lachesis muta",
            washout_days=60,
            pathogenetic_hazard="Severe miasmatic upheaval, profound depressive states, and skin necrosis."
        ),
        InimicalRule(
            remedy_a="Sepia officinalis",
            remedy_b="Lachesis muta",
            washout_days=45,
            pathogenetic_hazard="Severe venous congestion, hot flashes, intense melancholy, and menstrual hemorrhage."
        ),
        InimicalRule(
            remedy_a="Sepia officinalis",
            remedy_b="Pulsatilla pratensis",
            washout_days=30,
            pathogenetic_hazard="Contradictory venous and hormonal symptoms without clear therapeutic direction."
        ),
        InimicalRule(
            remedy_a="Ferrum metallicum",
            remedy_b="Pulsatilla pratensis",
            washout_days=30,
            pathogenetic_hazard="Chlorotic circulatory turmoil, flushing, and digestive intolerance."
        ),
        InimicalRule(
            remedy_a="Stramonium",
            remedy_b="Coffea cruda",
            washout_days=14,
            pathogenetic_hazard="Terrifying hallucinations, violent delirium, and complete cardiac insomnia."
        ),
        InimicalRule(
            remedy_a="Nitricum acidum",
            remedy_b="Lachesis muta",
            washout_days=60,
            pathogenetic_hazard="Malignant ulceration of mucous surfaces and profound syphilitic breakdown."
        ),
        InimicalRule(
            remedy_a="Aceticum acidum",
            remedy_b="Arnica montana",
            washout_days=14,
            pathogenetic_hazard="Suppression of traumatic extravasation and extreme gastrointestinal wasting."
        ),
        InimicalRule(
            remedy_a="Aceticum acidum",
            remedy_b="Atropa belladonna",
            washout_days=14,
            pathogenetic_hazard="Neutralization of Belladonna's curative action with severe colic."
        ),
        InimicalRule(
            remedy_a="Aceticum acidum",
            remedy_b="Lachesis muta",
            washout_days=30,
            pathogenetic_hazard="Destructive blood decomposition, hemorrhage, and anasarca."
        ),
        InimicalRule(
            remedy_a="Ranunculus bulbosus",
            remedy_b="Staphysagria",
            washout_days=14,
            pathogenetic_hazard="Intercostal neuralgia exacerbation and vesicular dermal blistering."
        ),
        InimicalRule(
            remedy_a="Cantharis vesicatoria",
            remedy_b="Atropa belladonna",
            washout_days=14,
            pathogenetic_hazard="Violent inflammation of bladder neck and meningeal congestion."
        ),
        InimicalRule(
            remedy_a="Carbo vegetabilis",
            remedy_b="Kreosotum",
            washout_days=30,
            pathogenetic_hazard="Severe capillary bleeding, gangrenous decay, and gastrointestinal burning."
        ),
        InimicalRule(
            remedy_a="Hepar sulphuris",
            remedy_b="Mercurius solubilis",
            washout_days=30,
            pathogenetic_hazard="Suppurative destruction of lymphatic glands and severe salivation."
        ),
        InimicalRule(
            remedy_a="Kali carbonicum",
            remedy_b="Nitricum acidum",
            washout_days=45,
            pathogenetic_hazard="Severe pleuritic pains, renal inflammation, and systemic weakness."
        ),
        InimicalRule(
            remedy_a="Aloe socotrina",
            remedy_b="Allium cepa",
            washout_days=14,
            pathogenetic_hazard="Violent catarrhal colitis and mucous tenesmus."
        ),
        InimicalRule(
            remedy_a="Calcarea carbonica",
            remedy_b="Bryonia alba",
            washout_days=45,
            pathogenetic_hazard="Calcarea should not be immediately followed by Bryonia; produces serous inflammation."
        )
    ]

    # Classical Antidotes Dictionary
    ANTIDOTES: Dict[str, List[str]] = {
        "Aconitum napellus": ["Coffea cruda", "Strychnos nux-vomica"],
        "Apis mellifica": ["Natrum muriaticum", "Ipecacuanha", "Ledum palustre"],
        "Arsenicum album": ["Camphora", "China officinalis", "Hepar sulphuris", "Strychnos nux-vomica"],
        "Atropa belladonna": ["Coffea cruda", "Hepar sulphuris", "Hyoscyamus niger"],
        "Bryonia alba": ["Aconitum napellus", "Camphora", "Chamomilla", "Strychnos nux-vomica"],
        "Calcarea carbonica": ["Camphora", "Nitricum acidum", "Strychnos nux-vomica"],
        "Causticum": ["Coffea cruda", "Colocynthis", "Strychnos nux-vomica"],
        "Digitalis purpurea": ["Camphora", "Opium", "Serpentaria"],
        "Hepar sulphuris": ["Atropa belladonna", "Chamomilla", "Silicea terra"],
        "Ignatia amara": ["Arnica montana", "Camphora", "Chamomilla", "Pulsatilla pratensis"],
        "Lachesis muta": ["Arsenicum album", "Atropa belladonna", "Camphora", "Nitricum acidum"],
        "Lycopodium clavatum": ["Camphora", "Pulsatilla pratensis", "Causticum"],
        "Mercurius solubilis": ["Aurum metallicum", "Hepar sulphuris", "Nitricum acidum", "Sulphur"],
        "Strychnos nux-vomica": ["Aconitum napellus", "Camphora", "Chamomilla", "Coffea cruda"],
        "Phosphorus": ["Camphora", "Coffea cruda", "Strychnos nux-vomica", "Terebinthina"],
        "Pulsatilla pratensis": ["Chamomilla", "Coffea cruda", "Ignatia amara", "Strychnos nux-vomica"],
        "Rhus toxicodendron": ["Anacardium orientale", "Atropa belladonna", "Camphora", "Bryonia alba"],
        "Sepia officinalis": ["Aconitum napellus", "Smilax aspera (Sarsaparilla)", "Sulphur"],
        "Silicea terra": ["Camphora", "Fluoricum acidum", "Hepar sulphuris"],
        "Sulphur": ["Aconitum napellus", "Camphora", "Chamomilla", "Mercurius solubilis", "Pulsatilla pratensis"]
    }

    @classmethod
    def _find_rule(cls, rem1: str, rem2: str) -> Optional[InimicalRule]:
        """Looks up whether two remedies form an inimical pair."""
        r1, r2 = rem1.strip().lower(), rem2.strip().lower()
        for rule in cls.RULES_26:
            a, b = rule.remedy_a.strip().lower(), rule.remedy_b.strip().lower()
            if (r1 == a and r2 == b) or (r1 == b and r2 == a):
                return rule
        return None

    @classmethod
    def evaluate_sequence(
        cls,
        candidate_remedy: str,
        prior_remedy: str,
        days_since_prior: int,
        is_acute_override: bool = False
    ) -> InimicalEvaluation:
        """
        Evaluates the clinical compatibility of prescribing candidate_remedy following prior_remedy.
        """
        rule = cls._find_rule(candidate_remedy, prior_remedy)
        if not rule:
            return InimicalEvaluation(
                candidate_remedy=candidate_remedy,
                prior_remedy=prior_remedy,
                days_since_prior=days_since_prior,
                status=ToxicitySafetyStatus.APPROVED,
                is_acute_override=is_acute_override,
                hazard_description="No known classical inimical or incompatible relationship.",
                clinical_advice="Remedy sequence is clinically permissible."
            )

        # Inimical rule found!
        if days_since_prior < rule.washout_days:
            if is_acute_override:
                return InimicalEvaluation(
                    candidate_remedy=candidate_remedy,
                    prior_remedy=prior_remedy,
                    days_since_prior=days_since_prior,
                    status=ToxicitySafetyStatus.WARNING_OVERRIDABLE,
                    is_acute_override=True,
                    hazard_description=rule.pathogenetic_hazard,
                    clinical_advice=(
                        f"ACUTE INTERCURRENT OVERRIDE ACTIVATED: {candidate_remedy} is traditionally inimical to "
                        f"{prior_remedy} (washout {days_since_prior}/{rule.washout_days} days). "
                        f"Administer only for emergent acute crisis under strict supervision. "
                        f"Clear with indicated acute antidote or placebo upon resolution."
                    )
                )
            else:
                return InimicalEvaluation(
                    candidate_remedy=candidate_remedy,
                    prior_remedy=prior_remedy,
                    days_since_prior=days_since_prior,
                    status=ToxicitySafetyStatus.HARD_BLOCKED,
                    is_acute_override=False,
                    hazard_description=rule.pathogenetic_hazard,
                    clinical_advice=(
                        f"HARD CLINICAL SAFETY BLOCK: {candidate_remedy} is strictly INIMICAL to {prior_remedy}. "
                        f"Only {days_since_prior} days have elapsed since prior administration; "
                        f"minimum required washout period is {rule.washout_days} days. "
                        f"Prescribing this sequence risks severe pathogenesis: {rule.pathogenetic_hazard}"
                    )
                )

        # Washout period elapsed
        return InimicalEvaluation(
            candidate_remedy=candidate_remedy,
            prior_remedy=prior_remedy,
            days_since_prior=days_since_prior,
            status=ToxicitySafetyStatus.APPROVED,
            is_acute_override=is_acute_override,
            hazard_description=f"Inimical relationship exists, but minimum washout of {rule.washout_days} days has elapsed ({days_since_prior} days).",
            clinical_advice="Safe to prescribe as prior action has completely waned."
        )

    @classmethod
    def get_antidotes(cls, remedy_name: str) -> List[str]:
        """Returns classical antidotes for the specified remedy."""
        for name, antidotes in cls.ANTIDOTES.items():
            if name.lower() == remedy_name.strip().lower():
                return antidotes
        return ["Camphora (General universal antidote for vegetable remedies)"]
