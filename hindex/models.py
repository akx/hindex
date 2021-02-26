import re

import attr


@attr.s(auto_attribs=True)
class Term:
    original: str
    norm: str


@attr.s(auto_attribs=True)
class TermWithContext(Term):
    before: str
    text: str
    after: str
    doc_id: str

    @classmethod
    def from_match_and_source(
        cls,
        term: Term,
        *,
        match: re.Match,
        source: str,
        context_length: int,
        doc_id: str,
    ) -> "TermWithContext":
        if context_length > 0:
            start, end = match.span()
            before_start = max(0, start - context_length)
            after_end = end + context_length
            before = source[before_start:start]
            after = source[end:after_end]
        else:
            before = ""
            after = ""
        return TermWithContext(
            original=term.original,
            norm=term.norm,
            doc_id=doc_id,
            before=before.strip(),
            text=match.group(0).strip(),
            after=after.strip(),
        )

    @classmethod
    def from_term_with_match(
        cls,
        term: "TermWithMatch",
        *,
        context_length: int,
    ):
        return cls.from_match_and_source(
            term,
            context_length=context_length,
            match=term.match,
            source=term.source,
            doc_id=term.doc_id,
        )


@attr.s(auto_attribs=True)
class TermWithMatch(Term):
    match: re.Match
    source: str
    doc_id: str
