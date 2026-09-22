"""
Static Geospatial Indian District Groundwater Risk Correlator - Geo-Epi (Phase 69).

Provides zero-dependency static epidemiological correlation between Indian postal PIN codes,
districts, and endemic hydrogeological contaminants (Arsenic and Fluoride) based on
Central Ground Water Board (CGWB) of India surveys.
Enforces Samuel Hahnemann's Organon of Medicine §4 & §5 (Removing Obstacles to Cure / Causa Occasionalis).
"""
import re
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ContaminantType(str, Enum):
    ARSENIC = "ARSENIC"
    FLUORIDE = "FLUORIDE"
    HEAVY_METALS_INDUSTRIAL = "HEAVY_METALS_INDUSTRIAL"
    NONE_DETECTED = "NONE_DETECTED"


class GeoRiskLevel(str, Enum):
    HYPER_ENDEMIC = "HYPER_ENDEMIC"      # > 0.05 mg/L Arsenic or > 1.5 mg/L Fluoride
    MODERATE_ENDEMIC = "MODERATE_ENDEMIC" # 0.01 - 0.05 mg/L Arsenic or 1.0 - 1.5 mg/L Fluoride
    LOW_BASELINE = "LOW_BASELINE"


class GeoRiskProfile(BaseModel):
    region_name: str
    state: str
    risk_level: GeoRiskLevel
    primary_contaminant: ContaminantType
    cgwb_reference: str
    mandatory_screenings: List[str]
    obstacle_to_cure_warning: str
    suggested_constitutional_remedies: List[str]


class PatientGeoExposureEvaluation(BaseModel):
    patient_id: str
    pin_code: Optional[str] = None
    district: Optional[str] = None
    years_exposed: float = 0.0
    profile: GeoRiskProfile
    toxicology_screening_mandated: bool = False
    clinical_advisory: str


class GeoAquiferRegistry:
    """
    In-memory static registry of high-risk hydrogeological aquifers in India.
    Zero external network calls, < 50 KB RAM footprint.
    """

    # 3-digit PIN code prefix mapping to endemic risk
    # Format: prefix -> (region_name, state, risk_level, contaminant, ref, screenings, remedies)
    PIN_PREFIX_MAP: Dict[str, GeoRiskProfile] = {
        # West Bengal - Gangetic Alluvial Arsenic Belt
        "743": GeoRiskProfile(
            region_name="North 24 Parganas / South 24 Parganas",
            state="West Bengal",
            risk_level=GeoRiskLevel.HYPER_ENDEMIC,
            primary_contaminant=ContaminantType.ARSENIC,
            cgwb_reference="CGWB West Bengal Arsenic Survey; Holocene shallow alluvial aquifers (>0.05 mg/L)",
            mandatory_screenings=["Spot/24h Urine Arsenic", "Nail/Hair Arsenic Biomarkers", "Cutaneous Biopsy Surveillance (INV-17)"],
            obstacle_to_cure_warning="Aphorism §4: Patient drinks untreated ground/municipal tube-well water in hyper-endemic arsenic zone.",
            suggested_constitutional_remedies=["Arsenicum album", "Arsenicum iodatum", "Antimonium crudum", "Hydrocotyle asiatica", "Thuja occidentalis"],
        ),
        "741": GeoRiskProfile(
            region_name="Nadia",
            state="West Bengal",
            risk_level=GeoRiskLevel.HYPER_ENDEMIC,
            primary_contaminant=ContaminantType.ARSENIC,
            cgwb_reference="CGWB Bhagirathi River Basin Arsenic Zone",
            mandatory_screenings=["Spot/24h Urine Arsenic", "Cutaneous Keratosis Audit"],
            obstacle_to_cure_warning="Aphorism §4: High risk of arsenical dermatosis and neuropathy.",
            suggested_constitutional_remedies=["Arsenicum album", "Sulphur", "Petroleum"],
        ),
        "742": GeoRiskProfile(
            region_name="Murshidabad",
            state="West Bengal",
            risk_level=GeoRiskLevel.HYPER_ENDEMIC,
            primary_contaminant=ContaminantType.ARSENIC,
            cgwb_reference="CGWB Murshidabad Floodplain Aquifer Survey",
            mandatory_screenings=["Spot/24h Urine Arsenic", "Nail Arsenic Concentration"],
            obstacle_to_cure_warning="Aphorism §4: Endemic groundwater arsenic exposure.",
            suggested_constitutional_remedies=["Arsenicum album", "Nitricum acidum"],
        ),
        "732": GeoRiskProfile(
            region_name="Malda",
            state="West Bengal",
            risk_level=GeoRiskLevel.HYPER_ENDEMIC,
            primary_contaminant=ContaminantType.ARSENIC,
            cgwb_reference="CGWB Malda District Arsenic Investigation",
            mandatory_screenings=["Spot/24h Urine Arsenic"],
            obstacle_to_cure_warning="Aphorism §4: Chronic arsenical melanosis and keratosis risk.",
            suggested_constitutional_remedies=["Arsenicum album", "Graphites"],
        ),
        # Bihar - Gangetic Alluvial Arsenic Belt
        "802": GeoRiskProfile(
            region_name="Bhojpur / Buxar",
            state="Bihar",
            risk_level=GeoRiskLevel.HYPER_ENDEMIC,
            primary_contaminant=ContaminantType.ARSENIC,
            cgwb_reference="CGWB Middle Ganga Plain Ground Water Contamination Report",
            mandatory_screenings=["Spot/24h Urine Arsenic", "Liver Function Panel"],
            obstacle_to_cure_warning="Aphorism §4: Endemic arsenic poisoning along southern Ganga bank.",
            suggested_constitutional_remedies=["Arsenicum album", "Lycopodium clavatum"],
        ),
        # Telangana / Andhra - Fluoride Belt
        "508": GeoRiskProfile(
            region_name="Nalgonda",
            state="Telangana",
            risk_level=GeoRiskLevel.HYPER_ENDEMIC,
            primary_contaminant=ContaminantType.FLUORIDE,
            cgwb_reference="CGWB Granitic Basement High Fluoride Aquifer Survey (>1.5 mg/L)",
            mandatory_screenings=["Serum Fluoride", "24h Urine Fluoride", "Skeletal Radiography"],
            obstacle_to_cure_warning="Aphorism §4: Severe endemic dental and skeletal fluorosis aquifer.",
            suggested_constitutional_remedies=["Fluoricum acidum", "Calcarea fluorica", "Silicea"],
        ),
        # Rajasthan - Fluoride Belt
        "342": GeoRiskProfile(
            region_name="Jodhpur / Nagaur",
            state="Rajasthan",
            risk_level=GeoRiskLevel.HYPER_ENDEMIC,
            primary_contaminant=ContaminantType.FLUORIDE,
            cgwb_reference="CGWB Rajasthan Arid Zone Fluoride Assessment",
            mandatory_screenings=["Serum Fluoride", "Dental Enamel Mottling Audit"],
            obstacle_to_cure_warning="Aphorism §4: High groundwater fluoride mineralization.",
            suggested_constitutional_remedies=["Calcarea fluorica", "Fluoricum acidum"],
        ),
    }

    # Baseline low-risk default profile
    DEFAULT_PROFILE = GeoRiskProfile(
        region_name="General Indian District / Non-Endemic",
        state="India",
        risk_level=GeoRiskLevel.LOW_BASELINE,
        primary_contaminant=ContaminantType.NONE_DETECTED,
        cgwb_reference="CGWB Standard Baseline Aquifer",
        mandatory_screenings=[],
        obstacle_to_cure_warning="No hydrogeological contaminant flagged. Standard homeopathic posology applies.",
        suggested_constitutional_remedies=[],
    )

    def lookup_by_pincode(self, pincode: str) -> GeoRiskProfile:
        """Looks up risk profile by 6-digit Indian PIN code using 3-digit prefix."""
        cleaned = re.sub(r"\D", "", pincode)
        if len(cleaned) >= 3:
            prefix = cleaned[:3]
            if prefix in self.PIN_PREFIX_MAP:
                return self.PIN_PREFIX_MAP[prefix]
        return self.DEFAULT_PROFILE

    def lookup_by_district(self, district_name: str) -> GeoRiskProfile:
        """Fuzzy match on canonical district name."""
        clean_name = re.sub(r"\b(district|dist|zila|dt)\b", "", district_name, flags=re.IGNORECASE).strip().lower()
        for profile in self.PIN_PREFIX_MAP.values():
            reg_lower = profile.region_name.lower()
            if clean_name and (clean_name in reg_lower or reg_lower in clean_name):
                return profile
        return self.DEFAULT_PROFILE

    def evaluate_exposure(
        self,
        patient_id: str,
        pin_code: Optional[str] = None,
        district: Optional[str] = None,
        years_exposed: float = 0.0,
    ) -> PatientGeoExposureEvaluation:
        """
        Evaluates patient groundwater exposure risk based on PIN code or district and duration.
        """
        profile = self.DEFAULT_PROFILE
        if pin_code:
            profile = self.lookup_by_pincode(pin_code)
        elif district:
            profile = self.lookup_by_district(district)

        # Mandate toxicology screening if in hyper-endemic zone and exposed for >= 3 years
        mandate_screening = (
            profile.risk_level == GeoRiskLevel.HYPER_ENDEMIC
            and years_exposed >= 3.0
        )

        if mandate_screening:
            advisory = (
                f"CRITICAL EPIDEMIOLOGICAL ALERT (Organon §4 & §5): Patient has resided {years_exposed} years in "
                f"{profile.region_name} ({profile.state}), a documented {profile.primary_contaminant.value} {profile.risk_level.value} aquifer. "
                f"Mandatory toxicology biomarker screening ({', '.join(profile.mandatory_screenings)}) required immediately under INV-14. "
                "Drinking water MUST be switched to certified safe sources immediately before curative response can be achieved."
            )
        elif profile.risk_level == GeoRiskLevel.HYPER_ENDEMIC:
            advisory = (
                f"CAUTION: Patient located in {profile.region_name}, an endemic {profile.primary_contaminant.value} zone. "
                "Verify household drinking water filtration source."
            )
        else:
            advisory = "No documented high-risk aquifer contamination in registered postal zone."

        return PatientGeoExposureEvaluation(
            patient_id=patient_id,
            pin_code=pin_code,
            district=district,
            years_exposed=years_exposed,
            profile=profile,
            toxicology_screening_mandated=mandate_screening,
            clinical_advisory=advisory,
        )
