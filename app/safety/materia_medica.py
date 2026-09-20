"""
Classical Materia Medica RAG Knowledge Engine (Phase 18).
Encodes verified pathogenetic profiles from Hahnemann, Kent, Boericke, Clarke, Allen, and Hering.
"""
from typing import Dict, List, Optional
from app.models.safety import MateriaMedicaEntry

class MateriaMedicaKnowledgeEngine:
    """
    Classical Materia Medica knowledge repository.
    Enables semantic lookup and clinical keynotes verification.
    """

    DATABASE: Dict[str, MateriaMedicaEntry] = {
        "Arsenicum album": MateriaMedicaEntry(
            remedy_name="Arsenicum album",
            guiding_symptoms=[
                "Great prostration with rapid sinking of vital forces",
                "Burning pains relieved by heat, hot applications, and warm drinks",
                "Intense thirst for small sips of water at frequent intervals",
                "Nocturnal aggravation, particularly between 1:00 AM and 2:00 AM",
                "Cadaveric, offensive, acrid, excoriating discharges"
            ],
            mind_keynotes=[
                "Extreme anguish, restlessness, driving patient from bed to bed",
                "Intense fear of death, believing recovery is impossible and medicine is useless",
                "Fastidious, perfectionistic, desires everything in neat order"
            ],
            sphere_of_action=[
                "Mucous membranes (destructive inflammation)",
                "Gastrointestinal tract (violent gastritis, enteritis)",
                "Cardiovascular system (heart failure, septic states)",
                "Skin (dry, scaly, burning eruptions)"
            ],
            key_modalities_agg=["1:00 AM to 2:00 AM", "Cold air", "Cold drinks", "Lying on affected side"],
            key_modalities_amel=["Heat in general", "Hot applications", "Warm drinks", "Head elevated"],
            authorities_cited=["Hahnemann (Materia Medica Pura)", "Kent", "Boericke", "Hering"]
        ),
        "Sulphur": MateriaMedicaEntry(
            remedy_name="Sulphur",
            guiding_symptoms=[
                "Burning sensations everywhere: vertex, palms, soles of feet at night",
                "Canine hunger or empty sinking sensation at pit of stomach at 11:00 AM",
                "Standing is the most uncomfortable posture; cannot walk or stand without stooping",
                "Aversion to washing, bathing; washing aggravates skin and general symptoms",
                "Red orifices of the body: red lips, red eyelids, red ears, red anus"
            ],
            mind_keynotes=[
                "Philosophic temperament, armchair theorist, 'ragged philosopher'",
                "Selfish, lazy, critical of others, disregard for external cleanliness",
                "Religious melancholia, anxious scrupulosity"
            ],
            sphere_of_action=[
                "Venous circulation (portal congestion, hemorrhoids)",
                "Skin (pruritic, burning eruptions worse heat of bed)",
                "Lymphatic and glandular system",
                "Serous and mucous membranes"
            ],
            key_modalities_agg=["Warmth of bed", "Washing/bathing", "Standing", "11:00 AM", "Rest"],
            key_modalities_amel=["Dry warm weather", "Motion", "Lying on right side"],
            authorities_cited=["Hahnemann (The Chronic Diseases)", "Kent", "Boericke", "Allen"]
        ),
        "Lycopodium clavatum": MateriaMedicaEntry(
            remedy_name="Lycopodium clavatum",
            guiding_symptoms=[
                "Symptoms proceed from right to left (right throat to left, right ovary to left)",
                "Characteristic aggravation period strictly from 4:00 PM to 8:00 PM",
                "Excessive flatulence and abdominal distension immediately after eating even a little",
                "Desire for warm food, hot drinks; aversion to cold drinks",
                "One foot hot, the other cold"
            ],
            mind_keynotes=[
                "Intellectually keen but physically weak and lacking confidence",
                "Anticipatory anxiety before public speaking, but performs brilliantly once started",
                "Domineering and irritable at home, subservient to superiors"
            ],
            sphere_of_action=[
                "Digestive tract and hepatobiliary system",
                "Urinary organs (red sand in urine, right renal colic)",
                "Respiratory system (pneumonia with fan-like motion of alae nasi)"
            ],
            key_modalities_agg=["4:00 PM to 8:00 PM", "Right side", "Warm room", "Cold food/drinks"],
            key_modalities_amel=["Warm drinks", "Cool open air", "Loosening tight clothing", "Passing flatus"],
            authorities_cited=["Hahnemann (The Chronic Diseases)", "Kent", "Boericke", "Boger"]
        ),
        "Pulsatilla pratensis": MateriaMedicaEntry(
            remedy_name="Pulsatilla pratensis",
            guiding_symptoms=[
                "Symptoms are constantly changing and erratic: wandering joint pains",
                "Thirstlessness with nearly all complaints, even during high inflammatory heat",
                "Discharges are thick, bland, yellowish-green (never excoriating)",
                "Intense intolerance of warm closed rooms; craving for cool, fresh open air",
                "Worse from fatty, greasy, rich foods, pork, pastries"
            ],
            mind_keynotes=[
                "Mild, gentle, yielding, timid, affectionate disposition",
                "Weeps easily while relating symptoms; easily consoled (consolation ameliorates)",
                "Fear of the dark, ghosts, and being alone"
            ],
            sphere_of_action=[
                "Venous vascular system (varicose veins, venous stasis)",
                "Mucous membranes (bland catarrh)",
                "Female reproductive organs (amenorrhea, delayed menses from getting feet wet)",
                "Synovial joints"
            ],
            key_modalities_agg=["Warm room", "Heat of bed", "Rich greasy food", "Twilight", "Rest"],
            key_modalities_amel=["Open cool air", "Continued slow motion", "Cold applications", "Consolation"],
            authorities_cited=["Hahnemann (Materia Medica Pura)", "Kent", "Boericke", "Clarke"]
        ),
        "Bryonia alba": MateriaMedicaEntry(
            remedy_name="Bryonia alba",
            guiding_symptoms=[
                "Extreme aggravation from the slightest motion; relief from absolute rest",
                "Sharp stitching, tearing pains, ameliorated by hard pressure and lying on painful side",
                "Excessive dryness of all mucous membranes: dry cracked lips, dry stool",
                "Intense thirst for large quantities of cold water at long intervals",
                "Right-sided lateral affinity (right chest, right hypochondrium, right ovary)"
            ],
            mind_keynotes=[
                "Exceedingly irritable, wants to be left completely undisturbed",
                "Talks of business during delirium; desires to get out of bed and go home"
            ],
            sphere_of_action=[
                "Serous membranes (pleurisy, synovitis, peritonitis with effusion)",
                "Fibrous tissue and joints",
                "Liver and gastrointestinal tract",
                "Lungs and bronchi"
            ],
            key_modalities_agg=["The least motion", "Warmth", "Rising up", "Morning", "Eating"],
            key_modalities_amel=["Absolute quiet rest", "Lying on painful side", "Hard pressure", "Cold food"],
            authorities_cited=["Hahnemann (Materia Medica Pura)", "Kent", "Boericke", "Hering"]
        )
    }

    @classmethod
    def get_entry(cls, remedy_name: str) -> Optional[MateriaMedicaEntry]:
        """Retrieves verified Materia Medica entry."""
        return cls.DATABASE.get(remedy_name)

    @classmethod
    def search_keynotes(cls, query: str) -> List[Dict]:
        """Searches Materia Medica keynotes and returns matching remedies."""
        q_lower = query.lower()
        matches = []
        for rem_name, entry in cls.DATABASE.items():
            matched_lines = []
            for s in entry.guiding_symptoms + entry.mind_keynotes:
                if q_lower in s.lower():
                    matched_lines.append(s)
            if matched_lines:
                matches.append({
                    "remedy_name": rem_name,
                    "matched_keynotes": matched_lines,
                    "authorities": entry.authorities_cited
                })
        return matches
