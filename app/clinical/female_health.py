"""
Female Reproductive Health, Menstrual Modalities & Obstetric Engine (Phase 29).
Codifies gynecological modalities, flow dynamics, bearing-down sensations,
and menstrual concordances per Kent, Guernsey, and Clarke.
"""
from typing import List, Optional
from app.models.clinical import MenstrualModalityProfile, FemaleHealthPrescription

class FemaleHealthEngine:
    """
    Evaluates gynecological symptom totality, flow rhythms, and pelvic concomitants.
    """

    @classmethod
    def evaluate_menstrual_case(cls, profile: MenstrualModalityProfile) -> FemaleHealthPrescription:
        """
        Determines the gynecological simillimum based on cycle modalities and concomitants.
        """
        concomitants_str = " ".join(profile.concomitants).lower()

        # 1. Bearing-down / Pelvic Prolapse
        if "bearing down" in concomitants_str or "cross legs" in concomitants_str or "indifference" in concomitants_str:
            return FemaleHealthPrescription(
                indicated_remedy="Sepia officinalis",
                recommended_potency="200C",
                clinical_focus="Pelvic relaxation, uterine prolapse, chloasma, and profound emotional indifference.",
                key_concordance="Sepia: Sensation of pelvic contents protruding through vulva; must cross limbs tightly."
            )

        # 2. Amelioration as soon as flow establishes
        if profile.modality_with_flow == "BETTER_WHEN_FLOW_FLOWS" or "left ovary" in concomitants_str:
            return FemaleHealthPrescription(
                indicated_remedy="Lachesis muta",
                recommended_potency="200C",
                clinical_focus="Premenstrual tension, left ovarian neuralgia, climacteric flushes.",
                key_concordance="Lachesis: Dramatic amelioration of all somatic and mental distress upon flow onset."
            )

        # 3. Delayed, Scanty, Suppressed from wet feet, Changeable
        if profile.flow_timing == "DELAYED_SUPPRESSED" or profile.flow_nature == "SCANTY" or "weeps easily" in concomitants_str:
            return FemaleHealthPrescription(
                indicated_remedy="Pulsatilla pratensis",
                recommended_potency="30C",
                clinical_focus="Amenorrhea, delayed menarche, scanty changeable flow, weeping disposition.",
                key_concordance="Pulsatilla: Suppressed menses from getting feet chilled; wandering pelvic pains."
            )

        # 4. Severe pain proportional to volume of flow
        if profile.modality_with_flow == "PAIN_PROPORTIONAL_TO_FLOW":
            return FemaleHealthPrescription(
                indicated_remedy="Cimicifuga racemosa",
                recommended_potency="200C",
                clinical_focus="Neuralgic dysmenorrhea, inframammary pains, shooting pains across pelvis.",
                key_concordance="Cimicifuga: Paroxysmal uterine cramps increase in severity as menstrual flow increases."
            )

        # 5. Profuse metrorrhagia from sacrum to pubes
        if profile.flow_nature == "PROFUSE_METRORRHAGIC" or "sacrum to pubes" in concomitants_str:
            return FemaleHealthPrescription(
                indicated_remedy="Sabina",
                recommended_potency="30C",
                clinical_focus="Uterine hemorrhage, threatened miscarriage, expulsion of large dark clots.",
                key_concordance="Sabina: Intense shooting pains radiating from sacrum through to pubic bone."
            )

        # Default fallback
        return FemaleHealthPrescription(
            indicated_remedy="Pulsatilla pratensis",
            recommended_potency="30C",
            clinical_focus="General hormonal balance and menstrual regulation.",
            key_concordance="Classical endocrine and venous regulator."
        )
