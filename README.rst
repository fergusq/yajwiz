yajwI'
======

**yajwI'** is a Klingon NLP toolkit that includes basic tokenization, morphological analysis and POS tagging.

It heavily uses the `boQwI' dictionary <https://github.com/De7vID/klingon-assistant-data>`_.

Installation
------------

yajwI' requires Python 3.8 or newer.

It can be installed from PyPI::

    pip install yajwiz

Tokenization
------------

The library includes very simple tokenization.

>>> import yajwiz
>>> yajwiz.tokenize("Hegh neH chav qoH. qanchoHpa' qoH, Hegh qoH.")
[('WORD', 'Hegh'), ('SPACE', ' '), ('WORD', 'neH'), ('SPACE', ' '), ('WORD', 'chav'), ('SPACE', ' '), ('WORD', 'qoH'), ('PUNCT', '.'), ('SPACE', ' '), ('WORD', "qanchoHpa'"), ('SPACE', ' '), ('WORD', 'qoH'), ('PUNCT', ','), ('SPACE', ' '), ('WORD', 'Hegh'), ('SPACE', ' '), ('WORD', 'qoH'), ('PUNCT', '.')]


Morphological analysis
----------------------

The ``yajwiz.analyze`` function parses a word and returns a list of possible parses and a lot of extra information.

>>> yajwiz.analyze("yInwI'")
[
    {
        'WORD': "yInwI'",
        'POS': 'N',
        'XPOS': 'N',
        'PARTS': ['yIn:n', "-wI':n:suff"],
        'LEMMA': 'yIn',
        'SUFFIX': {'N4': "-wI'"},
        'XPOS_GSUFF': 'N',
        'UNGRAMMATICAL': True
    },
    {
        'WORD': "yInwI'",
        'POS': 'V',
        'XPOS': 'VT',
        'PARTS': ['yIn:v:t_c', "-wI':v:suff"],
        'LEMMA': 'yIn',
        'SUFFIX': {'V9': "-wI'"},
        'XPOS_GSUFF': "VT.wI'"
    }
]

Currently the analyzer is very permissive and does allow using wrong plurals and possessive suffixes (eg. **yInwI'** instead of **yInwIj**). It will try to mark this kind of errors with ``'UNGRAMMATICAL': True``. It detects the following errors:

- Using **-pu'**, **-wI'**, **-lI'**, etc. when the noun is not a person noun
- Using **-Du'** when the noun is not a body part
- Using **-vIS** without using **-taH**
- Using **-lu'** with an illegal verb prefix
- Using intransitive verbs with prefixes indicating object
- Using **-ghach** without any other verb suffix

There is also a simpler function ``yajwiz.split_to_morphemes``, that returns a set of tuples of strings (usually there will be only one tuple in the set):

>>> yajwiz.split_to_morphemes("yInwI'")
{('yIn', "-wI'")}

List of Parts of Speech
.......................

===== ===========
XPOS  Explanation
===== ===========
VS    Stative verb
VT    Transitive verb
VI    Intransitive verb
VA    Transitive and intransitive verb
V?    Verb with unknown transitivity
NL    Person noun
NB    Body part noun
PRON  Pronoun (including **'Iv** and **nuq**: it is a noun that can function as a copula)
NUM   Number
N     Other noun
ADV   Adverb
EXCL  Exclamation
CONJ  Conjunction
QUES  Question word (other than **'Iv** and **nuq**)
UNK   Unknown
===== ===========

CONLL-U files and POS tagger
----------------------------

CONLL-U files are a popular data format for storing annotated linguistic data.

yajwI' can generate CONLL-U files filled with morphological information (it does not support dependency parsing).

Below is an example script that first parses a text without a trained POS tagger,
then trains a POS tagger with it and finally parses the text with the tagger and saves the result to a CONLL-U file.

.. code:: python

    import yajwiz

    with open("prose-corpus.txt", "r") as f:
        text = f.read()

    conllu = yajwiz.text_to_conllu(text)

    tagger = yajwiz.Tagger()
    tagger.train(yajwiz.conllu_to_tagged_list(conllu))

    conllu = yajwiz.text_to_conllu(text, tagger)

    with open("prose-corpus.conllu", "w") as f:
        f.write(conllu)

Without a trained POS tagger, ambiguous words will be left without a tag:

.. code::

    # Hegh neH chav qoH.
    1	Hegh	_	_	_	_	_	_	_	_
    2	neH	_	_	_	_	_	_	_	_
    3	chav	_	_	_	_	_	_	_	_
    4	qoH	qoH	NOUN	N	_	_	_	_	_
    5	.	.	PUNCT	PUNCT	_	_	_	_	_

    # qanchoHpa' qoH, Hegh qoH.
    1	qanchoHpa'	qan	VERB	V?.pa'	Person=3|ObjPerson=3,0	_	_	_	SuffixV3=-choH|SuffixV9=-pa'
    2	qoH	qoH	NOUN	N	_	_	_	_	_
    3	,	,	PUNCT	PUNCT	_	_	_	_	_
    4	Hegh	_	_	_	_	_	_	_	_
    5	qoH	qoH	NOUN	N	_	_	_	_	_
    6	.	.	PUNCT	PUNCT	_	_	_	_	_

After training the tagger, it will take the "best guess" when deciding the POS.

.. code::

    # Hegh neH chav qoH.
    1	Hegh	Hegh	VERB	VT	Person=3|ObjPerson=3,0	_	_	_	_
    2	neH	neH	ADV	ADV	_	_	_	_	_
    3	chav	chav	VERB	VT	Person=3|ObjPerson=3,0	_	_	_	_
    4	qoH	qoH	NOUN	N	_	_	_	_	_
    5	.	.	PUNCT	PUNCT	_	_	_	_	_

    # qanchoHpa' qoH, Hegh qoH.
    1	qanchoHpa'	qan	VERB	V?.pa'	Person=3|ObjPerson=3,0	_	_	_	SuffixV3=-choH|SuffixV9=-pa'
    2	qoH	qoH	NOUN	N	_	_	_	_	_
    3	,	,	PUNCT	PUNCT	_	_	_	_	_
    4	Hegh	Hegh	VERB	VT	Person=3|ObjPerson=3,0	_	_	_	_
    5	qoH	qoH	NOUN	N	_	_	_	_	_
    6	.	.	PUNCT	PUNCT	_	_	_	_	_

In this example the tagger made a mistake: it classified the first **Hegh** as VT, although it should be N. I don't have a correctly tagged corpus, so evaluating the tagger is currently impossible. :(

Copyright
---------

yajwiz (c) 2020 Iikka Hauhio

This program a contains the `boQwI' dictionary <https://github.com/De7vID/klingon-assistant-data>`_ (``data.json``) that is licensed under the Apache License 2.0.

The Python files are also licensed under the Apache License 2.0. See the LICENSE file for more details.
