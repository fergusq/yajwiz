from functools import reduce
import re
from typing import Callable, Dict, List, NamedTuple, Optional, Set, Tuple, Union
from yajwiz.types import Analysis, ProofreaderError, TokenType, Token

def _bitset_to_bitstring(bitset: Dict[str, str], included_bits: List[str]) -> str:
    return "".join(bitset.get(b, ".") for b in included_bits)

PUNCTUATION_NAMES = {
    ".": {"Period"},
    ",": {"Comma"},
    ":": {"Colon"},
    ";": {"Semicolon"},
    "!": {"ExclamationMark"},
    "?": {"QuestionMark"},
    "\"": {"QuotationMark"},
    "“": {"QuotationMark", "Left"},
    "”": {"QuotationMark", "Right"},
    "‘": {"QuotationMark", "Left"},
    "’": {"QuotationMark", "Right"},
    "«": {"QuotationMark", "Left"},
    "»": {"QuotationMark", "Right"},
    "‹": {"QuotationMark", "Left"},
    "›": {"QuotationMark", "Right"},
    "<": {"LessThanSign", "AngleBracket", "Left"},
    ">": {"GreaterThanSign", "AngleBracket", "Right"},
    "(": {"Parenthesis", "Left"},
    ")": {"Parenthesis", "Right"},
    "{": {"Brace", "Left"},
    "}": {"Brace", "Right"},
    "[": {"Bracket", "Left"},
    "]": {"Bracket", "Right"},
    "*": {"Asterisk"},
    "/": {"Slash"},
    "\\": {"Backslash"},
    "`": {"Backtick"},
    "~": {"Tilde"},
    "^": {"CircumflexMark"},
    "=": {"EqualsSign"},
    "+": {"PlusSign"},
    "-": {"MinusSign"},
    "–": {"Dash"},
    "_": {"Underscore"},
    "%": {"PercentSign"},
    "$": {"DollarSign", "CurrencySign"},
    "€": {"EuroSign", "CurrencySign"},
}

def _tokens_to_bitstring(tokens: List[Token], included_bits: List[str]) -> str:
    token_bitsets = []
    for token in tokens:
        if token.token_type == "PUNCT":
            bitset = {"Punct"}
            if token.text in PUNCTUATION_NAMES:
                bitset |= PUNCTUATION_NAMES[token.text]
            
            if len(token.text) == 1:
                bitset |= {str(ord(token.text))}
            
            token_bitsets.append([{bit: "1" for bit in bitset}])
        
        else:
            token_bitsets.append([a["SYNTAX_INFO"]["BITS"] for a in token.analyses])

    bitstring = ""
    for i, token_bitset in enumerate(token_bitsets):
        bitset = {}
        for bit in included_bits:
            if token_bitset and all(bit in s for s in token_bitset):
                bitset[bit] = "1"
            
            elif all(bit not in s for s in token_bitset):
                bitset[bit] = "0"
        
        bitstring += "," + str(i) + ":" + _bitset_to_bitstring(bitset, included_bits)
    
    return bitstring

def _pattern_to_regex(pattern: str) -> Tuple[re.Pattern, List[str]]:
    regex_parts = []
    while pattern:
        group_name = None
        if m := re.match(r"\w+", pattern):
            group_name = m.group(0)
            pattern = pattern[len(group_name):]
        
        if pattern[0] == "{":
            pattern = pattern[1:]
            end_index = pattern.index("}")
            bitcond = {}
            for bit in pattern[:end_index].split(","):
                val = "1"
                if bit.startswith("!"):
                    val = "0"
                    bit = bit[1:]
                
                bitcond[bit] = val
            
            if group_name:
                regex_parts += [f"(?P<{group_name}>"]
                regex_parts += [bitcond]
                regex_parts += [")"]
            
            else:
                regex_parts += [bitcond]
            
            pattern = pattern[end_index+1:]
        
        elif pattern[0] == "(":
            if group_name:
                regex_parts += [f"(?P<{group_name}>"]

            else:
                regex_parts += ["(?:"]
            
            pattern = pattern[1:]
        
        elif not group_name and pattern[0] in "*+?|)":
            regex_parts += [pattern[0]]
            pattern = pattern[1:]
        
        elif pattern[0] == "." or group_name and pattern[0].isspace():
            if group_name:
                regex_parts += [f"(?P<{group_name}>"]

            regex_parts += [{}]
            if group_name:
                regex_parts += [")"]
            
            pattern = pattern[1:]
        
        elif pattern[0].isspace():
            pattern = pattern[1:]
        
        else:
            raise Exception("Invalid pattern")
    
    bits = set()
    for part in regex_parts:
        if isinstance(part, dict):
            bits |= set(part.keys())
    
    included_bits = list(bits)

    regex = ""
    for part in regex_parts:
        if isinstance(part, str):
            regex += part
        
        elif isinstance(part, dict):
            regex += r",\d+:" + _bitset_to_bitstring(part, included_bits)
    
    return re.compile(regex), included_bits

class GrammarRule(NamedTuple):
    name: str
    pattern: str
    re_pattern: re.Pattern
    included_bits: List[str]
    message: str
    replacement: Optional[str]
    positive_examples: List[str]
    negative_examples: List[str]

    @staticmethod
    def from_dict(d={}, **d2) -> "GrammarRule":
        d = {**d, **d2}
        pattern, included_bits = _pattern_to_regex(d["pattern"])
        return GrammarRule(
            name=d["name"],
            pattern=d["pattern"],
            re_pattern=pattern,
            included_bits=included_bits,
            message=d["message"],
            replacement=d.get("replacement"),
            positive_examples=d.get("positive_examples", []),
            negative_examples=d.get("negative_examples", []),
        )

GRAMMAR_RULES: List[GrammarRule] = [
    GrammarRule.from_dict(
        name="aspect in complex sentence 1",
        pattern=r"({«'e'»}|{«net»}) ({«neH»}|{«neHHa'»})? {V7}",
        message="ASPECT SUFFIX IN COMPLEX SENTENCE",
        positive_examples=["DaH 'e' vIleghpu'", "DaH net leghtaH", "DaH 'e' neH vIleghpu'", "DaH net neHHa' leghtaH"],
        negative_examples=["DaH 'e' vIlegh", "DaH net legh", "DaH 'e' neH vIlegh", "DaH net neHHa' legh"],
    ),
    GrammarRule.from_dict(
        name="net with illegal subject",
        pattern=r"{«net»} ({Subj1}|{Subj2}|{-lu'})",
        message="net WITH ILLEGAL SUBJECT",
        positive_examples=["jISuv net vISov", "jISuv net boSov", "jISuv net Sovlu'"],
        negative_examples=["jISuv net Sov", "gheDlIj DaHoHHa'pu' moratlh\n'ej gheDDaj charghHa' molor\nQob qo' qeylIs yIqIm"],
    ),
    GrammarRule.from_dict(
        name="illegal 'e' or net",
        pattern=r"error({«'e'»}|{«net»}) verb({reH:v}|{Quj}|{jatlh:v}|{ja':v})",
        message="$error WITH $verb\\lemma",
        replacement="",
        positive_examples=["tugh jISuv 'e' qaja'."],
        negative_examples=["tugh jISuv. qaja'."]
    ),
    GrammarRule.from_dict(
        name="'e' with neH 1",
        pattern=r"error{«'e'»} {neH:v}",
        message="'e' WITH neH",
        replacement="",
        positive_examples=["tugh jISuv 'e' vIneH."],
        negative_examples=["tugh jISuv vIneH."]
    ),
    GrammarRule.from_dict(
        name="'e' with neH 2",
        pattern=r"error{«'e'»} {«neH»} {!Obj3}",
        message="'e' WITH neH",
        replacement="",
        positive_examples=["tugh jISuv 'e' neH qorDu'wIj."],
        negative_examples=["tugh jISuv neH qorDu'wIj.", "tugh jISuv 'e' neH DaSov."]
    ),
]

def _replace_groups(tokens: List[Token], groups: Dict[str, List[int]], text: str) -> str:
    for g in groups:
        if f"${g}" in text:
            text = text.replace(f"${g}\\lemma", " ".join(tokens[i].analyses[0]["LEMMA"] if tokens[i].analyses else tokens[i].text for i in groups[g]))
            text = text.replace(f"${g}", " ".join(tokens[i].text for i in groups[g]))
    
    return text

def proofread_tokens(tokens: List[Token], rules=GRAMMAR_RULES) -> List[ProofreaderError]:
    errors = []
    for token in tokens:
        if token.token_type == "WORD":
            if len(token.analyses) == 0:
                errors.append(ProofreaderError("unknown word", f"UNKNOWN WORD {token.text}", token.location, token.end_location()))
            
            elif all(a.get("UNGRAMMATICAL", None) for a in token.analyses):
                errors.append(ProofreaderError("ungrammatical", token.analyses[0]["UNGRAMMATICAL"], token.location, token.end_location()))
    
    for rule in rules:
        bitstring = _tokens_to_bitstring(tokens, rule.included_bits)
        #print(rule.included_bits)
        #print(rule.re_pattern)
        #print(bitstring)
        if m := rule.re_pattern.search(bitstring):
            groups = {key: [int(t[1:-1]) for t in re.findall(r",\d+:", value)] for key, value in m.groupdict().items()}
            #print(groups)

            replacement = rule.replacement
            if replacement is not None:
                replacement = _replace_groups(tokens, groups, replacement)
            
            message = _replace_groups(tokens, groups, rule.message)
            if "error" in groups:
                span = groups["error"]
            
            else:
                span = [int(t[1:-1]) for t in re.findall(r",\d+:", m.group(0))]
            
            start, end = tokens[span[0]].location, tokens[span[-1]].end_location()
            errors.append(ProofreaderError(rule.name, message, start, end, replacement=replacement))

    return errors

def test_grammar_rules():
    from . import analyzer
    succ = 0
    fail = 0
    for rule in GRAMMAR_RULES:
        examples: List[Tuple[str, str]] = [("Positive", example) for example in rule.positive_examples]
        examples += [("Negative", example) for example in rule.negative_examples]
        for example_type, example in examples:
            tokens = analyzer._tokenize_for_proofreader(example)
            errors = proofread_tokens(tokens, [rule])
            for error in errors:
                if example_type == "Positive" and rule.name == error.rule_name:
                    succ += 1
                
                elif rule.name == error.rule_name:
                    print(rule.name)
                    print(example_type + " example:", example)
                    print("->", error)
                    print()
                    fail += 1
            
            if not errors:
                if example_type == "Positive":
                    print(rule.name)
                    print("Positive example:", example)
                    print("NO ERRORS")
                    print()
                    fail += 1
                
                else:
                    succ += 1
    
    print(f"Result: {succ} ok, {fail} failed")

if __name__ == "__main__":
    test_grammar_rules()