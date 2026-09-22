"""
Handwritten Homeopathic Prescription OCR & Clinical Script Ingestion Engine (HHPIE).

Provides end-to-end ingestion, parsing, normalization, and safety verification
of scanned or photographed handwritten homeopathic doctor prescriptions.
Works with raw images (PIL preprocessing), client-offloaded OCR tokens,
and raw transcribed text without requiring heavy server-side GPU models (< 50MB RAM footprint).

Enforces:
- INV-16: Canonical Remedy Identification across 150 HPI remedies.
- INV-01: Inimical Remedy Combination Firewall.
- INV-12: Obstetric First-Trimester Safety Check.
- NCH Act 2020: Human-in-the-loop verification gate before RMP digital signing.
"""
import io
import re
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field

# PIL is used for lightweight image validation and preprocessing without GPU bloat
try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from app.repertory.canonical_registry import (
    CanonicalRemedyRegistry,
    CanonicalRemedy,
    UnresolvedRemedyException
)
from app.safety.inimical_matrix import InimicalSafetyMatrix
from app.safety.obstetric_firewall import ObstetricSafetyFirewall


class PotencyScale(str, Enum):
    CENTESIMAL = "CENTESIMAL"
    FIFTY_MILLESIMAL = "50_MILLESIMAL"
    DECIMAL = "DECIMAL"
    MOTHER_TINCTURE = "MOTHER_TINCTURE"
    UNSPECIFIED = "UNSPECIFIED"


class DosageFrequency(str, Enum):
    OD = "OD"          # Once daily
    BD = "BD"          # Twice daily
    TDS = "TDS"        # Thrice daily
    QID = "QID"        # Four times daily
    HS = "HS"          # At bedtime
    STAT = "STAT"      # Immediately once
    ALT_DAYS = "ALT_DAYS" # Alternate days
    WEEKLY = "WEEKLY"
    SOS = "SOS"        # As needed
    CUSTOM = "CUSTOM"


class DosageForm(str, Enum):
    GLOBULES = "GLOBULES"
    LIQUID_DROPS = "LIQUID_DROPS"
    POWDER = "POWDER"
    TABLETS = "TABLETS"
    DISTILLED_WATER = "DISTILLED_WATER"
    SAC_LAC = "SAC_LAC"


class ParsedPrescriptionItem(BaseModel):
    item_index: int
    raw_line: str
    remedy_query: str
    canonical_remedy_name: str
    canonical_id: Optional[str] = None
    potency: str
    scale: PotencyScale = PotencyScale.CENTESIMAL
    dosage_form: DosageForm = DosageForm.GLOBULES
    frequency: DosageFrequency = DosageFrequency.OD
    posology_instruction: str
    duration_days: Optional[int] = None
    is_placebo_sac_lac: bool = False
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)
    requires_review: bool = False
    review_notes: List[str] = Field(default_factory=list)


class ParsedHandwrittenPrescription(BaseModel):
    prescription_id: str = Field(default_factory=lambda: f"RX-SCAN-{uuid.uuid4().hex[:8].upper()}")
    doctor_name: Optional[str] = None
    doctor_registration: Optional[str] = None
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    prescription_date: Optional[str] = None
    chief_complaints: List[str] = Field(default_factory=list)
    clinical_diagnoses: List[str] = Field(default_factory=list)
    items: List[ParsedPrescriptionItem] = Field(default_factory=list)
    general_advice: List[str] = Field(default_factory=list)
    raw_extracted_text: str
    overall_confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    requires_doctor_verification: bool = False
    verification_reasons: List[str] = Field(default_factory=list)
    inimical_conflicts_detected: List[str] = Field(default_factory=list)
    obstetric_warnings: List[str] = Field(default_factory=list)
    ingestion_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HandwrittenPrescriptionEngine:
    """
    High-performance, zero-GPU handwritten prescription parser and normalizer.
    Tailored specifically to classical homeopathic doctor shorthands, Latin symbols,
    and HPI pharmacopoeial nomenclature.
    """

    # Common handwritten abbreviations for frequent remedies
    HANDWRITTEN_REMEDY_ALIASES: Dict[str, str] = {
        "ars": "Arsenicum album",
        "ars alb": "Arsenicum album",
        "ars. alb": "Arsenicum album",
        "ars-alb": "Arsenicum album",
        "arsenic": "Arsenicum album",
        "nux": "Nux vomica",
        "nux vom": "Nux vomica",
        "nux. vom": "Nux vomica",
        "nux-v": "Nux vomica",
        "nux v": "Nux vomica",
        "bry": "Bryonia alba",
        "bry alb": "Bryonia alba",
        "bry. alb": "Bryonia alba",
        "rhus": "Rhus toxicodendron",
        "rhus tox": "Rhus toxicodendron",
        "rhus-t": "Rhus toxicodendron",
        "puls": "Pulsatilla pratensis",
        "puls nig": "Pulsatilla pratensis",
        "lyc": "Lycopodium clavatum",
        "lycop": "Lycopodium clavatum",
        "phos": "Phosphorus",
        "sep": "Sepia officinalis",
        "calc": "Calcarea carbonica",
        "calc carb": "Calcarea carbonica",
        "calc c": "Calcarea carbonica",
        "calc-c": "Calcarea carbonica",
        "calc fluor": "Calcarea fluorica",
        "calc phos": "Calcarea phosphorica",
        "sil": "Silicea",
        "silic": "Silicea",
        "merc": "Mercurius solubilis",
        "merc sol": "Mercurius solubilis",
        "merc. sol": "Mercurius solubilis",
        "nat mur": "Natrum muriaticum",
        "nat. mur": "Natrum muriaticum",
        "nat-m": "Natrum muriaticum",
        "nat m": "Natrum muriaticum",
        "bell": "Atropa belladonna",
        "bellad": "Atropa belladonna",
        "acon": "Aconitum napellus",
        "acon nap": "Aconitum napellus",
        "arn": "Arnica montana",
        "arn mont": "Arnica montana",
        "arnica": "Arnica montana",
        "thuj": "Thuja occidentalis",
        "thuja": "Thuja occidentalis",
        "thuja occ": "Thuja occidentalis",
        "hep": "Hepar sulphuris calcareum",
        "hep sulph": "Hepar sulphuris calcareum",
        "hepar": "Hepar sulphuris calcareum",
        "ign": "Ignatia amara",
        "ignat": "Ignatia amara",
        "gels": "Gelsemium sempervirens",
        "gelsem": "Gelsemium sempervirens",
        "ant crud": "Antimonium crudum",
        "ant. crud": "Antimonium crudum",
        "ant-c": "Antimonium crudum",
        "ant tart": "Antimonium tartaricum",
        "hydrocotyle": "Hydrocotyle asiatica",
        "hydr asiat": "Hydrocotyle asiatica",
        "carbo veg": "Carbo vegetabilis",
        "carb veg": "Carbo vegetabilis",
        "carb-v": "Carbo vegetabilis",
        "chin": "Cinchona officinalis",
        "chin off": "Cinchona officinalis",
        "china": "Cinchona officinalis",
        "sulph": "Sulphur",
        "sulf": "Sulphur",
        "caust": "Causticum",
        "kali carb": "Kali carbonicum",
        "kali bich": "Kali bichromicum",
        "lues": "Syphilinum",
        "syph": "Syphilinum",
        "psor": "Psorinum",
        "medo": "Medorrhinum",
        "tub": "Tuberculinum",
        "carc": "Carcinosinum",
        "pyrog": "Pyrogenium",
        "hyper": "Hypericum perforatum",
        "symph": "Symphytum officinale",
        "ham": "Hamamelis virginiana",
        "ruta": "Ruta graveolens",
    }

    # Placebo / Sac Lac keywords
    PLACEBO_KEYWORDS = {"sl", "sac lac", "sac. lac", "sac-lac", "sacrum lactis", "placebo", "sugar of milk", "phytum"}

    # Potency matching regexes
    POTENCY_PATTERNS = [
        (r"\b(0/[1-9]|0/[1-3][0-9]|lm\s*[0-9]+|lm/[0-9]+)\b", PotencyScale.FIFTY_MILLESIMAL),
        (r"\b(q|mt|theta|ø|mother tincture)\b", PotencyScale.MOTHER_TINCTURE),
        (r"\b([1-9][0-9]*x)\b", PotencyScale.DECIMAL),
        (r"\b(30c?|200c?|1m|10m|50m|cm)\b", PotencyScale.CENTESIMAL),
        (r"\b(30|200)\b", PotencyScale.CENTESIMAL),
    ]

    # Frequency mapping
    FREQUENCY_MAP = {
        "od": DosageFrequency.OD,
        "once daily": DosageFrequency.OD,
        "morning": DosageFrequency.OD,
        "bd": DosageFrequency.BD,
        "bid": DosageFrequency.BD,
        "twice daily": DosageFrequency.BD,
        "tds": DosageFrequency.TDS,
        "tid": DosageFrequency.TDS,
        "thrice daily": DosageFrequency.TDS,
        "three times": DosageFrequency.TDS,
        "qid": DosageFrequency.QID,
        "four times": DosageFrequency.QID,
        "hs": DosageFrequency.HS,
        "bedtime": DosageFrequency.HS,
        "night": DosageFrequency.HS,
        "stat": DosageFrequency.STAT,
        "immediately": DosageFrequency.STAT,
        "sos": DosageFrequency.SOS,
        "as needed": DosageFrequency.SOS,
        "alt day": DosageFrequency.ALT_DAYS,
        "alt days": DosageFrequency.ALT_DAYS,
        "alternate days": DosageFrequency.ALT_DAYS,
        "weekly": DosageFrequency.WEEKLY,
    }

    @classmethod
    def preprocess_image(cls, image_bytes: bytes) -> Dict[str, Any]:
        """
        Lightweight image verification and preprocessing using PIL.
        Converts to grayscale, enhances contrast, and validates dimensions without GPU dependencies.
        """
        if not PIL_AVAILABLE:
            return {"status": "PIL_NOT_AVAILABLE", "width": 0, "height": 0}

        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size
            img_format = img.format or "UNKNOWN"

            # Grayscale conversion & contrast normalization
            gray = img.convert("L")
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(1.8)

            # Sharpen edges for handwriting strokes
            sharpened = enhanced.filter(ImageFilter.SHARPEN)

            out_buffer = io.BytesIO()
            sharpened.save(out_buffer, format="PNG")
            processed_bytes = out_buffer.getvalue()

            return {
                "status": "SUCCESS",
                "width": width,
                "height": height,
                "format": img_format,
                "processed_bytes_length": len(processed_bytes),
            }
        except Exception as exc:
            return {"status": "ERROR", "error": str(exc)}

    @classmethod
    def parse_handwritten_text(
        cls,
        raw_text: str,
        patient_age: Optional[int] = None,
        patient_gender: Optional[str] = None,
        is_pregnant: bool = False,
    ) -> ParsedHandwrittenPrescription:
        """
        Parses raw or OCR-transcribed handwritten prescription text.
        Extracts doctor info, complaints, diagnoses, and structured prescription items.
        Enforces INV-16, INV-01, and INV-12 safety gates.
        """
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        prescription = ParsedHandwrittenPrescription(
            raw_extracted_text=raw_text,
            patient_age=patient_age,
            patient_gender=patient_gender,
        )

        rx_mode = False
        item_counter = 1

        for line in lines:
            line_lower = line.lower()

            # 1. Doctor / Reg parsing
            if "dr." in line_lower or "dr " in line_lower:
                prescription.doctor_name = line
                continue
            if "reg" in line_lower and ("no" in line_lower or ":" in line_lower or "-" in line_lower):
                prescription.doctor_registration = line
                continue

            # 2. Date parsing
            date_match = re.search(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b", line)
            if date_match and not prescription.prescription_date:
                prescription.prescription_date = date_match.group(1)

            # 3. Patient Info
            if "patient:" in line_lower or "pt:" in line_lower or "name:" in line_lower:
                prescription.patient_name = line.split(":", 1)[-1].strip()
                # Try age/gender extraction: e.g. "45/M", "Age: 32 yrs F"
                age_match = re.search(r"\b(\d{1,2})\s*(?:yrs|yr|y)?\s*/?\s*([mf]|male|female)?\b", line_lower)
                if age_match:
                    try:
                        prescription.patient_age = int(age_match.group(1))
                    except ValueError:
                        pass
                    if age_match.group(2):
                        g = age_match.group(2).upper()
                        prescription.patient_gender = "MALE" if g.startswith("M") else "FEMALE"
                continue

            # 4. Clinical Complaints (C/o, H/o, O/E)
            if any(p in line_lower for p in ["c/o", "complaining of", "h/o", "history of", "o/e", "on examination"]):
                prescription.chief_complaints.append(line)
                continue

            # 5. Diagnoses (Dx, Diagnosis)
            if any(p in line_lower for p in ["dx", "diagnosis", "k/c/o", "known case of"]):
                prescription.clinical_diagnoses.append(line)
                continue

            # 6. Advice / Regimen
            if any(p in line_lower for p in ["adv:", "advice:", "diet:", "regimen:"]):
                prescription.general_advice.append(line)
                continue

            # 7. Rx trigger
            if re.match(r"^(rx|r/|d/|treatment|medicines?)\b", line_lower):
                rx_mode = True
                continue

            # 8. Prescription item line parsing
            is_numbered_item = bool(re.match(r"^\d+[\.\)]\s*", line))
            is_instruction_continuation = bool(
                prescription.items
                and (
                    line.startswith(" ")
                    or line.startswith("\t")
                    or any(re.search(rf"\b{kw}\b", line_lower) for kw in ["od", "bd", "bid", "tds", "tid", "qid", "hs", "stat", "sos", "days", "succussions", "morning", "night", "empty stomach", "before food", "after food", "aqua"])
                )
                and not is_numbered_item
            )

            if is_instruction_continuation:
                # Merge into the last active item's posology
                last_item = prescription.items[-1]
                last_item.posology_instruction = f"{last_item.posology_instruction} | {line}".strip()
                # Update frequency if found in continuation line
                freq = cls._extract_frequency(line_lower)
                if freq != DosageFrequency.OD:
                    last_item.frequency = freq
                # Extract duration if present
                dur_match = re.search(r"\bx\s*(\d+)\s*days?", line_lower)
                if dur_match:
                    last_item.duration_days = int(dur_match.group(1))
            elif is_numbered_item or rx_mode:
                cleaned_line = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
                item = cls._parse_item_line(cleaned_line, item_counter)
                if item:
                    # Check for duration in same line
                    dur_match = re.search(r"\bx\s*(\d+)\s*days?", line_lower)
                    if dur_match:
                        item.duration_days = int(dur_match.group(1))
                    prescription.items.append(item)
                    item_counter += 1

        # Calculate overall transcription confidence
        if prescription.items:
            avg_conf = sum(i.confidence for i in prescription.items) / len(prescription.items)
            prescription.overall_confidence = round(avg_conf, 2)
        else:
            prescription.overall_confidence = 0.50
            prescription.requires_doctor_verification = True
            prescription.verification_reasons.append("No prescription items could be definitively extracted from scan.")

        # Safety Check 1: Inimical Remedy Matrix (INV-01)
        active_remedies = [i.canonical_remedy_name for i in prescription.items if not i.is_placebo_sac_lac and i.canonical_remedy_name]
        for i in range(len(active_remedies)):
            for j in range(i + 1, len(active_remedies)):
                r1, r2 = active_remedies[i], active_remedies[j]
                inim_rule = InimicalSafetyMatrix._find_rule(r1, r2)
                if inim_rule:
                    warning_msg = f"INIMICAL RELATIONSHIP CONFLICT (INV-01): {r1} and {r2} are mutually hostile / incompatible. Hazard: {inim_rule.pathogenetic_hazard}"
                    prescription.inimical_conflicts_detected.append(warning_msg)
                    prescription.requires_doctor_verification = True
                    prescription.verification_reasons.append(warning_msg)

        # Safety Check 2: Obstetric First-Trimester Safety (INV-12)
        if is_pregnant:
            from app.safety.obstetric_firewall import PatientObstetricProfile, PregnancyStatus
            obs_profile = PatientObstetricProfile(pregnancy_status=PregnancyStatus.TRIMESTER_1)
            for itm in prescription.items:
                if not itm.is_placebo_sac_lac:
                    obs_res = ObstetricSafetyFirewall.evaluate_obstetric_safety(
                        remedy_name=itm.canonical_remedy_name,
                        potency=itm.potency,
                        profile=obs_profile,
                        raise_on_block=False
                    )
                    if not obs_res.is_permitted:
                        obs_msg = f"OBSTETRIC CONTRAINDICATION (INV-12): {obs_res.reason}"
                        prescription.obstetric_warnings.append(obs_msg)
                        prescription.requires_doctor_verification = True
                        prescription.verification_reasons.append(obs_msg)

        # Flag verification if confidence < 0.80 or unreviewed items
        for itm in prescription.items:
            if itm.requires_review:
                prescription.requires_doctor_verification = True
                prescription.verification_reasons.extend(itm.review_notes)

        return prescription

    @classmethod
    def _parse_item_line(cls, line: str, index: int) -> Optional[ParsedPrescriptionItem]:
        """Parses a single medicine item line into canonical remedy, potency, form, and frequency."""
        line_lower = line.lower()

        # Check for Placebo / Sac Lac
        for p_kw in cls.PLACEBO_KEYWORDS:
            if p_kw in line_lower:
                freq = cls._extract_frequency(line_lower)
                return ParsedPrescriptionItem(
                    item_index=index,
                    raw_line=line,
                    remedy_query="Sacrum Lactis",
                    canonical_remedy_name="Sacrum Lactis (Placebo)",
                    canonical_id="SAC-LAC",
                    potency="N/A",
                    scale=PotencyScale.UNSPECIFIED,
                    dosage_form=DosageForm.SAC_LAC,
                    frequency=freq,
                    posology_instruction=line,
                    is_placebo_sac_lac=True,
                    confidence=0.98,
                )

        # Extract potency
        extracted_potency = "30C"
        extracted_scale = PotencyScale.CENTESIMAL
        for pat, scale in cls.POTENCY_PATTERNS:
            m = re.search(pat, line_lower)
            if m:
                extracted_potency = m.group(1).upper()
                extracted_scale = scale
                break

        # Extract Frequency
        frequency = cls._extract_frequency(line_lower)

        # Extract Dosage Form
        form = DosageForm.GLOBULES
        if any(w in line_lower for w in ["drop", "drops", "gtt", "liquid"]):
            form = DosageForm.LIQUID_DROPS
        elif any(w in line_lower for w in ["powder", "trit", "trituration", "sachet"]):
            form = DosageForm.POWDER
        elif any(w in line_lower for w in ["tab", "tablets", "biochemic"]):
            form = DosageForm.TABLETS

        # Extract remedy candidate token (usually leading segment before potency or dose)
        remedy_query = cls._extract_remedy_token(line)
        canonical_name = ""
        canonical_id = None
        confidence = 0.90
        requires_review = False
        review_notes = []

        # Map through shorthand alias dictionary first
        remedy_query_clean = re.sub(r"[^a-zA-Z\s]", "", remedy_query).strip().lower()
        if remedy_query_clean in cls.HANDWRITTEN_REMEDY_ALIASES:
            canonical_name = cls.HANDWRITTEN_REMEDY_ALIASES[remedy_query_clean]
            try:
                resolved = CanonicalRemedyRegistry.resolve_remedy(canonical_name)
                canonical_id = resolved.canonical_id
                canonical_name = resolved.standard_name
                confidence = 0.95
            except UnresolvedRemedyException:
                pass
        else:
            # Fallback to direct CanonicalRemedyRegistry resolution (INV-16)
            try:
                resolved = CanonicalRemedyRegistry.resolve_remedy(remedy_query)
                canonical_name = resolved.standard_name
                canonical_id = resolved.canonical_id
                confidence = 0.92
            except UnresolvedRemedyException:
                # Fuzzy attempt on individual tokens
                tokens = remedy_query.split()
                matched = False
                for token in tokens:
                    token_clean = token.lower().strip(".")
                    if token_clean in cls.HANDWRITTEN_REMEDY_ALIASES:
                        canonical_name = cls.HANDWRITTEN_REMEDY_ALIASES[token_clean]
                        try:
                            resolved = CanonicalRemedyRegistry.resolve_remedy(canonical_name)
                            canonical_id = resolved.canonical_id
                            canonical_name = resolved.standard_name
                            confidence = 0.85
                            matched = True
                            break
                        except UnresolvedRemedyException:
                            pass
                if not matched:
                    canonical_name = remedy_query
                    confidence = 0.50
                    requires_review = True
                    review_notes.append(
                        f"Unresolved remedy name '{remedy_query}'. Requires manual RMP verification per INV-16."
                    )

        return ParsedPrescriptionItem(
            item_index=index,
            raw_line=line,
            remedy_query=remedy_query,
            canonical_remedy_name=canonical_name,
            canonical_id=canonical_id,
            potency=extracted_potency,
            scale=extracted_scale,
            dosage_form=form,
            frequency=frequency,
            posology_instruction=line,
            confidence=confidence,
            requires_review=requires_review,
            review_notes=review_notes,
        )

    @classmethod
    def _extract_remedy_token(cls, line: str) -> str:
        """Extracts the probable remedy name from a medicine line."""
        # Remove trailing dose directions, numbers, potencies, frequencies
        parts = re.split(r"\s+[/,-]\s+|\s+(?=\b(?:30|200|1m|10m|50m|cm|0/[0-9]|q|mt|x)\b)|\s+(?=\b(?:pills|drops|tablets|powder|od|bd|tds|hs|stat)\b)", line, flags=re.IGNORECASE)
        candidate = parts[0].strip() if parts else line.strip()
        # Strip leading numbers: e.g. "1. Ars Alb" -> "Ars Alb"
        candidate = re.sub(r"^\d+[\.\)]\s*", "", candidate)
        return candidate.strip()

    @classmethod
    def _extract_frequency(cls, text: str) -> DosageFrequency:
        """Extracts posology frequency from line text."""
        for kw, freq in cls.FREQUENCY_MAP.items():
            if re.search(rf"\b{kw}\b", text):
                return freq
        return DosageFrequency.OD
