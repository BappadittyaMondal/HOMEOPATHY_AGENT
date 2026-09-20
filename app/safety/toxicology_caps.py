"""
Statutory Toxicology Limits & Alkaloid Safety Firewall (Phase 19).
Codifies the 20-Point Mother Tincture (Q) Limits, Schedule E(1) statutory controls,
and minimum dispensing potency thresholds per the Drugs and Cosmetics Act and HPI.
"""
from typing import Dict, Optional
import re
from app.models.safety import (
    MotherTinctureToxicityRule,
    ToxicologyCheckResult,
    ToxicitySafetyStatus
)

class ToxicologySafetyFirewall:
    """
    Production-grade statutory safety firewall enforcing strict toxicology thresholds,
    alkaloid safety caps, and non-overridable blocks on hazardous mother tinctures.
    """

    RULES_20: Dict[str, MotherTinctureToxicityRule] = {
        "Aconitum napellus": MotherTinctureToxicityRule(
            remedy_name="Aconitum napellus",
            toxic_constituent="Aconitine alkaloid",
            max_daily_dose_ml=0.0,
            banned_below_potency="3X",
            clinical_hazard="Lethal cardiac arrhythmia and sensory nerve paralysis. Pure aconitine LD50 is 0.1-0.2 mg/kg."
        ),
        "Arsenicum album": MotherTinctureToxicityRule(
            remedy_name="Arsenicum album",
            toxic_constituent="Arsenic trioxide (As2O3)",
            max_daily_dose_ml=0.0,
            banned_below_potency="6X",
            clinical_hazard="Cellular respiration enzyme poisoning, capillary damage, acute hemorrhagic gastroenteritis."
        ),
        "Atropa belladonna": MotherTinctureToxicityRule(
            remedy_name="Atropa belladonna",
            toxic_constituent="Hyoscyamine, Atropine, Scopolamine",
            max_daily_dose_ml=0.3,
            banned_below_potency="2X",
            clinical_hazard="Severe anticholinergic toxidrome: hyperthermia, mydriasis, delirium, tachyarrhythmias."
        ),
        "Strychnos nux-vomica": MotherTinctureToxicityRule(
            remedy_name="Strychnos nux-vomica",
            toxic_constituent="Strychnine & Brucine indole alkaloids",
            max_daily_dose_ml=0.5,
            banned_below_potency="2X",
            clinical_hazard="Glycine receptor antagonism producing reflex tetanic convulsions and asphyxia."
        ),
        "Digitalis purpurea": MotherTinctureToxicityRule(
            remedy_name="Digitalis purpurea",
            toxic_constituent="Digitoxin, Digoxin cardiac glycosides",
            max_daily_dose_ml=0.2,
            banned_below_potency="3X",
            clinical_hazard="Inhibition of Na+/K+-ATPase, hyperkalemia, heart block, ventricular tachycardia."
        ),
        "Gelsemium sempervirens": MotherTinctureToxicityRule(
            remedy_name="Gelsemium sempervirens",
            toxic_constituent="Gelsemine, Sempervirine",
            max_daily_dose_ml=0.5,
            banned_below_potency="2X",
            clinical_hazard="Central nervous system depression, diplopia, ptosis, and respiratory failure."
        ),
        "Conium maculatum": MotherTinctureToxicityRule(
            remedy_name="Conium maculatum",
            toxic_constituent="Coniine alkaloid",
            max_daily_dose_ml=0.2,
            banned_below_potency="3X",
            clinical_hazard="Nicotinic acetylcholine receptor blocker causing ascending flaccid paralysis."
        ),
        "Hyoscyamus niger": MotherTinctureToxicityRule(
            remedy_name="Hyoscyamus niger",
            toxic_constituent="Hyoscyamine, Scopolamine",
            max_daily_dose_ml=0.3,
            banned_below_potency="2X",
            clinical_hazard="Anticholinergic central delirium, visual hallucinations, and urinary retention."
        ),
        "Cantharis vesicatoria": MotherTinctureToxicityRule(
            remedy_name="Cantharis vesicatoria",
            toxic_constituent="Cantharidin terpenoid",
            max_daily_dose_ml=0.1,
            banned_below_potency="3X",
            clinical_hazard="Severe mucosal blistering, acute tubular necrosis, and violent priapism."
        ),
        "Secale cornutum": MotherTinctureToxicityRule(
            remedy_name="Secale cornutum",
            toxic_constituent="Ergotamine, Ergotoxine peptide alkaloids",
            max_daily_dose_ml=0.2,
            banned_below_potency="3X",
            clinical_hazard="Peripheral alpha-adrenergic vasospasm, dry gangrene, and uterine tetany."
        ),
        "Lachesis muta": MotherTinctureToxicityRule(
            remedy_name="Lachesis muta",
            toxic_constituent="Lachesis muta phospholipase & hemorrhagin venom",
            max_daily_dose_ml=0.0,
            banned_below_potency="6C",
            clinical_hazard="Disseminated intravascular coagulation (DIC), severe hemolysis, and tissue necrosis."
        ),
        "Crotalus horridus": MotherTinctureToxicityRule(
            remedy_name="Crotalus horridus",
            toxic_constituent="Crotalid venom zinc metalloproteinases",
            max_daily_dose_ml=0.0,
            banned_below_potency="6C",
            clinical_hazard="Systemic hemorrhagic diathesis, defibrinogenation, and microvascular shock."
        ),
        "Naja tripudians": MotherTinctureToxicityRule(
            remedy_name="Naja tripudians",
            toxic_constituent="Elapid neurotoxins (Cobratoxin)",
            max_daily_dose_ml=0.0,
            banned_below_potency="6C",
            clinical_hazard="Post-synaptic neuromuscular blockade and bulbar respiratory arrest."
        ),
        "Opium": MotherTinctureToxicityRule(
            remedy_name="Opium",
            toxic_constituent="Morphine, Codeine, Thebaine phenanthrene alkaloids",
            max_daily_dose_ml=0.2,
            banned_below_potency="3X",
            clinical_hazard="Mu-opioid respiratory arrest, pupillary miosis, coma. Governed under NDPS Act."
        ),
        "Cannabis sativa": MotherTinctureToxicityRule(
            remedy_name="Cannabis sativa",
            toxic_constituent="Delta-9-THC cannabinoids",
            max_daily_dose_ml=0.3,
            banned_below_potency="2X",
            clinical_hazard="Psychoactive dissociation, panic tachycardia, and psychomotor impairment."
        ),
        "Colchicum autumnale": MotherTinctureToxicityRule(
            remedy_name="Colchicum autumnale",
            toxic_constituent="Colchicine alkaloid",
            max_daily_dose_ml=0.2,
            banned_below_potency="3X",
            clinical_hazard="Mitotic spindle inhibition, multi-organ failure, and gastrointestinal necrosis."
        ),
        "Veratrum album": MotherTinctureToxicityRule(
            remedy_name="Veratrum album",
            toxic_constituent="Protoveratrine steroidal alkaloids",
            max_daily_dose_ml=0.2,
            banned_below_potency="3X",
            clinical_hazard="Bezold-Jarisch reflex: severe vagal bradycardia and hypotensive shock."
        ),
        "Plumbum metallicum": MotherTinctureToxicityRule(
            remedy_name="Plumbum metallicum",
            toxic_constituent="Inorganic Lead (Pb)",
            max_daily_dose_ml=0.0,
            banned_below_potency="6X",
            clinical_hazard="Encephalopathy, wrist-drop motor neuropathy, and chronic lead nephropathy."
        ),
        "Mercurius solubilis": MotherTinctureToxicityRule(
            remedy_name="Mercurius solubilis",
            toxic_constituent="Elemental & inorganic mercury compounds",
            max_daily_dose_ml=0.0,
            banned_below_potency="6X",
            clinical_hazard="Mercurialism: stomatitis, severe renal proximal tubule necrosis, and erethism."
        ),
        "Phosphorus": MotherTinctureToxicityRule(
            remedy_name="Phosphorus",
            toxic_constituent="Yellow/White Elemental Phosphorus",
            max_daily_dose_ml=0.0,
            banned_below_potency="3X",
            clinical_hazard="Acute yellow atrophy of liver, fatty degeneration, and spontaneous hemorrhage."
        )
    }

    @staticmethod
    def _potency_to_decimal_dilution_factor(potency_str: str) -> float:
        """
        Converts homeopathic potency notation into equivalent decimal dilution exponents (X scale).
        e.g.:
        Q / MT / Theta / 0 -> 0.0 (Undiluted Mother Tincture)
        1X -> 1.0, 2X -> 2.0, 3X -> 3.0, 6X -> 6.0
        1C -> 2.0, 2C -> 4.0, 3C -> 6.0, 6C -> 12.0, 30C -> 60.0, 200C -> 400.0, 1M -> 2000.0
        LM 0/1 -> 50000.0 (Infinitesimal)
        """
        p = potency_str.strip().upper()
        if p in ["Q", "MT", "0", "\u03b8", "THETA", "MOTHER TINCTURE"]:
            return 0.0

        if "LM" in p or "0/" in p or "Q" in p and ("/" in p):
            return 50000.0

        if "M" in p and not ("LM" in p):
            # e.g., 1M = 1000C = 2000X, 10M = 20000X, 50M = 100000X, CM = 200000X
            num_match = re.match(r"^(\d+)\s*M$", p)
            if num_match:
                mult = int(num_match.group(1))
                return float(mult * 2000.0)
            if p == "CM":
                return 200000.0

        # Match Centesimal (C or CH or CK)
        c_match = re.match(r"^(\d+)\s*(C|CH|CK)?$", p)
        if c_match and (c_match.group(2) or int(c_match.group(1)) > 12):
            val = int(c_match.group(1))
            return float(val * 2.0)

        # Match Decimal (X or D or DH)
        x_match = re.match(r"^(\d+)\s*(X|D|DH)$", p)
        if x_match:
            return float(x_match.group(1))

        # Default fallback
        return 0.0

    @classmethod
    def evaluate_prescription(
        cls,
        remedy_name: str,
        potency: str,
        daily_dose_ml: float = 0.0
    ) -> ToxicologyCheckResult:
        """
        Evaluates a candidate prescription against the 20-Point Statutory Toxicology Firewall.
        Returns safety status, blocking violation if any, and clinical guidance.
        """
        rule = cls.RULES_20.get(remedy_name)
        if not rule:
            # Remedy is not in the toxic 20 list; approved by default
            return ToxicologyCheckResult(
                remedy_name=remedy_name,
                requested_potency=potency,
                requested_daily_dose_ml=daily_dose_ml,
                status=ToxicitySafetyStatus.APPROVED,
                rule_matched=None,
                reason="Remedy is not subject to high-toxicity statutory restriction.",
                statutory_reference="HPI General Standards / Safe Non-Toxic Class"
            )

        requested_factor = cls._potency_to_decimal_dilution_factor(potency)
        banned_factor = cls._potency_to_decimal_dilution_factor(rule.banned_below_potency)

        # 1. Check if potency is below statutory minimum safe potency
        if requested_factor < banned_factor:
            return ToxicologyCheckResult(
                remedy_name=remedy_name,
                requested_potency=potency,
                requested_daily_dose_ml=daily_dose_ml,
                status=ToxicitySafetyStatus.HARD_BLOCKED,
                rule_matched=rule,
                reason=(
                    f"STATUTORY SAFETY VIOLATION: {remedy_name} at potency '{potency}' is strictly prohibited. "
                    f"Statutory minimum allowed potency is {rule.banned_below_potency}. "
                    f"Toxicity hazard: {rule.clinical_hazard}"
                ),
                statutory_reference="Drugs & Cosmetics Act Schedule E(1) & HPI Monograph Standards"
            )

        # 2. If it is mother tincture (requested_factor == 0.0), check daily dose limits
        if requested_factor == 0.0:
            if rule.max_daily_dose_ml == 0.0:
                return ToxicologyCheckResult(
                    remedy_name=remedy_name,
                    requested_potency=potency,
                    requested_daily_dose_ml=daily_dose_ml,
                    status=ToxicitySafetyStatus.HARD_BLOCKED,
                    rule_matched=rule,
                    reason=(
                        f"STATUTORY PROHIBITION: Mother Tincture (Q) of {remedy_name} is strictly prohibited "
                        f"under Indian and international pharmacopoeias due to extreme toxicity ({rule.toxic_constituent})."
                    ),
                    statutory_reference="Drugs & Cosmetics Act Schedule E(1) Rule 106B"
                )

            if daily_dose_ml > rule.max_daily_dose_ml:
                return ToxicologyCheckResult(
                    remedy_name=remedy_name,
                    requested_potency=potency,
                    requested_daily_dose_ml=daily_dose_ml,
                    status=ToxicitySafetyStatus.HARD_BLOCKED,
                    rule_matched=rule,
                    reason=(
                        f"MAXIMUM DOSE EXCEEDED: Daily dose of {daily_dose_ml:.2f} mL exceeds the statutory maximum "
                        f"threshold of {rule.max_daily_dose_ml:.2f} mL for {remedy_name} Q. Hazard: {rule.clinical_hazard}"
                    ),
                    statutory_reference="HPI Vol I-IX Toxic Substance Max Limit"
                )
            elif daily_dose_ml > (0.8 * rule.max_daily_dose_ml):
                return ToxicologyCheckResult(
                    remedy_name=remedy_name,
                    requested_potency=potency,
                    requested_daily_dose_ml=daily_dose_ml,
                    status=ToxicitySafetyStatus.WARNING_OVERRIDABLE,
                    rule_matched=rule,
                    reason=(
                        f"CLINICAL CAUTION: Daily dose {daily_dose_ml:.2f} mL approaches maximum safe ceiling "
                        f"({rule.max_daily_dose_ml:.2f} mL). Continuous therapeutic monitoring required."
                    ),
                    statutory_reference="HPI Safe Dispensing Protocol"
                )

        # Passed all checks
        return ToxicologyCheckResult(
            remedy_name=remedy_name,
            requested_potency=potency,
            requested_daily_dose_ml=daily_dose_ml,
            status=ToxicitySafetyStatus.APPROVED,
            rule_matched=rule,
            reason=f"Prescription conforms to statutory dilution ({rule.banned_below_potency}+) and toxicology safety caps.",
            statutory_reference="Drugs & Cosmetics Act Schedule E(1) & HPI Monograph Standards"
        )
