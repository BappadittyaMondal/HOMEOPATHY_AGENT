"""
Boenninghausen's Therapeutic Pocket Book (BTPB 1846) & Concordance Engine (Phase 08).
Models the 7 BTPB sections and computes Concordance scores for remedy relationships.
"""
from typing import List, Dict, Optional
from app.models.btpb import BTPBSectionEnum, ConcordanceRelationship

class BTPBConcordanceEngine:
    """
    Evaluates remedy relationships based on Boenninghausen's 7th section: Concordances.
    Guides the selection of complementary and chronic following remedies without inimical clashes.
    """

    # Section 7: Concordances Table (Empirical values based on BTPB 1846)
    CONCORDANCE_DB: Dict[str, List[Dict]] = {
        "Aconitum napellus": [
            {"related": "Sulphur", "mind": 18, "loc": 19, "sens": 19, "mod": 18, "type": "CHRONIC_COMPLEMENT"},
            {"related": "Coffea cruda", "mind": 16, "loc": 14, "sens": 15, "mod": 15, "type": "CONCORDANT"},
            {"related": "Belladonna", "mind": 17, "loc": 18, "sens": 17, "mod": 16, "type": "ACUTE_ANALOGUE"},
            {"related": "Arnica montana", "mind": 14, "loc": 16, "sens": 17, "mod": 15, "type": "CONCORDANT"}
        ],
        "Belladonna": [
            {"related": "Calcarea carbonica", "mind": 19, "loc": 20, "sens": 19, "mod": 18, "type": "CHRONIC_COMPLEMENT"},
            {"related": "Hyoscyamus niger", "mind": 18, "loc": 16, "sens": 17, "mod": 15, "type": "CONCORDANT"},
            {"related": "Stramonium", "mind": 19, "loc": 15, "sens": 16, "mod": 14, "type": "CONCORDANT"},
            {"related": "Bryonia alba", "mind": 14, "loc": 17, "sens": 18, "mod": 17, "type": "CONCORDANT"}
        ],
        "Bryonia alba": [
            {"related": "Rhus toxicodendron", "mind": 15, "loc": 18, "sens": 19, "mod": 19, "type": "COMPLEMENTARY_POLAR"},
            {"related": "Alumina", "mind": 16, "loc": 17, "sens": 18, "mod": 16, "type": "CHRONIC_COMPLEMENT"},
            {"related": "Natrum muriaticum", "mind": 15, "loc": 18, "sens": 17, "mod": 16, "type": "CHRONIC_FOLLOWER"},
            {"related": "Sulphur", "mind": 16, "loc": 18, "sens": 18, "mod": 17, "type": "CHRONIC_COMPLEMENT"}
        ],
        "Pulsatilla pratensis": [
            {"related": "Silicea", "mind": 18, "loc": 19, "sens": 18, "mod": 19, "type": "CHRONIC_COMPLEMENT"},
            {"related": "Kali bichromicum", "mind": 15, "loc": 18, "sens": 18, "mod": 16, "type": "CONCORDANT"},
            {"related": "Sulphur", "mind": 17, "loc": 18, "sens": 19, "mod": 17, "type": "CHRONIC_FOLLOWER"},
            {"related": "Lycopodium clavatum", "mind": 16, "loc": 17, "sens": 17, "mod": 16, "type": "CHRONIC_FOLLOWER"}
        ],
        "Nux vomica": [
            {"related": "Sepia officinalis", "mind": 18, "loc": 19, "sens": 19, "mod": 18, "type": "CHRONIC_COMPLEMENT"},
            {"related": "Sulphur", "mind": 17, "loc": 19, "sens": 18, "mod": 18, "type": "COMPLEMENTARY"},
            {"related": "Kali carbonicum", "mind": 16, "loc": 18, "sens": 17, "mod": 17, "type": "CHRONIC_FOLLOWER"},
            {"related": "Phosphorus", "mind": 15, "loc": 17, "sens": 17, "mod": 16, "type": "CONCORDANT"}
        ]
    }

    @classmethod
    def get_concordances(cls, remedy_name: str) -> List[ConcordanceRelationship]:
        """Returns ordered list of concordant remedies and relationship scores."""
        records = cls.CONCORDANCE_DB.get(remedy_name, [])
        results = []
        for r in records:
            total = r["mind"] + r["loc"] + r["sens"] + r["mod"]
            results.append(ConcordanceRelationship(
                primary_remedy=remedy_name,
                related_remedy=r["related"],
                total_concordance_score=total,
                mind_concordance=r["mind"],
                localities_concordance=r["loc"],
                sensations_concordance=r["sens"],
                modalities_concordance=r["mod"],
                relationship_type=r["type"]
            ))
        results.sort(key=lambda x: x.total_concordance_score, reverse=True)
        return results

    @classmethod
    def get_chronic_complement(cls, acute_remedy: str) -> Optional[str]:
        """Identifies primary chronic constitutional complement (e.g. Belladonna -> Calcarea carb)."""
        concordances = cls.get_concordances(acute_remedy)
        for c in concordances:
            if "COMPLEMENT" in c.relationship_type:
                return c.related_remedy
        return None
