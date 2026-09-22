"""
Automated Test Runner for Handwritten Homeopathic Prescription OCR & Ingestion Engine (HHPIE).
"""
import sys
import pytest


def run_prescription_ocr_tests() -> int:
    print("=" * 80)
    print("RUNNING HANDWRITTEN HOMEOPATHIC PRESCRIPTION OCR & INGESTION TEST SUITE")
    print("=" * 80)
    args = [
        "tests/test_prescription_ocr.py",
        "-v",
        "--tb=short"
    ]
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(run_prescription_ocr_tests())
