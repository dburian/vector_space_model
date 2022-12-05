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
    def __init__(self) -> None:
        self._lasts = {}
        self._terms = {}
        self._doc_freq = {}

    def add_posting(self, term: str, doc_id: str, count: int) -> None:
        posting = Posting(doc_id, count, self._terms.get(term, None))
        self._terms[term] = posting
        if term not in self._lasts:
            self._lasts[term] = posting

        self._doc_freq[term] = self._doc_freq.get(term, 0) + 1

    def update_with(self, other: InvertedIndex) -> None:
        assert isinstance(
            other, InvertedIndex
        ), "InvertedIndex: Unable to merge instances of other classes."

        for term in other._terms:
            prev_first = self._terms.get(term, None)
            self._terms[term] = other._terms[term]
            if prev_first is None:
                self._lasts[term] = other._lasts[term]
            else:
                other._lasts[term].next = prev_first

            self._doc_freq[term] = self._doc_freq.get(term, 0) + other._doc_freq[term]

    def get_most_similar(
        self,
        query: dict[str, int],
        weighting: Callable[[int, int], float],
        first_k: int = 1000,
    ) -> list[tuple[float, str]]:
        query_weights = self._normalize_query(query, weighting)
        scores, norms = self._compute_scores_w_norms(query_weights, weighting)

        min_heap = []
        for doc_id, count in scores.items():
            doc_score = count / math.sqrt(norms[doc_id])
            if len(min_heap) < first_k:
                heapq.heappush(min_heap, (doc_score, doc_id))
            elif doc_score > min_heap[0][0]:
                heapq.heappushpop(min_heap, (doc_score, doc_id))

        # get max similarity first
        return sorted(min_heap, key=lambda tup: tup[0], reverse=True)

    def _normalize_query(
        self, query: dict[str, int], weighting: Callable[[int, int], float]
    ) -> dict[str, float]:
        q_norm = 0
        for term, count in query.items():
            q_norm += weighting(count, self._doc_freq.get(term, 0)) ** 2

        q_norm = math.sqrt(q_norm)
        return {term: count / q_norm for term, count in query.items()}

    def _compute_scores_w_norms(
        self, query_weights: dict[str, float], weighting: Callable[[int, int], float]
    ) -> tuple[dict[str, float], dict[str, float]]:
        scores = {}
        norms = {}
        for term, query_w in query_weights.items():
            term_doc_freq = self._doc_freq.get(term, 0)
            posting = self._terms.get(term, None)
            while posting is not None:
                doc_weight = weighting(posting.count, term_doc_freq)
                scores[posting.doc_id] = (
                    scores.get(posting.doc_id, 0) + query_w * doc_weight
                )
                norms[posting.doc_id] = norms.get(posting.doc_id, 0) + doc_weight**2

                posting = posting.next

        return scores, norms

    def _valid_check(self) -> bool:
        postings = 0
        for _, posting in self._terms.items():
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
        for term, posting in self._terms.items():
            string += term + ":"
            while posting is not None:
                string += f" {posting.doc_id}({posting.count}) ->"
                posting = posting.next

            string += "\n"

        return string
