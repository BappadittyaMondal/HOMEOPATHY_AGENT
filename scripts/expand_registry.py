"""
Script to expand CanonicalRemedyRegistry to 150 classical HPI remedies.
"""
import sys
from pathlib import Path

# Complete dataset of 150 canonical remedies
REMEDIES_DATA = [
    # 1 - 31 (Existing)
    ("REM-ACON-001", "Aconitum napellus", "Monkshood", "Aconitum napellus Linn.", "Acon.", ["aconite", "acon", "aconitum", "aconitum napellus", "monkshood", "wolfsbane"], "VEGETABLE", True, "3X"),
    ("REM-BELL-002", "Atropa belladonna", "Deadly Nightshade", "Belladonna Linn.", "Bell.", ["belladonna", "bell", "atropa belladonna", "deadly nightshade"], "VEGETABLE", True, "2X"),
    ("REM-BRY-003", "Bryonia alba", "White Bryony", "Bryonia alba Linn.", "Bry.", ["bryonia", "bry", "bryonia alba", "white bryony"], "VEGETABLE", False, "Q"),
    ("REM-NUX-004", "Strychnos nux-vomica", "Poison Nut", "Nux vomica Linn.", "Nux-v.", ["nux vomica", "nux vom", "nux-v", "nux", "strychnos nux-vomica", "poison nut"], "VEGETABLE", True, "2X"),
    ("REM-SULPH-005", "Sulphur", "Brimstone", "Sulphur Sublimatum", "Sulph.", ["sulfur", "sulphur", "sulph", "brimstone", "sublimed sulphur"], "MINERAL", False, "Q"),
    ("REM-PHOS-006", "Phosphorus", "Elemental Phosphorus", "Phosphorus", "Phos.", ["phosphorus", "phos", "elemental phosphorus", "white phosphorus"], "MINERAL", True, "3X"),
    ("REM-RHUS-007", "Rhus toxicodendron", "Poison Ivy", "Rhus toxicodendron Linn.", "Rhus-t.", ["rhus tox", "rhus toxicodendron", "rhus-t", "poison ivy", "toxicodendron radicans"], "VEGETABLE", False, "Q"),
    ("REM-APIS-008", "Apis mellifica", "Honey Bee", "Apis mellifica", "Apis", ["apis", "apis mel", "apis mellifica", "honey bee"], "ANIMAL", False, "3X"),
    ("REM-ARS-009", "Arsenicum album", "White Arsenic", "Arsenicum album", "Ars.", ["arsenic", "arsenicum", "arsenicum album", "ars", "white arsenic", "as2o3"], "MINERAL", True, "6X"),
    ("REM-CALC-010", "Calcarea carbonica", "Middle Layer of Oyster Shell", "Calcarea carbonica ostrearum", "Calc.", ["calc carb", "calcarea carb", "calcarea carbonica", "calc", "oyster shell"], "MINERAL", False, "Q"),
    ("REM-LACH-011", "Lachesis muta", "Bushmaster Snake", "Lachesis mutus", "Lach.", ["lachesis", "lachesis muta", "lach", "bushmaster"], "ANIMAL", True, "6C"),
    ("REM-LYC-012", "Lycopodium clavatum", "Club Moss", "Lycopodium clavatum Linn.", "Lyc.", ["lycopodium", "lycopodium clavatum", "lyc", "club moss"], "VEGETABLE", False, "Q"),
    ("REM-NATM-013", "Natrum muriaticum", "Common Salt", "Natrum muriaticum", "Nat-m.", ["natrum mur", "natrum muriaticum", "nat-m", "common salt", "sodium chloride"], "MINERAL", False, "Q"),
    ("REM-PULS-014", "Pulsatilla pratensis", "Wind Flower", "Pulsatilla nigricans", "Puls.", ["pulsatilla", "pulsatilla pratensis", "puls", "wind flower", "pasque flower"], "VEGETABLE", False, "Q"),
    ("REM-SIL-015", "Silicea terra", "Pure Flint", "Silicea", "Sil.", ["silicea", "silicea terra", "sil", "silica", "pure flint"], "MINERAL", False, "6X"),
    ("REM-ARN-016", "Arnica montana", "Leopard's Bane", "Arnica montana Linn.", "Arn.", ["arnica", "arnica montana", "arn", "leopards bane"], "VEGETABLE", False, "Q"),
    ("REM-SEP-017", "Sepia officinalis", "Cuttlefish Ink", "Sepia succus", "Sep.", ["sepia", "sepia officinalis", "sep", "cuttlefish ink"], "ANIMAL", False, "3X"),
    ("REM-THUJ-018", "Thuja occidentalis", "Arbor Vitae", "Thuja occidentalis Linn.", "Thuj.", ["thuja", "thuja occidentalis", "thuj", "arbor vitae", "tree of life"], "VEGETABLE", False, "Q"),
    ("REM-IGN-019", "Ignatia amara", "St. Ignatius Bean", "Strychnos ignatii Berg.", "Ign.", ["ignatia", "ignatia amara", "ign", "st ignatius bean"], "VEGETABLE", True, "2X"),
    ("REM-CAUST-020", "Causticum", "Hahnemann's Tinctura Acris Sine Kali", "Causticum Hahnemanni", "Caust.", ["causticum", "caust", "causticum hahnemanni"], "MINERAL", False, "3X"),
    ("REM-CARB-021", "Carbo vegetabilis", "Vegetable Charcoal", "Carbo vegetabilis", "Carb-v.", ["carbo veg", "carbo vegetabilis", "carb-v", "vegetable charcoal"], "VEGETABLE", False, "Q"),
    ("REM-HEP-022", "Hepar sulphuris calcareum", "Hahnemann's Calcium Sulphide", "Hepar sulphuris calcareum", "Hep.", ["hepar sulph", "hepar sulphur", "hepar sulphuris", "hep", "calcium sulphide"], "MINERAL", False, "2X"),
    ("REM-GELS-023", "Gelsemium sempervirens", "Yellow Jasmine", "Gelsemium sempervirens Ait.", "Gels.", ["gelsemium", "gelsemium sempervirens", "gels", "yellow jasmine"], "VEGETABLE", True, "3X"),
    ("REM-CHIN-024", "China officinalis", "Peruvian Bark", "Cinchona officinalis Linn.", "Chin.", ["china", "china officinalis", "cinchona", "chin", "peruvian bark"], "VEGETABLE", False, "Q"),
    ("REM-COFF-025", "Coffea cruda", "Unroasted Coffee", "Coffea arabica Linn.", "Coff.", ["coffea", "coffea cruda", "coff", "unroasted coffee"], "VEGETABLE", False, "Q"),
    ("REM-CANTH-026", "Cantharis vesicatoria", "Spanish Fly", "Cantharis vesicatoria", "Canth.", ["cantharis", "cantharis vesicatoria", "canth", "spanish fly"], "ANIMAL", True, "3X"),
    ("REM-IPEC-027", "Ipecacuanha", "Ipecac Root", "Cephaelis ipecacuanha", "Ip.", ["ipecac", "ipecacuanha", "ip", "ipecac root"], "VEGETABLE", True, "2X"),
    ("REM-MERC-028", "Mercurius solubilis", "Hahnemann's Soluble Mercury", "Mercurius solubilis Hahnemanni", "Merc.", ["mercurius", "mercurius solubilis", "merc sol", "merc", "quicksilver"], "MINERAL", True, "3X"),
    ("REM-STAPH-029", "Staphysagria", "Stavesacre", "Delphinium staphisagria Linn.", "Staph.", ["staphysagria", "staph", "stavesacre"], "VEGETABLE", True, "3X"),
    ("REM-DRO-030", "Drosera rotundifolia", "Round-leaved Sundew", "Drosera rotundifolia Linn.", "Dros.", ["drosera", "drosera rotundifolia", "dros", "sundew"], "VEGETABLE", False, "Q"),
    ("REM-AUR-031", "Aurum metallicum", "Metallic Gold", "Aurum metallicum", "Aur.", ["aurum", "aurum metallicum", "aur", "metallic gold", "gold"], "MINERAL", False, "3X"),

    # 32 - 40: Cutaneous, Keratosis & Deep Tissue Polychrests
    ("REM-ANTC-032", "Antimonium crudum", "Black Sulphide of Antimony", "Antimonium crudum", "Ant-c.", ["antimonium crudum", "ant crud", "ant-c", "black antimony", "stibium"], "MINERAL", True, "3X"),
    ("REM-HYDR-033", "Hydrocotyle asiatica", "Indian Pennywort", "Centella asiatica Linn.", "Hydr-a.", ["hydrocotyle", "hydrocotyle asiatica", "centella asiatica", "gotu kola", "hydr-a"], "VEGETABLE", False, "Q"),
    ("REM-RADBR-034", "Radium bromatum", "Radium Bromide", "Radium bromatum", "Rad-br.", ["radium bromatum", "radium brom", "rad-br", "radium bromide"], "MINERAL", True, "6C"),
    ("REM-ARSI-035", "Arsenicum iodatum", "Iodide of Arsenic", "Arsenicum iodatum", "Ars-i.", ["arsenicum iodatum", "arsenic iod", "ars-i", "arsenic iodide"], "MINERAL", True, "3X"),
    ("REM-GRAPH-036", "Graphites", "Black Lead / Plumbago", "Graphites", "Graph.", ["graphites", "graph", "black lead", "plumbago"], "MINERAL", False, "3X"),
    ("REM-PETR-037", "Petroleum", "Crude Rock Oil", "Petroleum", "Petr.", ["petroleum", "petr", "rock oil", "crude petroleum", "coal oil"], "MINERAL", False, "3X"),
    ("REM-MEZER-038", "Mezereum", "Spurge Olive", "Daphne mezereum Linn.", "Mez.", ["mezereum", "daphne mezereum", "mez", "spurge olive"], "VEGETABLE", True, "3X"),
    ("REM-SARS-039", "Sarsaparilla", "Wild Licorice", "Smilax medica", "Sars.", ["sarsaparilla", "sars", "smilax", "wild licorice"], "VEGETABLE", False, "Q"),
    ("REM-ALUM-040", "Alumina", "Pure Clay / Aluminium Oxide", "Alumina", "Alum.", ["alumina", "alum", "argilla", "aluminium oxide"], "MINERAL", False, "6X"),

    # 41 - 50: Gastrointestinal, Hepatobiliary & Abdominal
    ("REM-CHEL-041", "Chelidonium majus", "Greater Celandine", "Chelidonium majus Linn.", "Chel.", ["chelidonium", "chelidonium majus", "chel", "celandine"], "VEGETABLE", True, "Q"),
    ("REM-POD-042", "Podophyllum peltatum", "Mayapple", "Podophyllum peltatum Linn.", "Pod.", ["podophyllum", "podophyllum peltatum", "pod", "mayapple", "mandrake"], "VEGETABLE", True, "Q"),
    ("REM-ALOE-043", "Aloe socotrina", "Socotrine Aloes", "Aloe socotrina", "Aloe", ["aloe", "aloe socotrina", "aloes"], "VEGETABLE", False, "Q"),
    ("REM-COLOC-044", "Colocynthis", "Bitter Apple", "Citrullus colocynthis", "Coloc.", ["colocynthis", "colocynth", "coloc", "bitter apple"], "VEGETABLE", True, "3X"),
    ("REM-CARB-AC-045", "Carbolicum acidum", "Phenol", "Acidum carbolicum", "Carb-ac.", ["carbolic acid", "carbolicum acidum", "carb-ac", "phenol"], "MINERAL", True, "3X"),
    ("REM-HYDRAS-046", "Hydrastis canadensis", "Golden Seal", "Hydrastis canadensis Linn.", "Hydr.", ["hydrastis", "hydrastis canadensis", "golden seal", "orange root"], "VEGETABLE", False, "Q"),
    ("REM-MAGC-047", "Magnesia carbonica", "Carbonate of Magnesia", "Magnesia carbonica", "Mag-c.", ["magnesia carb", "magnesia carbonica", "mag-c"], "MINERAL", False, "Q"),
    ("REM-MAGP-048", "Magnesia phosphorica", "Phosphate of Magnesia", "Magnesia phosphorica", "Mag-p.", ["magnesia phos", "magnesia phosphorica", "mag-p"], "MINERAL", False, "Q"),
    ("REM-NAT-S-049", "Natrum sulphuricum", "Sulphate of Sodium / Glauber's Salt", "Natrum sulphuricum", "Nat-s.", ["natrum sulph", "natrum sulphuricum", "nat-s", "glaubers salt"], "MINERAL", False, "Q"),
    ("REM-NAT-C-050", "Natrum carbonicum", "Carbonate of Sodium", "Natrum carbonicum", "Nat-c.", ["natrum carb", "natrum carbonicum", "nat-c", "washing soda"], "MINERAL", False, "Q"),

    # 51 - 58: Cardiovascular & Vascular Tonics
    ("REM-CRAT-051", "Crataegus oxyacantha", "Hawthorn", "Crataegus oxyacantha Linn.", "Crat.", ["crataegus", "crataegus oxyacantha", "crat", "hawthorn"], "VEGETABLE", False, "Q"),
    ("REM-CACT-052", "Cactus grandiflorus", "Night-blooming Cereus", "Cactus grandiflorus Linn.", "Cact.", ["cactus", "cactus grandiflorus", "cact", "night blooming cereus"], "VEGETABLE", False, "Q"),
    ("REM-DIG-053", "Digitalis purpurea", "Foxglove", "Digitalis purpurea Linn.", "Dig.", ["digitalis", "digitalis purpurea", "dig", "foxglove"], "VEGETABLE", True, "3X"),
    ("REM-SPIG-054", "Spigelia anthelmia", "Pinkroot", "Spigelia anthelmia Linn.", "Spig.", ["spigelia", "spigelia anthelmia", "spig", "pinkroot", "wormgrass"], "VEGETABLE", True, "3X"),
    ("REM-GLON-055", "Glonoine", "Nitroglycerine", "Glonoinum", "Glon.", ["glonoine", "glonoinum", "glon", "nitroglycerine"], "MINERAL", True, "3X"),
    ("REM-HAM-056", "Hamamelis virginiana", "Witch Hazel", "Hamamelis virginiana Linn.", "Ham.", ["hamamelis", "hamamelis virginiana", "ham", "witch hazel"], "VEGETABLE", False, "Q"),
    ("REM-VIP-057", "Vipera berus", "German Viper", "Vipera torva", "Vip.", ["vipera", "vipera berus", "vip", "viper venom"], "ANIMAL", True, "6C"),
    ("REM-CON-058", "Conium maculatum", "Poison Hemlock", "Conium maculatum Linn.", "Con.", ["conium", "conium maculatum", "con", "poison hemlock"], "VEGETABLE", True, "3X"),

    # 59 - 65: Respiratory, Chronobiology & ENT
    ("REM-KALI-BI-059", "Kali bichromicum", "Bichromate of Potash", "Kali bichromicum", "Kali-bi.", ["kali bich", "kali bichromicum", "kali-bi", "potassium bichromate"], "MINERAL", True, "3X"),
    ("REM-KALI-C-060", "Kali carbonicum", "Carbonate of Potassium", "Kali carbonicum", "Kali-c.", ["kali carb", "kali carbonicum", "kali-c", "pearl ash"], "MINERAL", False, "Q"),
    ("REM-ANTT-061", "Antimonium tartaricum", "Tartar Emetic", "Antimonium tartaricum", "Ant-t.", ["antimonium tart", "ant tart", "ant-t", "tartar emetic"], "MINERAL", True, "3X"),
    ("REM-SPONG-062", "Spongia tosta", "Roasted Sponge", "Spongia tosta", "Spong.", ["spongia", "spongia tosta", "spong", "roasted sponge"], "ANIMAL", False, "Q"),
    ("REM-SAMB-063", "Sambucus nigra", "Elder", "Sambucus nigra Linn.", "Samb.", ["sambucus", "sambucus nigra", "samb", "elderberry"], "VEGETABLE", False, "Q"),
    ("REM-RUMEX-064", "Rumex crispus", "Yellow Dock", "Rumex crispus Linn.", "Rumx.", ["rumex", "rumex crispus", "rumx", "yellow dock"], "VEGETABLE", False, "Q"),
    ("REM-SANG-065", "Sanguinaria canadensis", "Bloodroot", "Sanguinaria canadensis Linn.", "Sang.", ["sanguinaria", "sanguinaria canadensis", "sang", "bloodroot"], "VEGETABLE", True, "Q"),

    # 66 - 73: Trauma, Musculoskeletal & Periosteal Connective Tissue
    ("REM-HYPER-066", "Hypericum perforatum", "St. John's Wort", "Hypericum perforatum Linn.", "Hyper.", ["hypericum", "hypericum perforatum", "hyper", "st johns wort"], "VEGETABLE", False, "Q"),
    ("REM-SYMPH-067", "Symphytum officinale", "Knitbone", "Symphytum officinale Linn.", "Symph.", ["symphytum", "symphytum officinale", "symph", "knitbone", "comfrey"], "VEGETABLE", False, "Q"),
    ("REM-RUTA-068", "Ruta graveolens", "Bitter Wort / Rue", "Ruta graveolens Linn.", "Ruta", ["ruta", "ruta graveolens", "rue", "bitter herb"], "VEGETABLE", False, "Q"),
    ("REM-LED-069", "Ledum palustre", "Marsh Tea", "Ledum palustre Linn.", "Led.", ["ledum", "ledum palustre", "led", "marsh tea", "wild rosemary"], "VEGETABLE", False, "Q"),
    ("REM-CALC-F-070", "Calcarea fluorica", "Fluoride of Lime", "Calcarea fluorica", "Calc-f.", ["calcarea fluor", "calc fluor", "calc-f", "calcium fluoride"], "MINERAL", False, "3X"),
    ("REM-CALC-P-071", "Calcarea phosphorica", "Phosphate of Lime", "Calcarea phosphorica", "Calc-p.", ["calcarea phos", "calc phos", "calc-p", "calcium phosphate"], "MINERAL", False, "Q"),
    ("REM-RHOD-072", "Rhododendron chrysanthum", "Snow Rose / Siberian Rhododendron", "Rhododendron chrysanthum", "Rhod.", ["rhododendron", "rhododendron chrysanthum", "rhod", "snow rose"], "VEGETABLE", False, "Q"),
    ("REM-KALM-073", "Kalmia latifolia", "Mountain Laurel", "Kalmia latifolia Linn.", "Kalm.", ["kalmia", "kalmia latifolia", "kalm", "mountain laurel", "calico bush"], "VEGETABLE", True, "Q"),

    # 74 - 82: Renal, Urological & Pelvic-Uterine
    ("REM-BERB-074", "Berberis vulgaris", "Barberry", "Berberis vulgaris Linn.", "Berb.", ["berberis", "berberis vulgaris", "berb", "barberry"], "VEGETABLE", False, "Q"),
    ("REM-PAREIR-075", "Pareira brava", "Virgin Vine", "Chondrodendron tomentosum", "Pareir.", ["pareira", "pareira brava", "pareir", "virgin vine"], "VEGETABLE", False, "Q"),
    ("REM-SABIN-076", "Sabina", "Savine", "Juniperus sabina Linn.", "Sabin.", ["sabina", "juniperus sabina", "sabin", "savine"], "VEGETABLE", True, "3X"),
    ("REM-SEC-077", "Secale cornutum", "Ergot of Rye", "Claviceps purpurea", "Sec.", ["secale", "secale cornutum", "sec", "ergot of rye", "spurred rye"], "VEGETABLE", True, "3X"),
    ("REM-CAUL-078", "Caulophyllum thalictroides", "Blue Cohosh", "Caulophyllum thalictroides Linn.", "Caul.", ["caulophyllum", "caulophyllum thalictroides", "caul", "blue cohosh", "squaw root"], "VEGETABLE", False, "Q"),
    ("REM-CIMIC-079", "Cimicifuga racemosa", "Black Cohosh / Actaea", "Actaea racemosa Linn.", "Cimic.", ["cimicifuga", "actaea racemosa", "cimic", "black cohosh", "black snake root"], "VEGETABLE", False, "Q"),
    ("REM-KREOS-080", "Kreosotum", "Beechwood Creosote", "Kreosotum", "Kreos.", ["kreosotum", "kreosote", "kreos", "creosote"], "VEGETABLE", True, "3X"),
    ("REM-BORAX-081", "Borax veneta", "Biborate of Sodium", "Borax", "Bor.", ["borax", "borax veneta", "bor", "sodium borate"], "MINERAL", False, "Q"),
    ("REM-EQUI-082", "Equisetum hyemale", "Scouring Rush / Horsetail", "Equisetum hyemale Linn.", "Equis.", ["equisetum", "equisetum hyemale", "equis", "horsetail"], "VEGETABLE", False, "Q"),

    # 83 - 92: Endocrine, Neuro-Psychiatric & Spasmodic
    ("REM-IOD-083", "Iodium", "Iodine", "Iodium", "Iod.", ["iodine", "iodium", "iod"], "MINERAL", True, "3X"),
    ("REM-THYR-084", "Thyroidinum", "Thyroid Gland Extract", "Thyroidinum", "Thyr.", ["thyroidinum", "thyroid", "thyr"], "ANIMAL", False, "3X"),
    ("REM-HYOS-085", "Hyoscyamus niger", "Henbane", "Hyoscyamus niger Linn.", "Hyos.", ["hyoscyamus", "hyoscyamus niger", "hyos", "henbane"], "VEGETABLE", True, "2X"),
    ("REM-STRAM-086", "Stramonium", "Thorn Apple", "Datura stramonium Linn.", "Stram.", ["stramonium", "datura stramonium", "stram", "thorn apple", "jimson weed"], "VEGETABLE", True, "2X"),
    ("REM-CANN-I-087", "Cannabis indica", "Indian Hemp", "Cannabis sativa Linn.", "Cann-i.", ["cannabis indica", "cann-i", "indian hemp", "hashish"], "VEGETABLE", True, "3X"),
    ("REM-ANAC-088", "Anacardium orientale", "Marking Nut", "Semecarpus anacardium Linn.", "Anac.", ["anacardium", "anacardium orientale", "anac", "marking nut"], "VEGETABLE", True, "3X"),
    ("REM-PLAT-089", "Platina", "Metallic Platinum", "Platinum metallicum", "Plat.", ["platina", "platinum", "plat", "metallic platinum"], "MINERAL", False, "3X"),
    ("REM-TARENT-090", "Tarentula hispanica", "Spanish Spider", "Lycosa tarentula", "Tarent.", ["tarentula", "tarentula hispanica", "tarent", "spanish spider"], "ANIMAL", True, "6C"),
    ("REM-CUPR-091", "Cuprum metallicum", "Metallic Copper", "Cuprum metallicum", "Cupr.", ["cuprum", "cuprum metallicum", "cupr", "copper"], "MINERAL", True, "3X"),
    ("REM-ZINC-092", "Zincum metallicum", "Metallic Zinc", "Zincum metallicum", "Zinc.", ["zincum", "zincum metallicum", "zinc", "metallic zinc"], "MINERAL", False, "3X"),

    # 93 - 102: Classical Nosodes & Deep Anti-Miasmatics
    ("REM-PSOR-093", "Psorinum", "Psoric Nosode", "Psorinum", "Psor.", ["psorinum", "psor", "psorine"], "NOSODE", False, "6C"),
    ("REM-MED-094", "Medorrhinum", "Sycotic Nosode", "Medorrhinum", "Med.", ["medorrhinum", "med", "medorrhine"], "NOSODE", False, "6C"),
    ("REM-SYPH-095", "Syphilinum", "Syphilitic Nosode", "Syphilinum / Lueticum", "Syph.", ["syphilinum", "syph", "lueticum"], "NOSODE", False, "6C"),
    ("REM-TUB-096", "Tuberculinum", "Tuberculous Nosode", "Tuberculinum bovinum", "Tub.", ["tuberculinum", "tub", "bacillinum", "tuberculin"], "NOSODE", False, "6C"),
    ("REM-CARC-097", "Carcinosinum", "Cancer Nosode", "Carcinosinum", "Carc.", ["carcinosin", "carcinosinum", "carc"], "NOSODE", False, "6C"),
    ("REM-PYROG-098", "Pyrogenium", "Artificial Sepsine", "Pyrogenium", "Pyrog.", ["pyrogenium", "pyrog", "pyrogen"], "NOSODE", False, "6C"),
    ("REM-LYSS-099", "Lyssin", "Hydrophobinum", "Lyssinum", "Lyss.", ["lyssin", "lyssinum", "hydrophobinum", "lyss"], "NOSODE", False, "6C"),
    ("REM-VARIOL-100", "Variolinum", "Smallpox Nosode", "Variolinum", "Vario.", ["variolinum", "vario"], "NOSODE", False, "6C"),
    ("REM-MALAND-101", "Malandrinum", "Grease of Horses", "Malandrinum", "Maland.", ["malandrinum", "maland"], "NOSODE", False, "6C"),
    ("REM-DIPHTH-102", "Diphtherinum", "Diphtheritic Nosode", "Diphtherinum", "Diph.", ["diphtherinum", "diph"], "NOSODE", False, "6C"),

    # 103 - 117: Acute Infection, Febrile & Septic Organ Remidies
    ("REM-BAPT-103", "Baptisia tinctoria", "Wild Indigo", "Baptisia tinctoria Linn.", "Bapt.", ["baptisia", "baptisia tinctoria", "bapt", "wild indigo"], "VEGETABLE", False, "Q"),
    ("REM-EUP-PERF-104", "Eupatorium perfoliatum", "Boneset / Thoroughwort", "Eupatorium perfoliatum Linn.", "Eup-per.", ["eupatorium", "eupatorium perfoliatum", "eup-per", "boneset"], "VEGETABLE", False, "Q"),
    ("REM-CAMPH-105", "Camphora", "Camphor", "Cinnamomum camphora", "Camph.", ["camphora", "camphor", "camph"], "VEGETABLE", True, "Q"),
    ("REM-VERAT-106", "Veratrum album", "White Hellebore", "Veratrum album Linn.", "Verat.", ["veratrum", "veratrum album", "verat", "white hellebore"], "VEGETABLE", True, "3X"),
    ("REM-CHAM-107", "Chamomilla", "German Chamomile", "Matricaria chamomilla Linn.", "Cham.", ["chamomilla", "matricaria chamomilla", "cham", "german chamomile"], "VEGETABLE", False, "Q"),
    ("REM-CINA-108", "Cina maritima", "Wormseed", "Artemisia cina Berg.", "Cina", ["cina", "cina maritima", "wormseed", "santonica"], "VEGETABLE", True, "2X"),
    ("REM-BARY-C-109", "Baryta carbonica", "Carbonate of Barium", "Baryta carbonica", "Bar-c.", ["baryta carb", "baryta carbonica", "bar-c", "barium carbonate"], "MINERAL", True, "3X"),
    ("REM-BARY-M-110", "Baryta muriatica", "Chloride of Barium", "Baryta muriatica", "Bar-m.", ["baryta mur", "baryta muriatica", "bar-m", "barium chloride"], "MINERAL", True, "3X"),
    ("REM-PLUMB-111", "Plumbum metallicum", "Metallic Lead", "Plumbum metallicum", "Plumb.", ["plumbum", "plumbum metallicum", "plumb", "lead"], "MINERAL", True, "3X"),
    ("REM-TAB-112", "Tabacum", "Tobacco", "Nicotiana tabacum Linn.", "Tab.", ["tabacum", "nicotiana tabacum", "tab", "tobacco"], "VEGETABLE", True, "3X"),
    ("REM-CHOL-113", "Cholesterinum", "Cholesterine", "Cholesterinum", "Chol.", ["cholesterinum", "cholesterin", "chol"], "ANIMAL", False, "3X"),
    ("REM-CARD-M-114", "Carduus marianus", "St. Mary's Thistle", "Silybum marianum", "Card-m.", ["carduus marianus", "card-m", "milk thistle", "st marys thistle"], "VEGETABLE", False, "Q"),
    ("REM-BERB-A-115", "Berberis aquifolium", "Mountain Grape", "Mahonia aquifolium", "Berb-a.", ["berberis aquifolium", "berb-a", "mahonia", "oregon grape"], "VEGETABLE", False, "Q"),
    ("REM-ECHIN-116", "Echinacea angustifolia", "Purple Coneflower", "Echinacea angustifolia DC.", "Echin.", ["echinacea", "echinacea angustifolia", "echin", "purple coneflower"], "VEGETABLE", False, "Q"),
    ("REM-CALEN-117", "Calendula officinalis", "Marigold", "Calendula officinalis Linn.", "Calen.", ["calendula", "calendula officinalis", "calen", "marigold"], "VEGETABLE", False, "Q"),

    # 118 - 134: Spasm, Convulsion & Hysterical Neurosis
    ("REM-STICTA-118", "Sticta pulmonaria", "Lungwort Lichen", "Lobaria pulmonaria", "Stict.", ["sticta", "sticta pulmonaria", "stict", "lungwort"], "VEGETABLE", False, "Q"),
    ("REM-AMBR-119", "Ambra grisea", "Ambergris", "Ambra grisea", "Ambr.", ["ambra grisea", "ambra", "ambr", "ambergris"], "ANIMAL", False, "3X"),
    ("REM-MOSCH-120", "Moschus", "Musk Deer Secretion", "Moschus moschiferus", "Mosch.", ["moschus", "mosch", "musk"], "ANIMAL", True, "3X"),
    ("REM-VALER-121", "Valeriana officinalis", "Valerian", "Valeriana officinalis Linn.", "Valer.", ["valeriana", "valeriana officinalis", "valer", "valerian"], "VEGETABLE", False, "Q"),
    ("REM-ASAF-122", "Asafoetida", "Devil's Dung", "Ferula foetida", "Asaf.", ["asafoetida", "asaf", "devils dung", "hing"], "VEGETABLE", False, "Q"),
    ("REM-MEPH-123", "Mephitis putorius", "Skunk Secretion", "Mephitis putorius", "Meph.", ["mephitis", "mephitis putorius", "meph", "skunk"], "ANIMAL", False, "3X"),
    ("REM-CORALL-124", "Corallium rubrum", "Red Coral", "Corallium rubrum", "Cor-r.", ["corallium rubrum", "corallium", "cor-r", "red coral"], "ANIMAL", False, "3X"),
    ("REM-COCC-125", "Cocculus indicus", "Indian Cockle", "Anamirta cocculus", "Cocc.", ["cocculus", "cocculus indicus", "cocc", "indian cockle"], "VEGETABLE", True, "3X"),
    ("REM-NUX-M-126", "Nux moschata", "Nutmeg", "Myristica fragrans", "Nux-m.", ["nux moschata", "nux-m", "nutmeg"], "VEGETABLE", False, "Q"),
    ("REM-AGAR-127", "Agaricus muscarius", "Fly Agaric", "Amanita muscaria", "Agar.", ["agaricus", "agaricus muscarius", "agar", "fly agaric", "amanita"], "VEGETABLE", True, "3X"),
    ("REM-CICUTA-128", "Cicuta virosa", "Water Hemlock", "Cicuta virosa Linn.", "Cicut.", ["cicuta", "cicuta virosa", "cicut", "water hemlock", "cowbane"], "VEGETABLE", True, "3X"),
    ("REM-OENANTH-129", "Oenanthe crocata", "Water Dropwort", "Oenanthe crocata Linn.", "Oena.", ["oenanthe", "oenanthe crocata", "oena", "water dropwort", "hemlock dropwort"], "VEGETABLE", True, "3X"),
    ("REM-PASSIF-130", "Passiflora incarnata", "Passion Flower", "Passiflora incarnata Linn.", "Pass.", ["passiflora", "passiflora incarnata", "pass", "passion flower"], "VEGETABLE", False, "Q"),
    ("REM-PISCID-131", "Piscidia erythrina", "Jamaica Dogwood", "Piscidia piscipula", "Pisc.", ["piscidia", "piscidia erythrina", "pisc", "jamaica dogwood"], "VEGETABLE", False, "Q"),
    ("REM-AVENA-132", "Avena sativa", "Common Oat", "Avena sativa Linn.", "Aven.", ["avena", "avena sativa", "aven", "oat"], "VEGETABLE", False, "Q"),
    ("REM-ALFALF-133", "Alfalfa", "Medicago / Lucerne", "Medicago sativa Linn.", "Alf.", ["alfalfa", "medicago sativa", "alf", "lucerne"], "VEGETABLE", False, "Q"),
    ("REM-GINS-134", "Ginseng", "Wild Ginseng", "Panax quinquefolium Linn.", "Gins.", ["ginseng", "panax", "gins"], "VEGETABLE", False, "Q"),

    # 135 - 145: Periodic, Mineral Exostoses & Deep Acids
    ("REM-CINCH-S-135", "Chininum sulphuricum", "Sulphate of Quinine", "Chininum sulphuricum", "Chin-s.", ["chininum sulph", "chininum sulphuricum", "chin-s", "quinine"], "MINERAL", True, "1X"),
    ("REM-CEDR-136", "Cedron", "Rattlesnake Bean", "Simaruba cedron", "Cedr.", ["cedron", "simaruba cedron", "cedr"], "VEGETABLE", False, "Q"),
    ("REM-HEKLA-137", "Hekla lava", "Lava of Mount Hekla", "Hekla lava", "Hekla", ["hekla lava", "hekla", "hecla lava"], "MINERAL", False, "3X"),
    ("REM-MERC-C-138", "Mercurius corrosivus", "Corrosive Sublimate", "Hydrargyrum bichloratum", "Merc-c.", ["mercurius corrosivus", "merc corr", "merc-c", "corrosive sublimate"], "MINERAL", True, "3X"),
    ("REM-MERC-D-139", "Mercurius dulcis", "Calomel", "Hydrargyrum chloratum mite", "Merc-d.", ["mercurius dulcis", "calomel", "merc dulc", "merc-d"], "MINERAL", True, "3X"),
    ("REM-NITR-AC-140", "Nitricum acidum", "Nitric Acid", "Acidum nitricum", "Nit-ac.", ["nitric acid", "nitricum acidum", "nit-ac"], "MINERAL", True, "3X"),
    ("REM-MURIAT-AC-141", "Muriaticum acidum", "Hydrochloric Acid", "Acidum hydrochloricum", "Mur-ac.", ["muriatic acid", "muriaticum acidum", "mur-ac", "hydrochloric acid"], "MINERAL", True, "3X"),
    ("REM-SULPH-AC-142", "Sulphuricum acidum", "Sulphuric Acid", "Acidum sulphuricum", "Sul-ac.", ["sulphuric acid", "sulphuricum acidum", "sul-ac"], "MINERAL", True, "3X"),
    ("REM-OXAL-AC-143", "Oxalicum acidum", "Oxalic Acid", "Acidum oxalicum", "Ox-ac.", ["oxalic acid", "oxalicum acidum", "ox-ac"], "MINERAL", True, "3X"),
    ("REM-PICRIC-AC-144", "Picricum acidum", "Picric Acid", "Acidum picricum", "Pic-ac.", ["picric acid", "picricum acidum", "pic-ac"], "MINERAL", True, "3X"),
    ("REM-BENZ-AC-145", "Benzoicum acidum", "Benzoic Acid", "Acidum benzoicum", "Benz-ac.", ["benzoic acid", "benzoicum acidum", "benz-ac"], "MINERAL", False, "Q"),

    # 146 - 150: Schussler Biochemic Tissue Salts & Critical Elements
    ("REM-KALI-P-146", "Kali phosphoricum", "Phosphate of Potassium", "Kali phosphoricum", "Kali-p.", ["kali phos", "kali phosphoricum", "kali-p", "potassium phosphate"], "MINERAL", False, "Q"),
    ("REM-KALI-S-147", "Kali sulphuricum", "Sulphate of Potassium", "Kali sulphuricum", "Kali-s.", ["kali sulph", "kali sulphuricum", "kali-s", "potassium sulphate"], "MINERAL", False, "Q"),
    ("REM-KALI-M-148", "Kali muriaticum", "Chloride of Potassium", "Kali muriaticum", "Kali-m.", ["kali mur", "kali muriaticum", "kali-m", "potassium chloride"], "MINERAL", False, "Q"),
    ("REM-FERR-P-149", "Ferrum phosphoricum", "Phosphate of Iron", "Ferrum phosphoricum", "Ferr-p.", ["ferrum phos", "ferrum phosphoricum", "ferr-p", "iron phosphate"], "MINERAL", False, "Q"),
    ("REM-NAT-P-150", "Natrum phosphoricum", "Phosphate of Soda", "Natrum phosphoricum", "Nat-p.", ["natrum phos", "natrum phosphoricum", "nat-p", "sodium phosphate"], "MINERAL", False, "Q")
]

def generate_canonical_registry():
    out_lines = [
        '"""',
        'Canonical Remedy Registry & Nomenclature Normalization Engine (Phase 59 & 61).',
        'Resolves variant homeopathic nomenclature, abbreviations, and botanical synonyms',
        'to deterministic Canonical Remedy Identifiers across 150 standard HPI polychrests (INV-16).',
        'Injects statutory system-level research prototype transparency banner.',
        '"""',
        'import re',
        'from typing import Dict, List, Optional',
        'from pydantic import BaseModel, Field',
        '',
        '',
        'SYSTEM_STATUS_BANNER: str = (',
        '    "CLINICAL_DECISION_SUPPORT_SYSTEM_LEVEL_2 (CDSS-L2) [RESEARCH & CLINICAL PROTOTYPE] - "',
        '    "MANDATORY HUMAN-IN-THE-LOOP: ALL SIMILLIMUM RECOMMENDATIONS REQUIRE INDEPENDENT "',
        '    "VERIFICATION AND EXPLICIT SIGN-OFF BY A REGISTERED MEDICAL PRACTITIONER (RMP) UNDER NCH ACT 2020."',
        ')',
        '',
        '',
        'class UnresolvedRemedyException(Exception):',
        '    """Raised when a remedy alias cannot be mapped to any canonical pharmacopoeial entry (INV-16)."""',
        '    def __init__(self, message: str, query: str):',
        '        super().__init__(message)',
        '        self.message = message',
        '        self.query = query',
        '',
        '',
        'class CanonicalRemedy(BaseModel):',
        '    canonical_id: str',
        '    standard_name: str',
        '    common_name: str',
        '    hpi_official_name: str',
        '    canonical_abbreviation: str',
        '    aliases: List[str] = Field(default_factory=list)',
        '    kingdom: str',
        '    is_schedule_e1: bool = False',
        '    min_safe_potency: str = "Q"',
        '',
        '',
        'class CanonicalRemedyRegistry:',
        '    """',
        '    Master registry mapping disparate clinical synonyms, abbreviations, and Latin binominals',
        '    to a single authoritative CanonicalRemedy record across 150 HPI remedies (INV-16).',
        '    """',
        '',
        '    # Top 150 Classical & Clinical Pharmacopoeial Database',
        '    _REGISTRY: Dict[str, CanonicalRemedy] = {'
    ]

    for cid, sname, cname, hname, abbr, aliases, kingdom, e1, min_p in REMEDIES_DATA:
        aliases_repr = repr(aliases)
        entry = (
            f'        "{cid}": CanonicalRemedy(\n'
            f'            canonical_id="{cid}",\n'
            f'            standard_name="{sname}",\n'
            f'            common_name="{cname}",\n'
            f'            hpi_official_name="{hname}",\n'
            f'            canonical_abbreviation="{abbr}",\n'
            f'            aliases={aliases_repr},\n'
            f'            kingdom="{kingdom}",\n'
            f'            is_schedule_e1={e1},\n'
            f'            min_safe_potency="{min_p}"\n'
            f'        ),'
        )
        out_lines.append(entry)

    out_lines[-1] = out_lines[-1].rstrip(',')  # clean last comma

    out_lines.extend([
        '    }',
        '',
        '    # Fast lookup index: normalized_string -> canonical_id',
        '    _LOOKUP_INDEX: Dict[str, str] = {}',
        '',
        '    @classmethod',
        '    def _normalize(cls, text: str) -> str:',
        '        """Strips punctuation, trailing dots, and converts to lower case."""',
        '        return re.sub(r"[^a-zA-Z0-9]", "", text).lower()',
        '',
        '    @classmethod',
        '    def _build_index(cls) -> None:',
        '        if cls._LOOKUP_INDEX:',
        '            return',
        '        for cid, rem in cls._REGISTRY.items():',
        '            cls._LOOKUP_INDEX[cls._normalize(rem.canonical_id)] = cid',
        '            cls._LOOKUP_INDEX[cls._normalize(rem.standard_name)] = cid',
        '            cls._LOOKUP_INDEX[cls._normalize(rem.common_name)] = cid',
        '            cls._LOOKUP_INDEX[cls._normalize(rem.hpi_official_name)] = cid',
        '            cls._LOOKUP_INDEX[cls._normalize(rem.canonical_abbreviation)] = cid',
        '            for alias in rem.aliases:',
        '                cls._LOOKUP_INDEX[cls._normalize(alias)] = cid',
        '',
        '    @classmethod',
        '    def resolve_remedy(cls, query: str) -> CanonicalRemedy:',
        '        """',
        '        Resolves any synonym, abbreviation, or botanical name to its CanonicalRemedy record (INV-16).',
        '        """',
        '        cls._build_index()',
        '        norm = cls._normalize(query)',
        '        cid = cls._LOOKUP_INDEX.get(norm)',
        '        if not cid:',
        '            # Fallback prefix match for clinical abbreviations with minimum length >= 5',
        '            for alias_key, mapped_cid in cls._LOOKUP_INDEX.items():',
        '                if len(alias_key) >= 5 and (norm.startswith(alias_key) or alias_key.startswith(norm)):',
        '                    cid = mapped_cid',
        '                    break',
        '',
        '        if not cid or cid not in cls._REGISTRY:',
        '            raise UnresolvedRemedyException(',
        '                f"UNRESOLVED REMEDY (INV-16): Could not map \'{query}\' to any canonical pharmacopoeial entry.",',
        '                query=query',
        '            )',
        '',
        '        return cls._REGISTRY[cid]',
        '',
        '    @classmethod',
        '    def get_system_banner(cls) -> str:',
        '        """Returns statutory legal status banner."""',
        '        return SYSTEM_STATUS_BANNER',
        '',
        '    @classmethod',
        '    def total_remedies_count(cls) -> int:',
        '        """Returns total active canonical remedies in registry."""',
        '        return len(cls._REGISTRY)',
        ''
    ])

    target_path = Path("app/repertory/canonical_registry.py")
    target_path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"Successfully generated {target_path} with {len(REMEDIES_DATA)} remedies.")

if __name__ == "__main__":
    generate_canonical_registry()
