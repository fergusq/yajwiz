from typing import Dict, List, Literal, NamedTuple, Optional, Set, Tuple, TypedDict
from .tables import Person, Number

# Morphological analysis

Xpos = Literal["VS", "VT", "VI", "VA", "V?", "NL", "NB", "PRON", "NUM", "N", "ADV", "EXCL", "CONJ", "QUES", "UNK"]

class SyntaxInfo(TypedDict, total=False):
    ROLE: Literal["NP", "VP", "OTHER"]
    OBJECT_PERSON: Set[Person]
    OBJECT_NUMBER: Optional[Number]
    SUBJECT_PERSON: Set[Person]
    SUBJECT_NUMBER: Optional[Number]
    PLURAL: bool
    BITS: Set[str]

class _AnalysisRequired(TypedDict):
    WORD: str
    LEMMA: str
    POS: str
    XPOS: Xpos
    BOQWIZ_POS: str
    BOQWIZ_ID: str
    PARTS: List[str]

class Analysis(_AnalysisRequired, total=False):
    PREFIX: str
    SUFFIX: Dict[str, str]
    XPOS_GSUFF: str
    UNGRAMMATICAL: str
    SYNTAX_INFO: SyntaxInfo

TokenType = Literal["WORD", "SPACE", "PUNCT"]

class Token(NamedTuple):
    location: int
    token_type: TokenType
    text: str
    analyses: List[Analysis]

    def end_location(self):
        return self.location + len(self.text)

# Grammar checking

class ProofreaderError(NamedTuple):
    rule_name: str
    message: str
    location: int
    end_location: int
    replacement: Optional[str] = None