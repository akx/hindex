import os
import re
import unicodedata

punctuation_chars = set()
whitespace_chars = set()

for cp in range(65535):
    ch = chr(cp)
    cat = unicodedata.category(ch)
    if cat[0] == "P" or cat[0] == "S":
        punctuation_chars.add(ch)
    elif cat[0] == "Z":
        whitespace_chars.add(ch)

strip_set = "".join(sorted(set(punctuation_chars | whitespace_chars)))
punc_remove_re = re.compile("[%s]" % "|".join(re.escape(c) for c in strip_set))


def get_extension(filename):
    return os.path.splitext(filename)[1].lower()
