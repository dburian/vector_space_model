from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class Posting:
    doc_id: str
    count: int
    next: Optional[Posting] = None


class InvertedIndex:
    def __init__(self, terms: dict[str, Posting], lasts: dict[str, Posting]) -> None:
        self._terms = terms
        self._lasts = lasts

    @property
    def terms(self) -> dict[str, Posting]:
        return self._terms

    @property
    def lasts(self) -> dict[str, Posting]:
        return self._lasts

    def add_posting(self, term: str, doc_id: str, count: int) -> None:
        posting = Posting(doc_id, count, self._terms.get(term, None))
        self._terms[term] = posting
        if term not in self._lasts:
            self._lasts[term] = posting

    def update_with(self, other: InvertedIndex) -> None:
        for term in other.terms.keys():
            prev_first = self._terms.get(term, None)
            self._terms[term] = other.terms[term]
            if prev_first is None:
                self._lasts[term] = other.lasts[term]
            else:
                other.lasts[term].next = prev_first

    def get_most_similar(
        self,
        query: dict[str, int],
        weighting: Callable[[int], float],
        first_k: int = 1000,
    ) -> list[tuple[float, str]]:
        q_norm = 0
        for count in query.values():
            q_norm += weighting(count) ** 2

        q_norm = math.sqrt(q_norm)
        query_weights = {term: count / q_norm for term, count in query.items()}

        scores = {}
        norms = {}
        for term, query_w in query_weights.items():
            posting = self._terms.get(term, None)
            while posting is not None:
                doc_weight = weighting(posting.count)
                scores[posting.doc_id] = (
                    scores.get(posting.doc_id, 0) + query_w * doc_weight
                )
                norms[posting.doc_id] = norms.get(posting.doc_id, 0) + doc_weight**2

                posting = posting.next

        min_heap = []
        for doc_id, count in scores.items():
            doc_score = count / math.sqrt(norms[doc_id])
            if len(min_heap) < first_k:
                heapq.heappush(min_heap, (doc_score, doc_id))
            elif doc_score > min_heap[0][0]:
                heapq.heappushpop(min_heap, (doc_score, doc_id))

        # get max similarity first
        return sorted(min_heap, key=lambda tup: tup[0], reverse=True)

    def _valid_check(self) -> bool:
        postings = 0
        for term in self._terms.keys():
            posting = self._terms[term]
            unique_ids = set()
            while posting is not None:
                if posting.doc_id in unique_ids:
                    return False

                unique_ids.add(posting.doc_id)
                posting = posting.next

            postings += len(unique_ids)

        print(f"All right here, postings: {postings}")
        return True

    def __str__(self) -> str:
        if not self._valid_check():
            return "invalid"
        string = ""
        for term in self._terms.keys():
            string += term + ":"
            posting = self._terms[term]
            while posting is not None:
                string += f" {posting.doc_id}({posting.count}) ->"
                posting = posting.next

            string += "\n"

        return string
