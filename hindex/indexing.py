from typing import Iterable

import bs4

from hindex.models import TermWithContext
from hindex.terms import split_into_terms, make_stopword_remover
from hindex.utils import get_extension

HTML_EXTENSIONS = {".html", ".htm"}


def index_file(filename, context_length=20) -> Iterable[TermWithContext]:
    language, text = read_file(filename)
    term_gen = split_into_terms(text, language=language, doc_id=filename)
    stopword_remover = make_stopword_remover(language=language)

    for term in stopword_remover(term_gen):
        yield TermWithContext.from_term_with_match(term, context_length=context_length)


def read_file(filename):
    language = "english"  # TODO: detect language
    if get_extension(filename) in HTML_EXTENSIONS:
        with open(filename, "rb") as infp:
            soup = bs4.BeautifulSoup(infp.read(), features="html.parser")
            body = soup.find("body")
            text = body.get_text(separator="\n")
    else:
        raise NotImplementedError(f"... {filename}")
    return language, text
