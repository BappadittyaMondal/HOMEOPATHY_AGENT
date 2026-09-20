"""
Mental Health, Neuro-Psychiatric & Grief/Emotional Trauma Engine (Phase 30).
Codifies Samuel Hahnemann's Organon Aphorisms 210-230 on mental diseases,
etiology of grief, mortification, suppressed anger, and dispositional concordances.
"""
from typing import List, Optional
from app.models.clinical import PsychiatricEtiologyProfile, MentalHealthPrescription

class MentalHealthEngine:
    """
    Evaluates emotional trauma, chronic grief, and psychiatric dispositions
    in accordance with Hahnemannian somatopsychic principles.
    """

    @classmethod
    def evaluate_psychiatric_case(cls, profile: PsychiatricEtiologyProfile) -> MentalHealthPrescription:
        """
        Synthesizes emotional etiology and mood modalities into indicated simillimum.
        """
        concomitants_str = " ".join(profile.somatic_concomitants).lower()

        # 1. Profound Suicidal Melancholia / Guilt
        if profile.mood_state == "DEEP_MELANCHOLY_SUICIDAL" or "suicide" in concomitants_str or "neglected duty" in concomitants_str:
            return MentalHealthPrescription(
                indicated_remedy="Aurum metallicum",
                recommended_potency="1M",
                clinical_guidance=(
                    "EMERGENCY PSYCHIATRIC RED FLAG: Severe psychotic depression, religious melancholy, utter despair. "
                    "Feels unpardonable guilt and desires death. Ambulatory dispensing locked; requires immediate "
                    "24/7 psychiatric emergency crisis evaluation per Mental Healthcare Act 2017."
                )
            )

        # 2. Acute Silent Grief & Hysterical Paradoxes
        if profile.primary_etiology == "SILENT_GRIEF" and (
            profile.mood_state == "HYSTERICAL_PARADOX"
            or "sighing" in concomitants_str
            or "globus" in concomitants_str
        ):
            return MentalHealthPrescription(
                indicated_remedy="Ignatia amara",
                recommended_potency="200C",
                clinical_guidance=(
                    "Acute grief, recent bereavement, sudden romantic disappointment. "
                    "Involuntary deep sighing, paradoxical physical symptoms, globus hystericus."
                )
            )

        # 3. Suppressed Anger, Indignation, Mortification
        if profile.primary_etiology == "MORTIFICATION_SUPPRESSED_ANGER" or "trembling from anger" in concomitants_str:
            return MentalHealthPrescription(
                indicated_remedy="Staphysagria",
                recommended_potency="200C",
                clinical_guidance=(
                    "Ill-effects of suppressed rage, wounded honor, and indignation. "
                    "Patient suffers silently but trembles with indignation; throws objects when provoked."
                )
            )

        # 4. Chronic Long-standing Grief, Consolation Aggravates
        if profile.mood_state == "WEEPING_CONSOLATION_AGGRAVATES" or (
            profile.primary_etiology == "SILENT_GRIEF" and "dwelling on past" in concomitants_str
        ):
            return MentalHealthPrescription(
                indicated_remedy="Natrum muriaticum",
                recommended_potency="200C",
                clinical_guidance=(
                    "Inveterate chronic grief, brooding over past insults, weeping in solitude. "
                    "Consolation enrages the patient. Craving for salt and aversion to sunlight."
                )
            )

        # 5. Acute Sudden Terror / Panic with Fear of Death
        if profile.primary_etiology == "FRIGHT_SUDDEN_TERROR" or "fear of death" in concomitants_str:
            return MentalHealthPrescription(
                indicated_remedy="Aconitum napellus",
                recommended_potency="200C",
                clinical_guidance=(
                    "Acute post-traumatic panic state, intense agony, and restlessness. "
                    "Patient predicts the exact hour of death; extreme tachycardia and dread."
                )
            )

        # 6. Gentle, Weeping, Consolation Ameliorates
        if profile.mood_state == "WEEPING_CONSOLATION_AMELIORATES":
            return MentalHealthPrescription(
                indicated_remedy="Pulsatilla pratensis",
                recommended_potency="30C",
                clinical_guidance=(
                    "Mild, yielding disposition; weeps easily while describing symptoms. "
                    "Comforted and ameliorated by kind words, sympathy, and cool fresh air."
                )
            )

        # Default fallback
        return MentalHealthPrescription(
            indicated_remedy="Natrum muriaticum",
            recommended_potency="200C",
            clinical_guidance="Deep emotional stabilization and trauma resolution."
        )
