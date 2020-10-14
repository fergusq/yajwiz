from collections import defaultdict, Counter
import math
from re import T

from .analyzer import XPOS_INDEX, text_to_conllu_without_tagger, tokenize, analyze, _word_to_conllu

from typing import List, Tuple, Optional

def conllu_to_tagged_list(conllu_text: str) -> List[List[Tuple[str, Optional[str]]]]:
    sentences = []
    for line in conllu_text.split("\n"):
        line = line.strip()
        if not line:
            continue

        fields = line.split("\t")
        num = int(fields[0])
        form = fields[1]
        lemma = fields[2]
        _upos = fields[3]
        xpos = fields[4]

        if num == 1:
            sentences.append([])
        
        sentences[-1].append((lemma if lemma != "_" else form, xpos if xpos != "_" else None))
    
    return sentences

END_TOKEN: Tuple[str, Optional[str]] = ("$", "$")

class Tagger:
    """
    POS Tagger implementation that can fill missing POS information to sentences that have been mostly tagged
    """

    def __init__(self):
        self.word_dist = defaultdict(Counter)
        self.tag_dist1 = defaultdict(Counter)
        self.tag_dist2 = defaultdict(Counter)
        self.tags = set()
    
    def train(self, sentences: List[List[Tuple[str, Optional[str]]]]):
        for s in sentences:
            for (l1, p1), (_l2, p2), (_l3, p3) in zip(s, s[1:]+[END_TOKEN], s[2:]+[END_TOKEN, END_TOKEN]):
                if p1:
                    self.word_dist[p1][l1] += 1
                    if p2:
                        self.tag_dist1[p2][p1] += 1
                        self.tag_dist2[(p2, p3)][p1] += 1

                    self.tags.add(p1)
    
    def _get_word_prob(self, word, tag):
        p = self.word_dist[tag][word]
        t = sum(self.word_dist[tag].values())
        if p == 0 and word in XPOS_INDEX[tag] and tag in {"ADV", "CONJ"}:
            p = t / len(self.word_dist[tag])

        return -1000 if p == 0 else math.log(p / t)

    def _get_tag_prob(self, tag1, tag2, tag3):
        p = self.tag_dist2[(tag2, tag3)][tag1]
        t = sum(self.tag_dist2[(tag2, tag3)].values())
        if t == 0:
            p = self.tag_dist1[tag2][tag1]
            t = sum(self.tag_dist1[tag2].values())

        return -1000 if p == 0 else math.log(p / t)
    
    def tag(self, sent: List[Tuple[str, Optional[str]]]) -> List[Tuple[str, Optional[str]]]:
        sent = sent.copy()
        for i, ((l1, p1), (_l2, p2), (_l3, p3)) in reversed(list(enumerate(zip(sent, sent[1:] + [END_TOKEN], sent[2:] + [END_TOKEN, END_TOKEN])))):
            if not p1:
                max_score = -1e9
                max_tag: Optional[str] = None
                for tag in self.tags:
                    if "." in tag:
                        continue

                    score = self._get_word_prob(l1, tag) + self._get_tag_prob(tag, p2, p3)
                    if score > max_score:
                        max_score = score
                        max_tag = tag
                
                if max_tag:
                    sent[i] = (l1, max_tag)
        
        return sent

def text_to_conllu(text: str, tagger: Optional[Tagger] = None) -> str:
    """
    Converts a given text to the CONLL-U format with morphological information (dependencies are not parsed).
    If a word has multiple analyses, its POS and other info is not included (as they are not exactly known).

    If a tagger is provided, uses it to take the "best guess" when selecting from multiple analyses.
    """

    if not tagger:
        return text_to_conllu_without_tagger(text)
    
    ans = ""

    conllu = []
    tagged_sent = []
    tokens = tokenize(text)

    def tag_and_append():
        nonlocal ans, conllu, tagged_sent
        guessed_tags = tagger.tag(tagged_sent)
        for i, ((l1, p1), (_l2, p2)) in enumerate(zip(tagged_sent, guessed_tags)):
            if not p1 and p2:
                analyses = analyze(l1)
                for analysis in analyses:
                    if analysis["XPOS_GSUFF"] == p2:
                        conllu[i] = "\t".join(_word_to_conllu(i+1, l1, [analysis]))
                        break
        
        ans += "\n\n" + "\n".join(conllu)
        conllu = []
        tagged_sent = []

    i = 1
    for token_type, token in tokens:
        if token_type == "SPACE":
            continue

        elif token_type == "PUNCT":
            conllu.append("{}\t{}\t{}\tPUNCT\tPUNCT\t_\t_\t_\t_\t_".format(i, token, token))
            tagged_sent.append((token, "PUNCT"))
            if token in ".!?":
                i = 1
                tag_and_append()
            
            else:
                i += 1
        
        else:
            analyses = analyze(token)
            fields = _word_to_conllu(i, token, analyses)
            conllu.append("\t".join(fields))
            if fields[2] == "_":
                tagged_sent.append((token, None))
            
            else:
                tagged_sent.append((fields[2], fields[4]))
            i += 1
    
    if conllu:
        tag_and_append()
    
    return ans