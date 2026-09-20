"""
Genius Epidemicus & Acute Epidemic Triage Engine (Phase 26).
Codifies Samuel Hahnemann's collective symptom synthesis per Organon Aphorisms 100-102
to identify the collective homeopathic epidemic simillimum across an outbreak cohort.
"""
from collections import Counter
from typing import Dict, List, Optional, Tuple
from app.models.clinical import EpidemicCase, GeniusEpidemicusResult

class GeniusEpidemicusEngine:
    """
    Synthesizes multiple individual epidemic case reports to extract the collective
    characteristic symptom totality and compute the true Genius Epidemicus remedy.
    """

    # Classical Epidemic Profiles Benchmark Matrix
    EPIDEMIC_PROFILES: Dict[str, Dict[str, List[str]]] = {
        "Influenza / Dengue Break-Bone": {
            "primary": "Eupatorium perfoliatum",
            "secondary": "Gelsemium sempervirens",
            "keynotes": [
                "deep aching in bones as if broken",
                "soreness of eyeballs",
                "chills in back followed by burning fever",
                "thirst for cold water before and during chill",
                "restlessness with aching muscles"
            ]
        },
        "Epidemic Catarrhal Grippe (Gelsemium Type)": {
            "primary": "Gelsemium sempervirens",
            "secondary": "Bryonia alba",
            "keynotes": [
                "dullness dizziness drowsiness",
                "heavy drooping eyelids ptosis",
                "occipital headache extending to forehead",
                "muscular soreness and trembling",
                "complete thirstlessness with fever"
            ]
        },
        "Asiatic Cholera Collapse (Hahnemannian Cholera)": {
            "primary": "Camphora",
            "secondary": "Veratrum album",
            "keynotes": [
                "sudden icy coldness of body with aversion to being covered",
                "rice water copious purging and vomiting",
                "cold sweat on forehead with prostration",
                "violent cramps in calves and abdomen",
                "asphyctic rapid collapse of vital powers"
            ]
        },
        "Scarlet Fever / Anginous Exanthem (Belladonna Type)": {
            "primary": "Belladonna",
            "secondary": "Apis mellifica",
            "keynotes": [
                "smooth fiery red erysipelatous rash",
                "violent cerebral congestion and hot head",
                "dilated pupils with photophobia",
                "strawberry tongue with swollen red fauces",
                "throbbing carotids with high inflammatory delirium"
            ]
        },
        "Gastroenteritis / Dysentery Epidemic": {
            "primary": "Arsenicum album",
            "secondary": "Mercurius corrosivus",
            "keynotes": [
                "rapid prostration out of proportion to illness",
                "burning pains relieved by warm drinks and heat",
                "intense thirst for frequent small sips of water",
                "nocturnal aggravation past midnight 1 to 2 AM",
                "cadaveric offensive diarrheic stools"
            ]
        }
    }

    @classmethod
    def synthesize_epidemic_cohort(
        cls,
        cases: List[EpidemicCase],
        prevalence_threshold: float = 0.40
    ) -> GeniusEpidemicusResult:
        """
        Synthesizes a cohort of epidemic case encounters into the collective totality.
        Identifies the primary and secondary Genius Epidemicus remedies.
        """
        if not cases:
            return GeniusEpidemicusResult(
                total_cases_analyzed=0,
                common_symptom_core=[],
                primary_remedy="Indeterminate (Zero cases submitted)",
                secondary_remedy=None,
                concordance_percentage=0.0
            )

        total_n = len(cases)
        symptom_counter = Counter()

        for c in cases:
            for s in c.symptoms:
                s_clean = s.strip().lower()
                symptom_counter[s_clean] += 1

        # Extract symptoms meeting or exceeding prevalence threshold
        common_core = [
            sym for sym, count in symptom_counter.items()
            if (count / total_n) >= prevalence_threshold
        ]

        if not common_core:
            # Fallback to the top 3 most frequent symptoms
            common_core = [sym for sym, _ in symptom_counter.most_common(3)]

        # Match against classical profiles
        best_profile_name = ""
        best_primary = "Indeterminate"
        best_secondary = None
        max_score = -1.0

        for profile_name, data in cls.EPIDEMIC_PROFILES.items():
            keynotes = data["keynotes"]
            matches = 0
            for core_sym in common_core:
                for kn in keynotes:
                    # Partial token overlap or substring match
                    kn_words = set(kn.split())
                    core_words = set(core_sym.split())
                    if len(kn_words.intersection(core_words)) >= 2 or kn in core_sym or core_sym in kn:
                        matches += 1
                        break
            
            score = matches / max(len(keynotes), 1)
            if score > max_score:
                max_score = score
                best_profile_name = profile_name
                best_primary = data["primary"]
                best_secondary = data["secondary"]

        concordance_pct = round(min(max_score * 100.0, 100.0), 2)
        if max_score <= 0.1:
            best_primary = "Indeterminate Simillimum"
            best_secondary = None
            concordance_pct = 0.0

        return GeniusEpidemicusResult(
            total_cases_analyzed=total_n,
            common_symptom_core=common_core,
            primary_remedy=best_primary,
            secondary_remedy=best_secondary,
            concordance_percentage=concordance_pct
        )
