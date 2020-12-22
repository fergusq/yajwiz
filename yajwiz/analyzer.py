import json
import re
from collections import defaultdict
import copy
import os

from typing import DefaultDict, Dict, List, Set, Tuple, Optional, Literal, TypedDict

from .tables import SUFFIX_TYPES, UNIVERSAL_FEATURES, XPOS_TO_UPOS, PREFIX_TABLE, Person, Number

Xpos = Literal["VS", "VT", "VI", "VA", "V?", "NL", "NB", "PRON", "NUM", "N", "ADV", "EXCL", "CONJ", "QUES", "UNK"]

class BoqwizEntry(TypedDict):
    entry_name: str
    part_of_speech: str

def _get_xpos(entry: BoqwizEntry) -> Xpos:
    pos2 = entry["part_of_speech"]
    if pos2.startswith("v:is"):
        return "VS"
    
    elif pos2.startswith("v:t"):
        return "VT"
    
    elif pos2.startswith("v:i"):
        return "VI"
    
    elif pos2.startswith("v:ambi"):
        return "VA"
    
    elif pos2.startswith("v:") or pos2 == "v":
        return "V?"
    
    elif pos2.startswith("n:") and "being" in pos2:
        return "NL"
    
    elif pos2.startswith("n:") and "body" in pos2:
        return "NB"
    
    elif pos2.startswith("n:") and ("pro" in pos2 or entry["entry_name"] in {"'Iv", "nuq", "jIH"}):
        return "PRON"
    
    elif pos2.startswith("n") and entry["entry_name"] in {"wa'", "cha'", "wej", "loS", "vagh", "jav", "Soch", "chorgh", "Hut"}:
        return "NUM"
    
    elif pos2.startswith("n:") or pos2 == "n":
        return "N"
    
    elif pos2 == "adv":
        return "ADV"
    
    elif pos2.startswith("excl"):
        return "EXCL"
    
    elif pos2.startswith("conj"):
        return "CONJ"
    
    elif pos2.startswith("ques"):
        return "QUES"
    
    else:
        return "UNK"

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(SCRIPT_DIR, "data.json"), "r") as f:
    data = json.load(f)

VERBS: List[str] = []
STATIVE_VERBS: List[str] = []
NOUNS: List[str] = []

ALL_WORDS: Set[str] = set()
WORD_INDEX: DefaultDict[str, List[BoqwizEntry]] = defaultdict(lambda: [])
XPOS_INDEX: DefaultDict[str, Set[BoqwizEntry]] = defaultdict(set)

for entry in data["qawHaq"].values():
    word = entry["entry_name"]
    pos = entry["part_of_speech"]
    if "hyp" in pos:
        continue

    good = not (" " in word or "pref" in pos or "suff" in pos or "deriv" in pos)

    if pos.startswith("v:") or pos == "v":
        if good:
            VERBS.append(word)

        WORD_INDEX[word + ":v"].append(entry)
    
        if good and pos.startswith("v:is"):
            STATIVE_VERBS.append(word)
    
    elif pos.startswith("n:") or pos == "n":
        if good:
            NOUNS.append(word)

        WORD_INDEX[word + ":n"].append(entry)
    
    else:
        WORD_INDEX[word + ":other"].append(entry)
    
    ALL_WORDS.add(word)
    XPOS_INDEX[_get_xpos(entry)].add(word)

NOUN_SUFFIX_REGEX = r"('a'|Hom|(?<=[bDHjqlmnpQrStvwy'hg])oy|(?<![bDHjqlmnpQrStvwy'hg])'oy)?(pu'|Du'|mey)?(qoq|Hey|na')?(wI'|ma'|lI'|ra'|wIj|maj|lIj|raj|Daj|chaj|vam|vetlh)?(Daq|vo'|mo'|vaD|'e')?"

NOUN_REGEX = re.compile(r"(" + r"|".join(NOUNS) + r")" + NOUN_SUFFIX_REGEX)

VERB_SUFFIX_REGEX = r"(Ha')?('egh|chuq)?(be'|qu')?(nIS|qang|rup|beH|vIp)?(be'|qu')?(choH|qa')?(be'|qu')?(moH)?(be'|qu')?(lu'|laH)?(be'|qu')?(chu'|bej|ba'|law')?(be'|qu')?(pu'|ta'|taH|lI')?(be'|qu')?(neS)?(be'|qu')?(Qo')?(?:(DI'|chugh|pa'|vIS|mo'|bogh|meH|'a'|jaj)|(?:(wI'|ghach)" + NOUN_SUFFIX_REGEX + r"))?"

VERB_REGEX = re.compile(r"(|HI|gho|yI|tI|pe|qa|Sa|vI|jI|pI|re|DI|wI|ma|cho|ju|Da|bI|tu|che|bo|Su|mu|nu|Du|lI|nI|lu)("
    + r"|".join(VERBS)
    + r")" + VERB_SUFFIX_REGEX)

PRONOUN_VERB_REGEX = re.compile(r"(jIH|maH|SoH|tlhIH|ghaH|chaH|'oH|bIH)" + VERB_SUFFIX_REGEX)

STATIVE_VERB_REGEX = re.compile(r"(" + r"|".join(STATIVE_VERBS) + r")(Ha')?(be')?(qu')?(be')?(Daq|vo'|mo'|vaD|'e')")

NUMBER_SUFFIX_REGEX = r"(maH|vatlh|SaD|SanID|netlh|bIp|'uy'|Saghan|maH'uy'|vatlhbIp|vatlh'uy'|SaDbIp|SanIDbIp)"
NUMBER_REGEX = re.compile(r"(wa'|cha'|wej|loS|vagh|jav|Soch|chorgh|Hut)(?:" + NUMBER_SUFFIX_REGEX +  r"(DIch|logh|leS|Hu')?|" + NUMBER_SUFFIX_REGEX + r"?(DIch|logh|leS|Hu'))")

def split_to_morphemes(word: str) -> Set[tuple]:
    """
    Given a word, splits it to morphemes. Prefixes and suffixes are marked with dashes.
    """
    ans = set()
    for regex in [NOUN_REGEX, STATIVE_VERB_REGEX, NUMBER_REGEX, PRONOUN_VERB_REGEX]:
        if m := regex.fullmatch(word):
            parts = []
            for i, part in enumerate(m.groups()):
                if not part:
                    continue

                if i > 0:
                    part = "-" + part

                parts.append(part)
            
            ans.add(tuple(parts))
    
    if m := VERB_REGEX.fullmatch(word):
        parts = []
        for i, part in enumerate(m.groups()):
            if not part:
                continue

            if i < 1:
                part = part + "-"

            elif i > 1:
                part = "-" + part

            parts.append(part)
        
        ans.add(tuple(parts))
    
    return ans

def _next_morphem(parsed: List[str], i: int) -> Tuple[int, Optional[str]]:
    oi = i
    i += 1
    while i < len(parsed):
        if parsed[i]:
            return i, parsed[i]

        i += 1
    
    return oi, None

LETTER = re.compile(r"(ch|gh|ng|tlh|[abDeHIjlmnopqQrStuvwy'])")

def split_to_letters(word: str) -> List[str]:
    """
    Splits the given word to Klingon letters. The word must not contain spaces or foreign letters.
    """
    letters = []
    while word:
        if m := re.match(LETTER, word):
            letter = m.group(1)
            word = word[len(letter):]
            letters += [letter]

        else:
            word = word[1:]

    return letters

def split_to_syllables(word: str) -> List[str]:
    """
    Splits the given word to syllables. The word msut not contain spaces or foreign words and it should follow the Klingon phonotactics.
    """
    letters = split_to_letters(word)
    syllables = [""]

    for prev, cur, succ in zip([""]+letters, letters, letters[1:]+[""]):
        if syllables[-1] and \
            cur not in "aeIou" and \
            (succ and succ in "aeIou" or \
                prev and prev not in "aeIou" and \
                not (prev+cur) in {"w'", "y'", "rgh"}):
            syllables.append(cur)

        else:
            syllables[-1] += cur
    
    return syllables

class SyntaxInfo(TypedDict, total=False):
    ROLE: Literal["NP", "VP", "OTHER"]
    OBJECT_PERSON: Set[Person]
    OBJECT_NUMBER: Optional[Number]
    SUBJECT_PERSON: Set[Person]
    SUBJECT_NUMBER: Optional[Number]
    PLURAL: bool

class _AnalysisRequired(TypedDict):
    WORD: str
    LEMMA: str
    POS: str
    XPOS: Xpos
    BOQWIZ_POS: str
    PARTS: List[str]

class Analysis(_AnalysisRequired, total=False):
    PREFIX: str
    SUFFIX: Dict[str, str]
    XPOS_GSUFF: str
    UNGRAMMATICAL: bool
    SYNTAX_INFO: SyntaxInfo

def _analyze_word_with_pos(ans: List[Analysis], start_pos: str, regex: re.Pattern[str], lemma_idx: int, word: str, infl_pos:str=None, lemma_pred=lambda l: True):
    if m := regex.fullmatch(word):
        parsed = list(m.groups())
        def rec(i: int, pos: str, obj: Analysis):
            if i >= len(parsed):
                return [obj]

            part = parsed[i]
            if not part:
                return rec(i + 1, pos, obj)

            if i < lemma_idx:
                part = part + "-"
                obj["PREFIX"] = part

            elif i > lemma_idx:
                part = "-" + part
            
                if pos == "v" and part in {"-Daq", "-vo'", "-mo'", "-vaD", "-'e'"}:
                    pos = "n"

                if "SUFFIX" not in obj:
                    obj["SUFFIX"] = {}
                
                obj["SUFFIX"][SUFFIX_TYPES[(part, pos)]] = part
                j, m = _next_morphem(parsed, i)
                if m in {"be'", "qu'"}:
                    obj["SUFFIX"][SUFFIX_TYPES[(part, pos)]] += m
                    i = j
            
            else:
                obj["LEMMA"] = part

            new_pos = pos

            if pos == "v" and part in ["-ghach", "-wI'"]:
                new_pos = "n"
            
            if i == lemma_idx and infl_pos:
                new_pos = infl_pos
            
            if (part + ":" + pos) in WORD_INDEX:
                objs = []
                for entry in WORD_INDEX[part + ":" + pos]:
                    new_obj = copy.deepcopy(obj)
                    new_obj["PARTS"].append(part + ":" + entry["part_of_speech"])
                    if i == lemma_idx:
                        #new_obj["BOQWIZ"] = entry

                        new_obj["XPOS"] = _get_xpos(entry)
                        new_obj["BOQWIZ_POS"] = entry["part_of_speech"]

                        if not lemma_pred(entry):
                            continue
                    
                    objs += rec(i + 1, new_pos, new_obj)
                
                return objs
            
            else:
                obj["PARTS"].append(part)
            
                return rec(i + 1, new_pos, obj)
        
        start_obj: Analysis = {
            "WORD": word,
            "POS": start_pos.upper(),
            "XPOS": "UNK",
            "BOQWIZ_POS": "?",
            "PARTS": [],
            "LEMMA": "",
        }

        objs = rec(0, start_pos, start_obj)
        
        ans += objs

GENDERED_SUFFIXES = {
    "being": {
        "-wI':n:suff",
        "-lI':n:suff",
        "-ma':n:suff",
        "-ra':n:suff",
        "-pu':n:suff"
    },
    "body": {"-Du':n:suff"},
    "other": set(),
}

def analyze(word: str, include_syntactical_info=False) -> List[Analysis]:
    """
    Given a word, returns a list of possible analyses.

    Each analysis has:
    - WORD: the analysed word itself
    - LEMMA: the base form of the word, without any affixes
    - POS: either `"N"`, `"V"` or `"OTHER"`
    - XPOS: a more detailed part of speech tag
    - XPOS_GSUFF: XPOS + grammatical suffix (N5 or V9 type suffix or grammatical number suffix)
    - PARTS: a list of boQwI' identifiers for morphemes
    - PREFIX: (optional) the prefix of the word
    - SUFFIX: (optional) a dict where key is the suffix type (like V7) and values is the suffix (like `-ta'be'`). Rovers are included in their preceding suffixes
    """
    ans: List[Analysis] = []
    
    _analyze_word_with_pos(ans, "n", NOUN_REGEX, 0, word)
    _analyze_word_with_pos(ans, "n", NUMBER_REGEX, 0, word)
    if not ans:
        _analyze_word_with_pos(ans, "n", PRONOUN_VERB_REGEX, 0, word, infl_pos="v", lemma_pred=lambda e: "pro" in e["part_of_speech"])

    _analyze_word_with_pos(ans, "v", VERB_REGEX, 1, word)
    _analyze_word_with_pos(ans, "v", STATIVE_VERB_REGEX, 0, word, lemma_pred=lambda e: "is" in e["part_of_speech"])

    if word + ":other" in WORD_INDEX:
        for entry in WORD_INDEX[word + ":other"]:
            ans.append({
                "WORD": word,
                "LEMMA": entry["entry_name"],
                "POS": "OTHER",
                "XPOS": _get_xpos(entry),
                "BOQWIZ_POS": entry["part_of_speech"],
                "PARTS": [ entry["entry_name"] + ":" + entry["part_of_speech"] ],
            })
    
    for analysis in ans:
        analysis["XPOS_GSUFF"] = analysis["XPOS"]
        if "SUFFIX" in analysis:
            if "V9" in analysis["SUFFIX"]:
                analysis["XPOS_GSUFF"] += "." + analysis["SUFFIX"]["V9"][1:]
            
            if "N5" in analysis["SUFFIX"]:
                analysis["XPOS_GSUFF"] += "." + analysis["SUFFIX"]["N5"][1:]
            
            if "L2" in analysis["SUFFIX"]:
                analysis["XPOS_GSUFF"] += "." + analysis["SUFFIX"]["L2"][1:]
        
        # Check for easy morphological errors:
        
        if analysis["POS"] == "N":
            gender = "body" if "body" in analysis["PARTS"][0] else \
                "being" if "being" in analysis["PARTS"][0] else \
                "other"
            
            for part in analysis["PARTS"]:
                for other_gender in {"being", "body", "other"} - {gender}:
                    if part in GENDERED_SUFFIXES[other_gender]:
                        analysis["UNGRAMMATICAL"] = True
        
        if "-vIS:v:suff" in analysis["PARTS"] and \
            "-taH:v:suff" not in analysis["PARTS"]:
            analysis["UNGRAMMATICAL"] = True
        
        if "-lu':v:suff" in analysis["PARTS"] and analysis.get("PREFIX", "") not in {"vI-", "Da-", "wI-", "bo-", "", "lu-"}:
            analysis["UNGRAMMATICAL"] = True
        
        if analysis["XPOS"] in {"VS", "VI"} and analysis.get("PREFIX", "") not in {"yI-", "pe-", "jI-", "bI-", "ma-", "Su-", ""} and "-moH:v:suff" not in analysis["PARTS"]:
            analysis["UNGRAMMATICAL"] = True
        
        if "-ghach:v:suff" in analysis["PARTS"] and analysis["PARTS"].index("-ghach:v:suff") - analysis["PARTS"].index(analysis["LEMMA"] + ":" + analysis["BOQWIZ_POS"]) < 2:
            analysis["UNGRAMMATICAL"] = True
        
        # Add extra information regarding the words rule in the syntax
        if include_syntactical_info:
            info: SyntaxInfo = {}
            analysis["SYNTAX_INFO"] = info
            if analysis["POS"] == "N":
                info["ROLE"] = "NP"
            
            elif analysis["POS"] == "V" and analysis.get("SUFFIX", {}).get("V9", None) in {"-wI'", "-ghach"}:
                info["ROLE"] = "NP"
            
            elif analysis["POS"] == "V":
                info["ROLE"] = "VP"
            
            else:
                info["ROLE"] = "OTHER"
            
            if info["ROLE"] == "VP":
                voice = "NP" if "-lu':v:suff" in analysis["PARTS"] else "P"
                subj_person: Set[Person]
                subj_number: Optional[Number]
                obj_person: Set[Person]
                obj_number: Optional[Number]
                if "PREFIX" in analysis or voice == "NP":
                    subj_person, subj_number, obj_person, obj_number = PREFIX_TABLE[(analysis.get("PREFIX", "-"), voice)]
                
                elif analysis["XPOS"] in {"VS", "VI"}:
                    subj_person = {3}
                    subj_number = None
                    obj_person = {0}
                    obj_number = None

                else:
                    subj_person = {3}
                    subj_number = None
                    obj_person = {0, 3}
                    obj_number = None
                
                info["SUBJECT_PERSON"] = subj_person
                info["SUBJECT_NUMBER"] = subj_number
                info["OBJECT_PERSON"] = obj_person
                info["OBJECT_NUMBER"] = obj_number
            
            elif info["ROLE"] == "NP":
                if "inhps" in analysis["BOQWIZ_POS"] or "inhpl" in analysis["BOQWIZ_POS"]:
                    info["PLURAL"] = False

                if analysis.get("SUFFIX", {}).get("N2", None) in {"-pu'", "-Du'", "-mey"}:
                    info["PLURAL"] = True

    return ans

def _word_to_conllu(num: int, word: str, analyses: List[Analysis]) -> tuple:
    if len(analyses) == 0:
        return (str(num), word, "_", "_", "_", "_", "_", "_", "_", "_")
    
    if len(analyses) > 1:
        if (all(a["POS"] == analyses[0]["POS"] for a in analyses)
            and all(a["LEMMA"] == analyses[0]["LEMMA"] for a in analyses)):
            pass

        else:
            return (str(num), word, "_", "_", "_", "_", "_", "_", "_", "_")
    
    analysis = analyses[0]
    feats = []
    extra = []
    if "PREFIX" in analysis:
        extra.append("Prefix=" + analysis["PREFIX"])
        f = UNIVERSAL_FEATURES.get((analysis["PREFIX"], "P" if not analysis.get("SUFFIX", {}).get("V5", "") == "-lu'" else "NP"), None)
        if f:
            feats.append(f)
    
    elif XPOS_TO_UPOS[analysis["XPOS"]] in {"VERB", "ADJ"}:
        f = UNIVERSAL_FEATURES.get(("-", "P" if not analysis.get("SUFFIX", {}).get("V5", "") == "-lu'" else "NP"), None)
        if f:
            feats.append(f)
    
    xpos = analysis["XPOS_GSUFF"]
    upos = XPOS_TO_UPOS[analysis["XPOS"]]
    
    if "SUFFIX" in analysis:
        for key in analysis["SUFFIX"]:
            extra.append("Suffix" + key + "=" + analysis["SUFFIX"][key])
            if (analysis["SUFFIX"][key], key) in UNIVERSAL_FEATURES:
                feats.append(UNIVERSAL_FEATURES[(analysis["SUFFIX"][key], key)])

    return (str(num), word, analysis["LEMMA"], upos, xpos, "_" if not feats else "|".join(feats), "_", "_", "_", "_" if not extra else "|".join(extra))

TokenType = Literal["WORD", "SPACE", "PUNCT"]

def tokenize(sentence: str) -> List[Tuple[TokenType, str]]:
    """
    Tokenizes the given text and returns a list of tuples with form `(type, value)` where type is one of `"WORD"`, `"SPACE"`, `"PUNCT"`.
    """
    tokens: List[Tuple[TokenType, str]] = []
    for matches in re.findall(r"([a-zA-Z'0-9]+|\s+|(.)\2*)", sentence):
        token = matches[0]
        if re.fullmatch(r"[a-zA-Z'0-9]+", token):
            tokens.append(("WORD", token))
        
        elif re.fullmatch(r"\s+", token):
            tokens.append(("SPACE", token))
        
        elif token:
            tokens.append(("PUNCT", token))
    
    return tokens

def text_to_conllu_without_tagger(text: str) -> str:
    """
    Converts a given text to the CONLL-U format with morphological information (dependencies are not parsed).
    If a word has multiple analyses, its POS and other info is not included (as they are not exactly known).
    """
    ans = []
    tokens = tokenize(text)
    i = 1
    for token_type, token in tokens:
        if token_type == "SPACE":
            continue

        elif token_type == "PUNCT":
            ans.append("{}\t{}\t{}\tPUNCT\tPUNCT\t_\t_\t_\t_\t_".format(i, token, token))
            if token in ".!?":
                i = 1
                ans.append("")
            
            else:
                i += 1
        
        else:
            analyses = analyze(token)
            ans.append("\t".join(_word_to_conllu(i, token, analyses)))
            i += 1
    
    return "\n".join(ans)
