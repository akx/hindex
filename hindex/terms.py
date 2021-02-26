import re
from typing import Iterable

from nltk.corpus import stopwords

from hindex.models import TermWithMatch, Term
from hindex.utils import punc_remove_re, strip_set


def normalize_term(term, language):
    term = term.lower()
    if language == "english":
        term = re.sub("'s$", "", term)
    term = punc_remove_re.sub("", term)
    return term


def split_into_terms(
    source: str, *, doc_id: str, language: str
) -> Iterable[TermWithMatch]:
    for match in re.finditer(r"\S+", source, flags=re.I):
        word = match.group(0)
        word = word.strip(strip_set)
        if not word:
            continue
        norm = normalize_term(word, language)
        yield TermWithMatch(
            original=word, norm=norm, match=match, source=source, doc_id=doc_id
        )


def make_stopword_remover(*, language):
    stopword_set = set(stopwords.words(language))

    def remover(stream: Iterable[Term]):
        return (term for term in stream if term.norm not in stopword_set)

    return remover
