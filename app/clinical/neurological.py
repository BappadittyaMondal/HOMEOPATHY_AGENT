"""
Neurological, Migraine & Cephalic Topography Repertory Engine (Phase 37).
Codifies lateral cephalic pathways (Spigelia left vs Sanguinaria right),
occipital urinary relief vectors (Gelsemium), and thermal envelopment relief (Silicea) per Kent and Allen.
"""
from typing import Optional
from app.models.clinical import CephalicTopographyProfile, NeurologicalPrescription

class NeurologicalEngine:
    """
    Evaluates cephalalgia, migraines, and cranial neuralgias based on anatomical topography,
    laterality vectors, and characteristic physical concomitants.
    """

    @classmethod
    def evaluate_neurological_case(cls, profile: CephalicTopographyProfile) -> NeurologicalPrescription:
        """
        Synthesizes neurological cephalalgia profile and returns indicated simillimum.
        """
        # 1. Spigelia: Left supraorbital neuralgia, sun-clock pattern
        if profile.laterality == "LEFT_SIDED" or profile.pain_pathway == "LEFT_SUPRAORBITAL_TO_OCCIPUT":
            return NeurologicalPrescription(
                indicated_remedy="Spigelia anthelmia",
                recommended_potency="200C",
                cephalic_affinity=(
                    "Left-sided supraorbital neuralgia. Pain radiates from occiput forward and settles "
                    "over the left eye and orbit; follows sun clock (increases with sunrise, declines with sunset); "
                    "extreme soreness of left eyeball."
                )
            )

        # 2. Sanguinaria: Right-sided migraine, begins in occiput, settles over right eye
        if profile.pain_pathway == "OCCIPUT_OVER_VERTEX_SETTLING_RIGHT_EYE" or (
            profile.laterality == "RIGHT_SIDED" and "right eye" in profile.pain_pathway.lower()
        ):
            return NeurologicalPrescription(
                indicated_remedy="Sanguinaria canadensis",
                recommended_potency="200C",
                cephalic_affinity=(
                    "American sick headache. Begins in occiput and cervical nape, spreads over vertex, "
                    "and settles over the right eye and temple. Relieved by quiet darkness, sleep, and bilious vomiting."
                )
            )

        # 3. Gelsemium: Occipital heaviness, ptosis, dramatically relieved by profuse urination
        if "profuse_urination" in profile.associated_symptom.lower() or "ptosis" in profile.associated_symptom.lower():
            return NeurologicalPrescription(
                indicated_remedy="Gelsemium sempervirens",
                recommended_potency="200C",
                cephalic_affinity=(
                    "Congestive occipital headache with profound dullness, dizziness, and heavy drooping eyelids (ptosis). "
                    "Feeling of tight band around forehead; dramatic, immediate relief after passing copious pale urine."
                )
            )

        # 4. Silicea: Nape ascending to vertex, relieved by warm wrapping
        if profile.pain_pathway == "NAPE_ASCENDING_UPWARDS" or "warm" in profile.associated_symptom.lower():
            return NeurologicalPrescription(
                indicated_remedy="Silicea terra",
                recommended_potency="200C",
                cephalic_affinity=(
                    "Chronic nervous headache originating in the nape of neck, ascending over vertex to settle "
                    "in right forehead/orbit. Chilly patient, intensely ameliorated by wrapping head up thickly and warmly."
                )
            )

        # 5. Belladonna: Violent throbbing, vascular right-sided congestion
        if "throbbing" in profile.associated_symptom.lower() or profile.laterality == "RIGHT_SIDED":
            return NeurologicalPrescription(
                indicated_remedy="Belladonna",
                recommended_potency="200C",
                cephalic_affinity=(
                    "Acute congestive vascular cephalalgia; throbbing temporal arteries and carotids; "
                    "hot flushed red face, dilated pupils, worse jarring, light, and noise."
                )
            )

        # Default fallback
        return NeurologicalPrescription(
            indicated_remedy="Belladonna",
            recommended_potency="30C",
            cephalic_affinity="General cephalic vascular and nervous support."
        )
