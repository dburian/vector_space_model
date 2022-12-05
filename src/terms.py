import math
import re
from collections import namedtuple
from typing import Callable, Optional

Term = namedtuple("Token", ["str", "count"])


def extract(
    string: str,
    separators: str,
    stop_words: Optional[set[str]] = None,
    term_map: Optional[Callable[[str], str]] = None,
) -> dict[str, int]:
    words = re.split("[" + separators + "]", string)

    if stop_words is None:
        stop_words = set()

    stop_words.add("")

    if term_map is None:
        # pylint: disable=unnecessary-lambda-assignment
        term_map = lambda x: x

    counts = {}
    for word in words:
        if word in stop_words:
            continue
        word = term_map(word)
        counts[word] = counts.get(word, 0) + 1

    return counts


def natural_weight(count: int, _) -> float:
    return count


def tf_idf_weight(
    document_count: int, term_frequency: int, document_frequency: int
) -> float:
    log_tf = 1 + math.log10(term_frequency)
    idf = (document_count / document_frequency) if document_frequency > 0 else 1
    log_idf = 1 + math.log10(idf)
    return log_tf * log_idf


WHSP_SEPS = r" \n\t"
PUNCT_SEPS = r",.:;?!"
PUNCT_EXT_SEPS = r'-_"\'/'
PAR_SEP = r"\[\]\(\)"
QUOT = r"\"'"
