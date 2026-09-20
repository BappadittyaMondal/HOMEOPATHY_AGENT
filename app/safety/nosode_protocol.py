"""
Nosodes & Sarcodes Safety Protocol (Phase 24).
Codifies safety firewalls, acute contraindication guards, and posological interval gates
for biological nosodes and endocrine sarcodes per H.C. Allen, Clarke, and Julian.
"""
from typing import Dict, Optional
from pydantic import BaseModel
from app.models.safety import (
    NosodePrescribingRule,
    ToxicitySafetyStatus
)

class NosodeSafetyEvaluation(BaseModel):
    nosode_name: str
    status: ToxicitySafetyStatus
    is_acute_fever_present: bool
    weeks_since_last_dose: Optional[int]
    rule: Optional[NosodePrescribingRule] = None
    clinical_warning: str
    permitted: bool

class NosodeSafetyProtocol:
    """
    Firewall safeguarding against dangerous nosode prescriptions,
    especially during acute fevers, inflammatory crises, or insufficient inter-dose intervals.
    """

    DATABASE: Dict[str, NosodePrescribingRule] = {
        "Psorinum": NosodePrescribingRule(
            nosode_name="Psorinum",
            miasmatic_clearance="Psora (Fundamental chronic deficiency & lack of reaction)",
            acute_contraindication=True,
            min_interval_weeks=12,
            indication_notes="Lack of reaction when well-chosen remedies fail; filthy odor, coldness, severe despair."
        ),
        "Medorrhinum": NosodePrescribingRule(
            nosode_name="Medorrhinum",
            miasmatic_clearance="Sycosis (Hyperplasia, condylomata, catarrh, pelvic pathology)",
            acute_contraindication=True,
            min_interval_weeks=12,
            indication_notes="Suppressed gonorrhea history; relieved at seashore; sleeps in knee-chest position."
        ),
        "Syphilinum": NosodePrescribingRule(
            nosode_name="Syphilinum",
            miasmatic_clearance="Syphilis (Destructive ulceration, tissue decay, nighttime bone pains)",
            acute_contraindication=True,
            min_interval_weeks=12,
            indication_notes="Linear ulcerations, nocturnal bone agony from sunset to sunrise, dread of the night."
        ),
        "Tuberculinum": NosodePrescribingRule(
            nosode_name="Tuberculinum",
            miasmatic_clearance="Tubercular Diathesis (Pseudopsora / Ringworm / Scrofula)",
            acute_contraindication=True,
            min_interval_weeks=12,
            indication_notes="Rapid emaciation despite ravenous appetite; changing symptoms; never given in active phthisis/fever."
        ),
        "Carcinosinum": NosodePrescribingRule(
            nosode_name="Carcinosinum",
            miasmatic_clearance="Carcinomatous dyscrasia (Compound miasm)",
            acute_contraindication=True,
            min_interval_weeks=12,
            indication_notes="High parental expectations, fastidious artistic temperament, family history of cancer."
        ),
        "Pyrogenium": NosodePrescribingRule(
            nosode_name="Pyrogenium",
            miasmatic_clearance="Septic Autointoxication & Pyemia",
            acute_contraindication=False,  # Exception: Indicated in severe acute septic fevers
            min_interval_weeks=1,
            indication_notes="Disparity between pulse and temperature; bed feels hard; septic puerperal fevers."
        ),
        "Anthracinum": NosodePrescribingRule(
            nosode_name="Anthracinum",
            miasmatic_clearance="Gangrenous septic inflammation",
            acute_contraindication=False,  # Acute septic indication
            min_interval_weeks=2,
            indication_notes="Black severe carbuncles with burning unbearable agony; gangrenous sloughing."
        ),
        "Lyssin": NosodePrescribingRule(
            nosode_name="Lyssin",
            miasmatic_clearance="Lyssinic nervous hyperesthesia",
            acute_contraindication=True,
            min_interval_weeks=12,
            indication_notes="Spasms triggered by running water, brilliant light, or drafts of air."
        ),
        "Variolinum": NosodePrescribingRule(
            nosode_name="Variolinum",
            miasmatic_clearance="Post-vaccinal eruptive dyscrasia",
            acute_contraindication=True,
            min_interval_weeks=8,
            indication_notes="Severe backache, pustular eruptions, and post-vaccination constitutional decline."
        )
    }

    @classmethod
    def evaluate_prescription(
        cls,
        nosode_name: str,
        is_acute_fever_or_crisis: bool = False,
        weeks_since_last_dose: Optional[int] = None
    ) -> NosodeSafetyEvaluation:
        """
        Evaluates safety parameters for prescribing a deep biological nosode.
        """
        rule = cls.DATABASE.get(nosode_name)
        if not rule:
            return NosodeSafetyEvaluation(
                nosode_name=nosode_name,
                status=ToxicitySafetyStatus.APPROVED,
                is_acute_fever_present=is_acute_fever_or_crisis,
                weeks_since_last_dose=weeks_since_last_dose,
                rule=None,
                clinical_warning="Remedy is not a restricted deep biological nosode.",
                permitted=True
            )

        # 1. Check acute contraindication
        if rule.acute_contraindication and is_acute_fever_or_crisis:
            return NosodeSafetyEvaluation(
                nosode_name=nosode_name,
                status=ToxicitySafetyStatus.HARD_BLOCKED,
                is_acute_fever_present=True,
                weeks_since_last_dose=weeks_since_last_dose,
                rule=rule,
                clinical_warning=(
                    f"STRICT CLINICAL CONTRAINDICATION: {nosode_name} must NEVER be administered during an active "
                    f"inflammatory acute fever or acute crisis. Risk of violent, irreversible aggravation or vital collapse. "
                    f"Indication must wait until acute phase is resolved by acute remedies."
                ),
                permitted=False
            )

        # 2. Check repetition interval
        if weeks_since_last_dose is not None and weeks_since_last_dose < rule.min_interval_weeks:
            return NosodeSafetyEvaluation(
                nosode_name=nosode_name,
                status=ToxicitySafetyStatus.HARD_BLOCKED,
                is_acute_fever_present=is_acute_fever_or_crisis,
                weeks_since_last_dose=weeks_since_last_dose,
                rule=rule,
                clinical_warning=(
                    f"POSOLOGY LOCKOUT: Only {weeks_since_last_dose} weeks have elapsed since last administration of "
                    f"{nosode_name}. Minimum required interval between chronic doses is {rule.min_interval_weeks} weeks. "
                    f"Premature repetition produces intractable medicinal aggravation."
                ),
                permitted=False
            )

        # Approved
        return NosodeSafetyEvaluation(
            nosode_name=nosode_name,
            status=ToxicitySafetyStatus.APPROVED,
            is_acute_fever_present=is_acute_fever_or_crisis,
            weeks_since_last_dose=weeks_since_last_dose,
            rule=rule,
            clinical_warning=f"Nosode protocol approved. Target miasm: {rule.miasmatic_clearance}.",
            permitted=True
        )
