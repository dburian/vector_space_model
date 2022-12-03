import sys
import time
from multiprocessing.pool import Pool
from typing import Iterator

from src import terms, utils
from src.document import DocumentCS
from src.index import InvertedIndex
from src.query import Query

SEPS = r' \t\n\.,\?!":;\[\]\(\)/'


def per_document(path: str) -> InvertedIndex:
    index = InvertedIndex({}, {})
    for doc in utils.get_document_iter(path, DocumentCS):
        doc_terms = terms.extract(doc.str_all, SEPS)
        for term_str, count in doc_terms.items():
            index.add_posting(term_str, str(doc.id), count)

    return index


def experiment(
    docs_paths_iter: Iterator[str], queries_path: str, output_file: str, run_id: str
) -> None:
    index = InvertedIndex({}, {})
    print("Indexing started")
    index_start = time.perf_counter()

    sys.setrecursionlimit(20000)
    with Pool() as pool:
        for i, docs_index in enumerate(
            pool.imap(per_document, docs_paths_iter, chunksize=20)
        ):
            print(f"\rRecieved index {i + 1}", end="")
            index.update_with(docs_index)

    # for i, path in enumerate(docs_paths_iter):
    #     print(f"\rRecieved index {i}", end="")
    #     for doc in utils.get_document_iter(path, DocumentCS):
    #         doc_terms = terms.extract(doc.str_all, r' \t\n\.,\?!":;\[\]\(\)/')
    #         for term in doc_terms:
    #             index.add_posting(term.str, str(doc.id), term.count)

    print()

    index_end = time.perf_counter()
    print(f"Indexing complete. Took: {index_end - index_start:.2f}s")

    with open(output_file, mode="w", encoding="utf-8") as output:
        for i, query in enumerate(utils.get_query_iter(queries_path, Query)):
            query_terms = terms.extract(query.title, SEPS)
            similars = index.get_most_similar(query_terms, terms.compute_natural_weight)
            utils.write_qrels(output, similars, query.id, run_id)
            print(f"\rGot similarities for query {i + 1}", end="")

    print()
    qrels_end = time.perf_counter()
    print(f"Computing similarities complete. Took {index_end - qrels_end:.2f}s")
