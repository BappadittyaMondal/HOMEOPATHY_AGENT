"""
Boenninghausen Polarity Analysis & Contraindication Subtraction Engine (Phase 13).
Calculates Polarity Difference (ΔP) and Contraindication Index (CI) to prevent iatrogenic aggravations.
"""
from typing import List, Dict, Tuple
from app.models.polarity import PolarPairDefinition, RemedyPolarityEvaluation

class BoenninghausenPolarityEngine:
    """
    Evaluates polar modality contradictions.
    Remedies with Contraindication Index CI >= 3 are penalized to avoid fatal aggravations.
    """

    POLAR_PAIRS: List[PolarPairDefinition] = [
        PolarPairDefinition(
            pair_id="POLAR-01",
            axis_name="THERMAL_COLD_VS_HEAT",
            positive_rubric="GENERALITIES - COLD - air - agg.",
            negative_rubric="GENERALITIES - WARMTH - agg."
        ),
        PolarPairDefinition(
            pair_id="POLAR-02",
            axis_name="MOTION_VS_REST",
            positive_rubric="EXTREMITIES - PAIN - motion - agg.",
            negative_rubric="EXTREMITIES - PAIN - motion - amel."
        ),
        PolarPairDefinition(
            pair_id="POLAR-03",
            axis_name="PRESSURE_TOUCH_VS_HARD_PRESSURE",
            positive_rubric="GENERALITIES - TOUCH - agg.",
            negative_rubric="HEAD - PAIN - pressure - amel."
        )
    ]

    # Verified Polar Grades Matrix for Core Polychrests (Rubric -> {Remedy -> Grade 1..4})
    POLAR_GRADES: Dict[str, Dict[str, int]] = {
        "GENERALITIES - COLD - air - agg.": {
            "Hepar sulphuris": 4, "Arsenicum album": 3, "Silicea": 3, "Nux vomica": 3,
            "Rhus toxicodendron": 3, "Pulsatilla pratensis": 0, "Sulphur": 1
        },
        "GENERALITIES - WARMTH - agg.": {
            "Pulsatilla pratensis": 3, "Sulphur": 3, "Apis mellifica": 3, "Iodium": 3,
            "Hepar sulphuris": 0, "Arsenicum album": 0, "Silicea": 0
        },
        "EXTREMITIES - PAIN - motion - agg.": {
            "Bryonia alba": 3, "Belladonna": 3, "Colchicum": 3,
            "Rhus toxicodendron": 1
        },
        "EXTREMITIES - PAIN - motion - amel.": {
            "Rhus toxicodendron": 3, "Ruta graveolens": 3, "Rhododendron": 2,
            "Bryonia alba": 0
        },
        "GENERALITIES - TOUCH - agg.": {
            "Hepar sulphuris": 4, "China officinalis": 3, "Lachesis muta": 3, "Spigelia": 2
        },
        "HEAD - PAIN - pressure - amel.": {
            "Bryonia alba": 3, "Magnesia muriatica": 3, "Pulsatilla pratensis": 2, "Argentum nitricum": 2
        }
    }

    @classmethod
    def evaluate_patient_polarities(
        cls, 
        patient_positive_rubrics: List[str], 
        candidate_remedies: List[str]
    ) -> Dict[str, RemedyPolarityEvaluation]:
        """
        Calculates ΔP and CI for each candidate remedy against active patient polarities.
        """
        results: Dict[str, RemedyPolarityEvaluation] = {}

        for remedy in candidate_remedies:
            delta_p = 0
            contra_index = 0
            contra_rubrics = []

            for pair in cls.POLAR_PAIRS:
                # Check if patient has positive polar symptom (e.g. < Cold)
                if pair.positive_rubric in patient_positive_rubrics:
                    pos_grade = cls.POLAR_GRADES.get(pair.positive_rubric, {}).get(remedy, 0)
                    neg_grade = cls.POLAR_GRADES.get(pair.negative_rubric, {}).get(remedy, 0)

                    delta_p += (pos_grade - neg_grade)

                    # If remedy has high grade (>= 3) in opposite modality -> Contraindication!
                    if neg_grade >= 3:
                        contra_index += neg_grade
                        contra_rubrics.append(
                            f"Contraindicated by {pair.negative_rubric} (Grade {neg_grade})"
                        )

                # Check if patient has negative polar symptom (e.g. < Warmth)
                elif pair.negative_rubric in patient_positive_rubrics:
                    pos_grade = cls.POLAR_GRADES.get(pair.positive_rubric, {}).get(remedy, 0)
                    neg_grade = cls.POLAR_GRADES.get(pair.negative_rubric, {}).get(remedy, 0)

                    delta_p += (neg_grade - pos_grade)

                    if pos_grade >= 3:
                        contra_index += pos_grade
                        contra_rubrics.append(
                            f"Contraindicated by {pair.positive_rubric} (Grade {pos_grade})"
                        )

            is_contra = (contra_index >= 3)
            # Penalty factor in [0.0, 1.0]
            penalty = min(1.0, contra_index / 6.0)

            results[remedy] = RemedyPolarityEvaluation(
                remedy_name=remedy,
                polarity_difference=delta_p,
                contraindication_index=contra_index,
                is_contraindicated=is_contra,
                contraindicated_rubrics=contra_rubrics,
                adjusted_penalty_factor=round(penalty, 2)
            )

        return results
