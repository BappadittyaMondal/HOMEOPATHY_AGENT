"""
Test Suite for Handwritten Homeopathic Prescription OCR & Ingestion Engine (HHPIE).
"""
import io
import pytest
from PIL import Image
from app.clinical.prescription_ocr import (
    HandwrittenPrescriptionEngine,
    ParsedHandwrittenPrescription,
    PotencyScale,
    DosageFrequency,
    DosageForm,
)


def test_parse_real_world_handwritten_prescription():
    """Parses a typical Bengal homeopathic doctor handwritten prescription with abbreviations."""
    sample_prescription = """
    Dr. S. K. Banerjee, MD (Hom)
    Reg No: WBHC-12345
    Date: 21/09/2026
    Patient: R. K. Mondal, 45/M

    C/o: Dark rough spots on feet & palms x 15 yrs
         Tooth sensitivity to cold water x 5 days
    O/E: Plantar keratosis, spotted pigmentation
    Dx: Chronic Arsenicosis (Hydro-endemic)

    Rx:
    1. Ars. Alb. 200 / 4 pills
       OD morning empty stomach x 3 days
    2. Sac Lac (SL) / 4 pills
       BD x 15 days
    3. Hydrocotyle Asiatica Q / 10 drops
       in 1/2 cup aqua TDS after food

    Adv: Switch drinking water immediately to RO/treated water.
    """

    parsed = HandwrittenPrescriptionEngine.parse_handwritten_text(
        raw_text=sample_prescription,
        patient_age=45,
        patient_gender="MALE",
        is_pregnant=False,
    )

    assert "Dr. S. K. Banerjee" in parsed.doctor_name
    assert "WBHC-12345" in parsed.doctor_registration
    assert parsed.patient_age == 45
    assert parsed.patient_gender == "MALE"
    assert "21/09/2026" in parsed.prescription_date
    assert len(parsed.chief_complaints) >= 2
    assert any("Arsenicosis" in d for d in parsed.clinical_diagnoses)
    assert len(parsed.items) == 3

    # Item 1: Ars Alb 200
    item1 = parsed.items[0]
    assert item1.canonical_remedy_name == "Arsenicum album"
    assert item1.canonical_id == "REM-ARS-009"
    assert item1.potency == "200" or item1.potency == "200C"
    assert item1.scale == PotencyScale.CENTESIMAL
    assert item1.frequency == DosageFrequency.OD
    assert item1.is_placebo_sac_lac is False

    # Item 2: Sac Lac (Placebo)
    item2 = parsed.items[1]
    assert item2.is_placebo_sac_lac is True
    assert item2.dosage_form == DosageForm.SAC_LAC
    assert item2.frequency == DosageFrequency.BD

    # Item 3: Hydrocotyle Q
    item3 = parsed.items[2]
    assert "Hydrocotyle" in item3.canonical_remedy_name
    assert item3.scale == PotencyScale.MOTHER_TINCTURE
    assert item3.frequency == DosageFrequency.TDS
    assert item3.dosage_form == DosageForm.LIQUID_DROPS

    # High confidence & no doctor verification blockers
    assert parsed.overall_confidence >= 0.85
    assert parsed.requires_doctor_verification is False


def test_lm_50_millesimal_potency_parsing():
    """Parses LM (0/1 to 0/30) potencies correctly."""
    rx_text = """
    Rx:
    1. Lycopodium 0/1 / 10 succussions in aqua
       OD morning
    2. Placebo (Sac Lac)
       BD x 14 days
    """
    parsed = HandwrittenPrescriptionEngine.parse_handwritten_text(rx_text)
    assert len(parsed.items) == 2

    lyc_item = parsed.items[0]
    assert "Lycopodium" in lyc_item.canonical_remedy_name
    assert lyc_item.potency == "0/1"
    assert lyc_item.scale == PotencyScale.FIFTY_MILLESIMAL
    assert lyc_item.frequency == DosageFrequency.OD


def test_inimical_combination_detected_inv01():
    """Prescribing hostile/inimical remedies (e.g. Causticum & Phosphorus) triggers safety block (INV-01)."""
    rx_text = """
    Rx:
    1. Causticum 200
       Morning OD
    2. Phos 200
       Night HS
    """
    parsed = HandwrittenPrescriptionEngine.parse_handwritten_text(rx_text)
    assert len(parsed.items) == 2
    assert parsed.requires_doctor_verification is True
    assert len(parsed.inimical_conflicts_detected) >= 1
    assert any("INIMICAL" in msg for msg in parsed.inimical_conflicts_detected)


def test_obstetric_contraindication_detected_inv12():
    """Prescribing abortifacient (Sabina) to pregnant patient triggers obstetric block (INV-12)."""
    rx_text = """
    Rx:
    1. Sabina 30C / 4 pills
       TDS x 3 days
    """
    parsed = HandwrittenPrescriptionEngine.parse_handwritten_text(
        raw_text=rx_text,
        patient_gender="FEMALE",
        patient_age=28,
        is_pregnant=True,
    )
    assert len(parsed.items) == 1
    assert parsed.requires_doctor_verification is True
    assert len(parsed.obstetric_warnings) >= 1
    assert any("OBSTETRIC CONTRAINDICATION" in w for w in parsed.obstetric_warnings)


def test_unresolved_garbled_remedy_requires_review_inv16():
    """Unrecognized or smudged remedy text triggers manual RMP review (INV-16)."""
    rx_text = """
    Rx:
    1. Xyz123RandomRemedy 30
       OD
    """
    parsed = HandwrittenPrescriptionEngine.parse_handwritten_text(rx_text)
    assert len(parsed.items) == 1
    item = parsed.items[0]
    assert item.requires_review is True
    assert parsed.requires_doctor_verification is True
    assert any("INV-16" in r for r in parsed.verification_reasons)


def test_image_preprocessing_pipeline():
    """Verifies PIL-based grayscale conversion, contrast enhancement, and validation."""
    # Create synthetic test image in memory
    img = Image.new("RGB", (300, 200), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    result = HandwrittenPrescriptionEngine.preprocess_image(img_bytes)
    assert result["status"] == "SUCCESS"
    assert result["width"] == 300
    assert result["height"] == 200
    assert result["processed_bytes_length"] > 0
