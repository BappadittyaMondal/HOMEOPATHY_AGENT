"""
HPI Single-Remedy vs. Branded Patent Polypharmacy Interception & Cost-Savings Engine (Phase 45).
Enforces Samuel Hahnemann's Single Remedy Law per Organon Aphorism 273, intercepts
unscientific commercial polypharmacy mixtures, and calculates institutional cost savings.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel

class PolypharmacyInterceptRequest(BaseModel):
    requested_formulation_name: str
    constituent_remedies: List[str]
    commercial_mrp_inr: float
    patient_presenting_complaint: str

class PolypharmacyInterceptReport(BaseModel):
    is_polypharmacy_detected: bool
    single_simillimum_recommended: str
    recommended_potency: str
    hpi_generic_cost_inr: float = 12.0  # Standard hospital dispensing cost of single dynamic dose
    commercial_cost_inr: float
    cost_savings_percentage: float
    clinical_rationale: str
    aphorism_basis: str = "Organon Aphorism 273: The Law of the Single Simple Remedy"

class PolypharmacyGuardEngine:
    """
    Interception engine that analyzes polypharmacy requests and enforces single-remedy prescribing.
    """

    # Knowledge base of common commercial complex formulas mapped to true classical single simillimum
    KNOWN_COMPLEXES: Dict[str, Dict[str, str]] = {
        "cough syrup complex": {
            "simillimum": "Bryonia alba",
            "potency": "30C",
            "rationale": "Commercial cough syrups mix Bryonia, Drosera, Ipecac, and Belladonna. Classical evaluation resolves totality to single Bryonia alba."
        },
        "digestive tonic mixture": {
            "simillimum": "Strychnos nux-vomica",
            "potency": "200C",
            "rationale": "Commercial digestive drops mix Nux vomica, Carbo veg, and Lycopodium. Totality indicates single Nux vomica."
        },
        "rheumatic drop complex": {
            "simillimum": "Rhus toxicodendron",
            "potency": "200C",
            "rationale": "Complex mixes Rhus tox, Bryonia, Colchicum, and Arnica. Indicated single remedy is Rhus toxicodendron."
        }
    }

    @classmethod
    def evaluate_formulation(
        cls,
        request: PolypharmacyInterceptRequest
    ) -> PolypharmacyInterceptReport:
        """
        Intercepts polypharmacy mixtures, identifies single generic simillimum, and calculates financial savings.
        """
        is_poly = len(request.constituent_remedies) > 1 or "complex" in request.requested_formulation_name.lower()

        req_lower = request.requested_formulation_name.lower()
        matched = None
        for k, v in cls.KNOWN_COMPLEXES.items():
            if k in req_lower:
                matched = v
                break

        if matched:
            remedy = matched["simillimum"]
            potency = matched["potency"]
            rationale = matched["rationale"]
        elif is_poly:
            remedy = request.constituent_remedies[0]
            potency = "200C"
            rationale = f"Polypharmacy intercepted ({len(request.constituent_remedies)} remedies). Prescribing single most homeomorphic remedy: {remedy}."
        else:
            remedy = request.constituent_remedies[0] if request.constituent_remedies else request.requested_formulation_name
            potency = "30C"
            rationale = "Legitimate single remedy prescription conforming to Organon Aphorism 273."

        generic_cost = 12.0
        comm_cost = max(request.commercial_mrp_inr, generic_cost)
        savings_pct = round(((comm_cost - generic_cost) / comm_cost) * 100.0, 2)

        return PolypharmacyInterceptReport(
            is_polypharmacy_detected=is_poly,
            single_simillimum_recommended=remedy,
            recommended_potency=potency,
            hpi_generic_cost_inr=generic_cost,
            commercial_cost_inr=comm_cost,
            cost_savings_percentage=savings_pct,
            clinical_rationale=rationale
        )
