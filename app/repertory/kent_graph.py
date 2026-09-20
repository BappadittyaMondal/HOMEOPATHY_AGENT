"""
Kent's Repertory Digital Graph & Cross-Referencing Engine (Phase 07).
Hierarchical rubric tree traversal, synonym resolution, and cross-reference graph queries.
"""
from typing import List, Dict, Set, Optional
from pydantic import BaseModel, Field

class KentRubricNode(BaseModel):
    rubric_id: str
    chapter: str
    full_path: str
    parent_path: Optional[str] = None
    level: int = 1
    remedy_grades: Dict[str, int] = Field(default_factory=dict)  # remedy_abbr -> grade (1..4)
    cross_references: List[str] = Field(default_factory=list)   # paths to related rubrics
    synonyms: List[str] = Field(default_factory=list)

class KentRepertoryGraph:
    """
    In-memory digital graph of Kent's Repertory.
    Enforces chapter hierarchies, parent-child navigation, and cross-referencing.
    """
    CANONICAL_CHAPTERS = [
        "MIND", "VERTIGO", "HEAD", "EYE", "VISION", "EAR", "HEARING", "NOSE",
        "FACE", "MOUTH", "TEETH", "THROAT", "EXTERNAL THROAT", "STOMACH",
        "ABDOMEN", "RECTUM", "STOOL", "BLADDER", "KIDNEYS", "PROSTATE",
        "URETHRA", "URINE", "GENITALIA MALE", "GENITALIA FEMALE",
        "LARYNX AND TRACHEA", "RESPIRATION", "COUGH", "EXPECTORATION",
        "CHEST", "BACK", "EXTREMITIES", "SLEEP", "CHILL", "FEVER",
        "PERSPIRATION", "SKIN", "GENERALITIES"
    ]

    def __init__(self):
        self.nodes: Dict[str, KentRubricNode] = {}        # full_path -> KentRubricNode
        self.children_map: Dict[str, List[str]] = {}     # full_path -> list of children full_paths
        self.chapter_index: Dict[str, List[str]] = {}    # chapter -> list of full_paths
        self._token_index: Dict[str, Set[str]] = {}      # word token -> set of full_paths
        self._bootstrap_canonical_graph()

    def _bootstrap_canonical_graph(self):
        """Initializes canonical base rubrics with grades and cross-references."""
        sample_rubrics = [
            {
                "path": "MIND - ANXIETY - health, about",
                "chapter": "MIND",
                "grades": {"Ars": 3, "Nit-ac": 3, "Calc": 2, "Phos": 2, "Kali-ar": 2},
                "cross_refs": ["MIND - FEAR - disease, of", "MIND - DESPAIR - recovery, of"],
                "synonyms": ["worries about illness", "hypochondriac anxiety"]
            },
            {
                "path": "MIND - FEAR - disease, of",
                "chapter": "MIND",
                "grades": {"Ars": 3, "Phos": 3, "Calc": 2, "Lach": 2},
                "cross_refs": ["MIND - ANXIETY - health, about"],
                "synonyms": ["fear of sickness", "nosophobia"]
            },
            {
                "path": "MIND - RESTLESSNESS",
                "chapter": "MIND",
                "grades": {"Acon": 3, "Ars": 3, "Rhus-t": 3, "Bell": 2, "Cham": 2},
                "cross_refs": ["GENERALITIES - MOTION - desires"],
                "synonyms": ["cannot sit still", "constant moving"]
            },
            {
                "path": "MIND - ANGER - ailments after",
                "chapter": "MIND",
                "grades": {"Cham": 3, "Coloc": 3, "Staph": 3, "Nux-v": 3, "Ign": 2},
                "cross_refs": ["MIND - MORTIFICATION - ailments after"],
                "synonyms": ["bad effects from wrath", "suppressed indignation"]
            },
            {
                "path": "HEAD - PAIN - forehead",
                "chapter": "HEAD",
                "grades": {"Bell": 3, "Bry": 3, "Nux-v": 3, "Gels": 2, "Iris": 2},
                "cross_refs": ["HEAD - PAIN - forehead - eyes, above"],
                "synonyms": ["frontal headache"]
            },
            {
                "path": "HEAD - PAIN - forehead - motion - agg.",
                "chapter": "HEAD",
                "grades": {"Bry": 3, "Bell": 3, "Nux-v": 2, "Spig": 2},
                "cross_refs": ["HEAD - PAIN - motion - agg."],
                "synonyms": ["frontal pain worse walking"]
            },
            {
                "path": "HEAD - PAIN - forehead - pressure - amel.",
                "chapter": "HEAD",
                "grades": {"Bry": 3, "Puls": 2, "Mag-m": 2, "Arg-n": 2},
                "cross_refs": ["HEAD - PAIN - pressure - amel."],
                "synonyms": ["headache relieved by tight bandage"]
            },
            {
                "path": "GENERALITIES - COLD - air - agg.",
                "chapter": "GENERALITIES",
                "grades": {"Hep": 3, "Ars": 3, "Nux-v": 3, "Sil": 3, "Psor": 3},
                "cross_refs": ["GENERALITIES - DRAFT - agg."],
                "synonyms": ["chilly patient", "worse in winter"]
            },
            {
                "path": "GENERALITIES - WARMTH - agg.",
                "chapter": "GENERALITIES",
                "grades": {"Puls": 3, "Sulph": 3, "Sec": 3, "Iod": 2, "Apis": 3},
                "cross_refs": ["GENERALITIES - HEAT - flushes of"],
                "synonyms": ["hot patient", "worse in warm room"]
            }
        ]

        for item in sample_rubrics:
            self.add_rubric(
                full_path=item["path"],
                chapter=item["chapter"],
                remedy_grades=item["grades"],
                cross_references=item["cross_refs"],
                synonyms=item["synonyms"]
            )

    def add_rubric(
        self, 
        full_path: str, 
        chapter: str, 
        remedy_grades: Optional[Dict[str, int]] = None,
        cross_references: Optional[List[str]] = None,
        synonyms: Optional[List[str]] = None
    ) -> KentRubricNode:
        """Adds or updates a rubric node and updates graph indices."""
        parts = [p.strip() for p in full_path.split("-")]
        level = len(parts)
        parent_path = " - ".join(parts[:-1]) if level > 1 else None

        node = KentRubricNode(
            rubric_id=f"KENT-{len(self.nodes)+1:05d}",
            chapter=chapter.upper(),
            full_path=full_path,
            parent_path=parent_path,
            level=level,
            remedy_grades=remedy_grades or {},
            cross_references=cross_references or [],
            synonyms=synonyms or []
        )
        self.nodes[full_path] = node

        # Hierarchy tracking
        if parent_path:
            self.children_map.setdefault(parent_path, []).append(full_path)
        self.chapter_index.setdefault(chapter.upper(), []).append(full_path)

        # Index tokens for keyword and synonym search (individual words)
        search_words = full_path.lower().replace("-", " ").split()
        for syn in node.synonyms:
            search_words.extend(syn.lower().replace("-", " ").split())

        for term in search_words:
            cleaned = "".join(c for c in term if c.isalnum())
            if len(cleaned) >= 3:
                self._token_index.setdefault(cleaned, set()).add(full_path)

        return node

    def get_rubric(self, full_path: str) -> Optional[KentRubricNode]:
        """Retrieves rubric node by exact path."""
        return self.nodes.get(full_path)

    def get_children(self, full_path: str) -> List[KentRubricNode]:
        """Returns direct child rubrics."""
        child_paths = self.children_map.get(full_path, [])
        return [self.nodes[p] for p in child_paths if p in self.nodes]

    def get_cross_references(self, full_path: str) -> List[KentRubricNode]:
        """Returns cross-referenced rubric nodes."""
        node = self.nodes.get(full_path)
        if not node:
            return []
        return [self.nodes[ref] for ref in node.cross_references if ref in self.nodes]

    def search_rubrics(self, query: str, limit: int = 10) -> List[KentRubricNode]:
        """Token-based search with synonym expansion."""
        tokens = [t.strip().lower() for t in query.split() if len(t.strip()) >= 3]
        if not tokens:
            return []

        matched_paths: Set[str] = set()
        for token in tokens:
            cleaned = "".join(c for c in token if c.isalnum())
            if cleaned in self._token_index:
                if not matched_paths:
                    matched_paths.update(self._token_index[cleaned])
                else:
                    matched_paths.intersection_update(self._token_index[cleaned])

        results = [self.nodes[p] for p in matched_paths if p in self.nodes]
        return results[:limit]

# Singleton graph instance
kent_graph = KentRepertoryGraph()
