import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import attr
import click
import nltk
import tqdm

from hindex.indexing import index_file, HTML_EXTENSIONS
from hindex.models import TermWithContext
from hindex.utils import get_extension

nltk.download("stopwords", quiet=True)


@click.command()
@click.option(
    "-i",
    "--input-dir",
    "input_dirs",
    type=click.Path(file_okay=False, dir_okay=True),
    multiple=True,
    required=True,
)
@click.option(
    "-o",
    "--out-dir",
    type=click.Path(file_okay=False, dir_okay=True, exists=False),
    required=True,
)
@click.option(
    "--context-length",
    type=int,
    default=30,
)
def main(input_dirs, out_dir, context_length):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = set()
    for input_dir in input_dirs:
        for dirpath, dirnames, filenames in os.walk(input_dir):
            for filename in filenames:
                ext = get_extension(filename)
                if ext in HTML_EXTENSIONS:
                    files.add(os.path.join(dirpath, filename))
    norm_terms = defaultdict(list)
    term_variants = defaultdict(set)
    doc_ids = set()
    with tqdm.tqdm(files) as file_iter:
        for filename in file_iter:
            for term in index_file(filename, context_length=context_length):
                norm_terms[term.norm].append(term)
                term_variants[term.norm].add(term.original)
                doc_ids.add(term.doc_id)
            file_iter.set_description(f"{len(norm_terms)} terms")
    doc_id_to_num_id = {
        doc_id: num_id for num_id, doc_id in enumerate(sorted(doc_ids), 1)
    }

    index_json = {
        "terms": {},
        "docs": doc_id_to_num_id,
    }
    subs = defaultdict(lambda: {"terms": {}})
    terms: Iterable[TermWithContext]
    for norm_term, terms in norm_terms.items():
        doc_num_ids = set(doc_id_to_num_id[term.doc_id] for term in terms)
        sub_id = get_sub_id(norm_term)
        index_json["terms"][norm_term] = [
            sub_id,
            len(doc_num_ids),
            len(terms),
            sorted(var for var in term_variants[norm_term] if var != norm_term),
        ]
        subs[sub_id]["terms"][norm_term] = [
            {
                "doc_id": doc_id_to_num_id[term.doc_id],
                "snippet": [term.before, term.text, term.after]
                if (term.before and term.after)
                else [],
            }
            for term in terms
        ]
    with open(out_dir / "index.json", "w") as outf:
        json.dump(index_json, outf, ensure_ascii=False)
    for sub_id, sub_json in subs.items():
        with open(out_dir / f"{sub_id}.json", "w") as outf:
            json.dump(sub_json, outf, ensure_ascii=False)


def get_sub_id(norm_term):
    return hashlib.md5(norm_term.encode()).hexdigest()[:2]
    #
    # if norm_term[:2].isalnum():
    #     sub_id = norm_term[:2]
    # else:
    #     sub_id = "%d.%d" % (ord(norm_term[0]), ord(norm_term[1]))
    # return sub_id


if __name__ == "__main__":
    main()
