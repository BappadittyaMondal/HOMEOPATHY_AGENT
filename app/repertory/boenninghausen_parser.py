"""
Boenninghausen Complete Symptom Parser & Grand Generalization Engine.
Deconstructs clinical text into Location, Sensation, Modality, and Concomitant (LSMC).
"""
import re
import uuid
from typing import List, Optional
from app.models.boenninghausen import (
    BoenninghausenParsedSymptom,
    BoenninghausenModality,
    PolarAxisEnum
)

class BoenninghausenParser:
    """
    Deconstructs narrative symptoms into Boenninghausen's 4-part anatomy (BTPB 1846).
    Evaluates symptom completeness and enables Grand Generalization.
    """

    POLAR_PATTERNS = [
        # Thermal Axis
        (r"(?:worse|agg|increased).*?(?:cold|chilly|winter|draft)", True, PolarAxisEnum.THERMAL, "Cold"),
        (r"(?:better|amel|relieved).*?(?:cold|ice|cold water|open air)", False, PolarAxisEnum.THERMAL, "Cold"),
        (r"(?:worse|agg|increased).*?(?:warmth|heat|summer|sun|warm room)", True, PolarAxisEnum.THERMAL, "Heat"),
        (r"(?:better|amel|relieved).*?(?:warmth|heat|hot applications|wrapping up)", False, PolarAxisEnum.THERMAL, "Heat"),

        # Motion Axis
        (r"(?:worse|agg|increased).*?(?:movement|motion|walking|exertion)", True, PolarAxisEnum.MOTION, "Motion"),
        (r"(?:better|amel|relieved).*?(?:movement|motion|walking|continued motion)", False, PolarAxisEnum.MOTION, "Motion"),
        (r"(?:worse|agg|increased).*?(?:rest|sitting|lying quiet)", True, PolarAxisEnum.MOTION, "Rest"),
        (r"(?:better|amel|relieved).*?(?:rest|quiet|lying still)", False, PolarAxisEnum.MOTION, "Rest"),

        # Pressure Axis
        (r"(?:worse|agg|increased).*?(?:touch|slight touch|contact)", True, PolarAxisEnum.PRESSURE, "Light Touch"),
        (r"(?:better|amel|relieved).*?(?:hard pressure|tight bandage|pressure)", False, PolarAxisEnum.PRESSURE, "Hard Pressure"),

        # Position Axis
        (r"(?:worse|agg).*?(?:lying on painful side|lying down)", True, PolarAxisEnum.POSITION, "Lying"),
        (r"(?:better|amel).*?(?:lying on painful side|sitting upright)", False, PolarAxisEnum.POSITION, "Position")
    ]

    CONCOMITANT_SIGNALS = [
        r"(?:accompanied by|along with|concomitant with|associated with|together with)\s+([a-zA-Z\s]+?)(?:[,.]|$)",
        r"(?:during the pain.*?also has)\s+([a-zA-Z\s]+?)(?:[,.]|$)"
    ]

    @classmethod
    def parse_symptom(cls, text: str) -> BoenninghausenParsedSymptom:
        """
        Parses a clinical statement into Location, Sensation, Modality, Concomitant.
        Calculates Completeness Score (0.0 to 1.0).
        """
        text_lower = text.lower().strip()
        
        # 1. Location
        location = None
        locations_catalog = [
            "right hypochondrium", "left knee", "forehead", "epigastrium",
            "lower abdomen", "lumbar spine", "throat", "chest", "occiput",
            "stomach", "right ovary", "skin", "joints", "teeth"
        ]
        for loc in locations_catalog:
            if loc in text_lower:
                location = loc.title()
                break
        if not location:
            # Fallback simple organs
            for loc in ["head", "eye", "ear", "nose", "back", "knee", "leg", "arm"]:
                if loc in text_lower:
                    location = loc.title()
                    break

        # 2. Sensation
        sensation = None
        sensations_catalog = [
            "stitching", "burning", "throbbing", "cramping", "tearing",
            "cutting", "pressing", "drawing", "bruised", "soreness"
        ]
        for sens in sensations_catalog:
            if sens in text_lower:
                sensation = sens.capitalize()
                break

        # 3. Modalities
        modalities: List[BoenninghausenModality] = []
        for pattern, is_agg, axis, trigger in cls.POLAR_PATTERNS:
            if re.search(pattern, text_lower):
                modalities.append(BoenninghausenModality(
                    trigger=trigger,
                    is_aggravation=is_agg,
                    polar_axis=axis,
                    intensity_grade=3
                ))

        # 4. Concomitants
        concomitants: List[str] = []
        for sig in cls.CONCOMITANT_SIGNALS:
            matches = re.finditer(sig, text_lower)
            for m in matches:
                concomitants.append(m.group(1).strip().capitalize())

        # Completeness calculation: 4 dimensions (0.25 weight each)
        score = 0.0
        if location:
            score += 0.25
        if sensation:
            score += 0.25
        if len(modalities) > 0:
            score += 0.25
        if len(concomitants) > 0:
            score += 0.25

        is_fully_qualified = (score >= 0.75)
        grand_gen_eligible = (len(modalities) > 0 and sensation is not None)

        return BoenninghausenParsedSymptom(
            symptom_id=f"BTPB-{uuid.uuid4().hex[:8].upper()}",
            original_text=text,
            location=location,
            sensation=sensation,
            modalities=modalities,
            concomitants=concomitants,
            completeness_score=round(score, 2),
            is_fully_qualified=is_fully_qualified,
            grand_generalization_eligible=grand_gen_eligible
        )
