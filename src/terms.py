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


def compute_natural_weight(count: int) -> float:
    return count
