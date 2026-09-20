"""
Musculoskeletal, Rheumatic & Pain Modality Analysis Engine (Phase 34).
Codifies polar motion modalities (Bryonia vs Rhus tox), periosteal affinities (Ruta),
and cryogenic modalities (Ledum) per Boenninghausen, Kent, and Boger.
"""
from typing import Optional
from app.models.clinical import MusculoskeletalModality, RheumaticPrescription

class MusculoskeletalEngine:
    """
    Evaluates musculoskeletal, joint, and periosteal syndromes
    based on kinetic and thermal modalities.
    """

    @classmethod
    def evaluate_rheumatic_case(cls, modality: MusculoskeletalModality) -> RheumaticPrescription:
        """
        Determines indicated rheumatic simillimum.
        """
        # 1. Ledum: Cold to touch, better cold applications, ascending rheumatism
        if modality.temperature_modality == "BETTER_COLD_APPLICATIONS":
            return RheumaticPrescription(
                indicated_remedy="Ledum palustre",
                recommended_potency="200C",
                tissue_affinity=(
                    "Small joints, gouty nodosities, ascending rheumatism (feet to knees). "
                    "Joints lack vital heat, cold to touch, yet dramatically ameliorated by ice-cold bathing."
                )
            )

        # 2. Ruta: Periosteum, flexor tendons, cartilages
        if modality.tissue_involved == "PERIOSTEUM_TENDONS":
            return RheumaticPrescription(
                indicated_remedy="Ruta graveolens",
                recommended_potency="30C",
                tissue_affinity=(
                    "Periosteum, cartilages, and flexor tendon insertions. Severe bruised, beaten ache "
                    "following sprains, repetitive tendonitis, or periosteal injury."
                )
            )

        # 3. Bryonia: Aggravation from slightest motion, relief from absolute rest
        if modality.motion_modality == "WORSE_ANY_SLIGHTEST_MOTION":
            return RheumaticPrescription(
                indicated_remedy="Bryonia alba",
                recommended_potency="200C",
                tissue_affinity=(
                    "Serous synovial membranes; acute synovitis with hot pale-red effusion. "
                    "Extreme aggravation from the slightest movement; relief from absolute quiet and hard pressure."
                )
            )

        # 4. Rhus Tox: Worse first motion, better continued motion, worse damp cold
        if modality.motion_modality == "WORSE_FIRST_MOTION_BETTER_CONTINUED" or modality.motion_modality == "RESTLESS_MUST_MOVE":
            return RheumaticPrescription(
                indicated_remedy="Rhus toxicodendron",
                recommended_potency="200C",
                tissue_affinity=(
                    "Fibrous tissue, tendons, and ligaments. Pain and stiffness on first beginning to move, "
                    "gradually passing off on continued gentle motion; aggravated by cold damp weather."
                )
            )

        # Default fallback
        return RheumaticPrescription(
            indicated_remedy="Rhus toxicodendron",
            recommended_potency="30C",
            tissue_affinity="Fibromuscular constitutional support."
        )
