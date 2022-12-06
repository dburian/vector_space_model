import functools
from multiprocessing.pool import Pool
from typing import Callable, Iterator

import bs4

from src import log, terms, utils
from src.document import Document
from src.index import InvertedIndex
from src.query import Query

SEPS = terms.WHSP_SEPS + terms.PUNCT_SEPS + terms.PAR_SEP + terms.QUOT


def per_document_base(
    path: str,
    stopwords: set[str],
    create_document: Callable[[bs4.element.Tag], Document],
) -> tuple[InvertedIndex, int]:
    index = InvertedIndex()
    doc_count = 0
    for doc in utils.get_document_iter(path, create_document):
        doc_count += 1
        doc_terms = terms.extract(doc.str_all, SEPS, stopwords)
        for term_str, count in doc_terms.items():
            index.add_posting(term_str, str(doc.id), count)

    return index, doc_count


def per_document_cs(path: str) -> tuple[InvertedIndex, int]:
    stopwords = utils.load_stopwords("stopwords/kaggle_cs.txt")
    return per_document_base(path, stopwords, Document)


def per_document_en(path: str) -> tuple[InvertedIndex, int]:
    stopwords = utils.load_stopwords("stopwords/kaggle_en.txt")
    return per_document_base(path, stopwords, Document)


def experiment(
    lan: str,
    docs_paths_iter: Iterator[str],
    queries_path: str,
    output_file: str,
    run_id: str,
) -> None:
    stopwords = utils.load_stopwords(f"stopwords/kaggle_{lan}.txt")
    per_doc = per_document_cs if lan == "cs" else per_document_en
    index = InvertedIndex()

    log.timed("Indexing started")

    doc_count = 0
    with Pool() as pool:
        for docs_index, inner_doc_count in pool.imap(
            per_doc, docs_paths_iter, chunksize=20
        ):
            doc_count += inner_doc_count
            print(f"\rRecieved index {doc_count}", end="")
            index.update_with(docs_index)

    print()

    log.timed("Indexing complete")

    tfidf_weight = functools.partial(terms.tf_idf_weight, doc_count)
    with open(output_file, mode="w", encoding="utf-8") as output:
        for i, query in enumerate(utils.get_query_iter(queries_path, Query)):
            query_terms = terms.extract(query.title, SEPS, stopwords)
            similars = index.get_most_similar(query_terms, tfidf_weight)
            utils.write_qrels(output, similars, query.id, run_id)
            print(f"\rGot similarities for query {i + 1}", end="")

    print()
    log.timed("Done")
