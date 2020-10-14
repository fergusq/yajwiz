

SUFFIX_TYPES = {
    ("-'a'", "n"): "N1",
    ("-Hom", "n"): "N1",
    ("-oy", "n"): "N1",
    ("-'oy", "n"): "N1",

    ("-pu'", "n"): "N2",
    ("-Du'", "n"): "N2",
    ("-mey", "n"): "N2",

    ("-qoq", "n"): "N3",
    ("-Hey", "n"): "N3",
    ("-na'", "n"): "N3",

    ("-wI'", "n"): "N4",
    ("-ma'", "n"): "N4",
    ("-lI'", "n"): "N4",
    ("-ra'", "n"): "N4",
    ("-wIj", "n"): "N4",
    ("-maj", "n"): "N4",
    ("-lIj", "n"): "N4",
    ("-raj", "n"): "N4",
    ("-Daj", "n"): "N4",
    ("-chaj", "n"): "N4",
    ("-vam", "n"): "N4",
    ("-vetlh", "n"): "N4",

    ("-Daq", "n"): "N5",
    ("-vo'", "n"): "N5",
    ("-mo'", "n"): "N5",
    ("-vaD", "n"): "N5",
    ("-'e'", "n"): "N5",

    ("-Ha'", "v"): "VR",
    ("-be'", "v"): "VR",
    ("-qu'", "v"): "VR",

    ("-'egh", "v"): "V1",
    ("-chuq", "v"): "V1",

    ("-nIS", "v"): "V2",
    ("-qang", "v"): "V2",
    ("-rup", "v"): "V2",
    ("-beH", "v"): "V2",
    ("-vIp", "v"): "V2",

    ("-choH", "v"): "V3",
    ("-qa'", "v"): "V3",

    ("-moH", "v"): "V4",

    ("-lu'", "v"): "V5",
    ("-laH", "v"): "V5",

    ("-chu'", "v"): "V6",
    ("-bej", "v"): "V6",
    ("-ba'", "v"): "V6",
    ("-law'", "v"): "V6",

    ("-pu'", "v"): "V7",
    ("-ta'", "v"): "V7",
    ("-taH", "v"): "V7",
    ("-lI'", "v"): "V7",

    ("-neS", "v"): "V8",

    ("-Qo'", "v"): "VQ",

    ("-DI'", "v"): "V9",
    ("-chugh", "v"): "V9",
    ("-pa'", "v"): "V9",
    ("-vIS", "v"): "V9",
    ("-mo'", "v"): "V9",
    ("-bogh", "v"): "V9",
    ("-meH", "v"): "V9",
    ("-'a'", "v"): "V9",
    ("-jaj", "v"): "V9",
    ("-ghach", "v"): "V9",
    ("-wI'", "v"): "V9",

    ("-maH", "n"): "L1",
    ("-vatlh", "n"): "L1",
    ("-SaD", "n"): "L1",
    ("-SanID", "n"): "L1",
    ("-netlh", "n"): "L1",
    ("-bIp", "n"): "L1",
    ("-'uy'", "n"): "L1",
    ("-Saghan", "n"): "L1",
    ("-maH'uy'", "n"): "L1",
    ("-vatlhbIp", "n"): "L1",
    ("-vatlh'uy'", "n"): "L1",
    ("-SaDbIp", "n"): "L1",
    ("-SanIDbIp", "n"): "L1",
    ("-DIch", "n"): "L2",
    ("-logh", "n"): "L2",
    ("-leS", "n"): "L2",
    ("-Hu'", "n"): "L2",
}

XPOS_TO_UPOS = {
    "VS": "ADJ",
    "VT": "VERB",
    "VI": "VERB",
    "VA": "VERB",
    "V?": "VERB",
    "NL": "NOUN",
    "NB": "NOUN",
    "PRON": "PRON",
    "NUM": "NUM",
    "N": "NOUN",
    "ADV": "ADV",
    "EXCL": "INTJ",
    "CONJ": "CCONJ",
    "QUES": "ADV",
    "UNK": "X",
}

UNIVERSAL_FEATURES = {
    #("-'a'", "N1"): "",
    #("-Hom", "N1"): "",
    #("-oy", "N1"): "",
    #("-'oy", "N1"): "",

    ("-pu'", "N2"): "Number=Plur",
    ("-Du'", "N2"): "Number=Plur",
    ("-mey", "N2"): "Number=Plur",

    #("-qoq", "N3"): "",
    #("-Hey", "N3"): "",
    #("-na'", "N3"): "",

    ("-wI'", "N4"): "Poss=Yes|PossPerson=1|PossNumber=Sing",
    ("-ma'", "N4"): "Poss=Yes|PossPerson=1|PossNumber=Plur",
    ("-lI'", "N4"): "Poss=Yes|PossPerson=2|PossNumber=Sing",
    ("-ra'", "N4"): "Poss=Yes|PossPerson=1|PossNumber=Plur",
    ("-wIj", "N4"): "Poss=Yes|PossPerson=1|PossNumber=Sing",
    ("-maj", "N4"): "Poss=Yes|PossPerson=1|PossNumber=Plur",
    ("-lIj", "N4"): "Poss=Yes|PossPerson=2|PossNumber=Sing",
    ("-raj", "N4"): "Poss=Yes|PossPerson=2|PossNumber=Plur",
    ("-Daj", "N4"): "Poss=Yes|PossPerson=3|PossNumber=Sing",
    ("-chaj", "N4"): "Poss=Yes|PossPerson=3|PossNumber=Plur",
    ("-vam", "N4"): "",
    ("-vetlh", "N4"): "",

    ("-Daq", "N5"): "Case=Loc",
    ("-vo'", "N5"): "Case=Ela",
    ("-mo'", "N5"): "Case=Cau",
    ("-vaD", "N5"): "Case=Dat",
    ("-'e'", "N5"): "Case=Top",

    ("HI-", "P"): "Mood=Imp|Person=2|ObjPerson=1|ObjNumber=Sing",
    ("gho-", "P"): "Mood=Imp|Person=2|ObjPerson=1|ObjNumber=Plur",
    ("yI-", "P"): "Mood=Imp|Person=2|ObjPerson=3,0|ObjNumber=Sing",
    ("tI-", "P"): "Mood=Imp|Person=2|ObjPerson=3|ObjNumber=Plur",
    ("pe-", "P"): "Mood=Imp|Person=2|Number=Plur|ObjPerson=0",

    ("qa-", "P"): "Person=1|Number=Sing|ObjPerson=2|ObjNumber=Sing",
    ("Sa-", "P"): "Person=1|Number=Sing|ObjPerson=2|ObjNumber=Plur",
    ("vI-", "P"): "Person=1|Number=Sing|ObjPerson=3",
    ("jI-", "P"): "Person=1|Number=Sing|ObjPerson=0",

    ("pI-", "P"): "Person=1|Number=Plur|ObjPerson=2|ObjNumber=Sing",
    ("re-", "P"): "Person=1|Number=Plur|ObjPerson=2|ObjNumber=Plur",
    ("wI-", "P"): "Person=1|Number=Plur|ObjPerson=3|ObjNumber=Sing",
    ("DI-", "P"): "Person=1|Number=Plur|ObjPerson=3|ObjNumber=Plur",
    ("ma-", "P"): "Person=1|Number=Plur|ObjPerson=0",

    ("cho-", "P"): "Person=2|Number=Sing|ObjPerson=1|ObjNumber=Sing",
    ("ju-", "P"): "Person=2|Number=Sing|ObjPerson=1|ObjNumber=Plur",
    ("Da-", "P"): "Person=2|Number=Sing|ObjPerson=3",
    ("bI-", "P"): "Person=2|Number=Sing|ObjPerson=0",

    ("tu-", "P"): "Person=2|Number=Plur|ObjPerson=1|ObjNumber=Sing",
    ("che-", "P"): "Person=2|Number=Plur|ObjPerson=1|ObjNumber=Plur",
    ("bo-", "P"): "Person=2|Number=Plur|ObjPerson=3",
    ("Su-", "P"): "Person=2|Number=Plur|ObjPerson=0",

    ("mu-", "P"): "Person=3|ObjPerson=1|ObjNumber=Sing",
    ("nu-", "P"): "Person=3|ObjPerson=1|ObjNumber=Plur",
    ("Du-", "P"): "Person=3|Number=Sing|ObjPerson=2|ObjNumber=Sing",
    ("nI-", "P"): "Person=3|Number=Plur|ObjPerson=2|ObjNumber=Sing",
    ("lI-", "P"): "Person=3|ObjPerson=2|ObjNumber=Plur",
    ("lu-", "P"): "Person=3|Number=Plur|ObjPerson=3|ObjNumber=Sing",

    ("-", "P"): "Person=3|ObjPerson=3,0",

    ("vI-", "NP"): "Person=0|ObjPerson=1|ObjNumber=Sing",
    ("wI-", "NP"): "Person=0|ObjPerson=1|ObjNumber=Plur",
    ("Da-", "NP"): "Person=0|ObjPerson=2|ObjNumber=Sing",
    ("bo-", "NP"): "Person=0|ObjPerson=2|ObjNumber=Plur",
    ("-", "NP"): "Person=0|ObjPerson=3,0|ObjNumber=Sing",
    ("lu-", "NP"): "Person=0|ObjPerson=3|ObjNumber=Plur",
    

    #"-Ha'": "VR",
    #"-be'": "VR",
    #"-qu'": "VR",

    #"-'egh": "V1",
    #"-chuq": "V1",

    #"-nIS": "V2",
    #"-qang": "V2",
    #"-rup": "V2",
    #"-beH": "V2",
    #"-vIp": "V2",

    #"-choH": "V3",
    #"-qa'": "V3",

    #"-moH": "V4",

    #"-lu'": "V5",
    #"-laH": "V5",

    #"-chu'": "V6",
    #"-bej": "V6",
    #"-ba'": "V6",
    #"-law'": "V6",

    ("-pu'", "V7"): "Aspect=Perf",
    ("-ta'", "V7"): "Aspect=Int",
    ("-taH", "V7"): "Aspect=Imp",
    ("-lI'", "V7"): "Aspect=Prog",

    ("-neS", "V8"): "Polite=Humb",

    #"-Qo'": "VQ",

    #"-DI'": "V9",
    #"-chugh": "V9",
    #"-pa'": "V9",
    #"-vIS": "V9",
    #"-mo'": "V9",
    #"-bogh": "V9",
    #"-meH": "V9",
    #"-'a'": "V9",
    ("-jaj", "V9"): "Mood=Jus",
    ("-ghach", "V9"): "VerbForm=Vnoun",
    ("-wI'", "V9"): "VerbForm=Vnoun",

    #"-maH": "L1",
    #"-vatlh": "L1",
    #"-SaD": "L1",
    #"-SanID": "L1",
    #"-netlh": "L1",
    #"-bIp": "L1",
    #"-'uy'": "L1",
    #"-Saghan": "L1",
    #"-maH'uy'": "L1",
    #"-vatlhbIp": "L1",
    #"-vatlh'uy'": "L1",
    #"-SaDbIp": "L1",
    #"-SanIDbIp": "L1",
    ("-DIch", "L2"): "NumType=Ord",
    #"-logh": "L2",
}