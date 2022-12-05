import functools
from multiprocessing.pool import Pool
from typing import Callable, Iterator, Optional

import bs4
from src import log, terms, utils
from src.document import Document, DocumentCS, DocumentEN
from src.index import InvertedIndex
from src.query import Query

SEPS = terms.WHSP_SEPS + terms.PUNCT_SEPS + terms.QUOT + terms.PAR_SEP


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
    stopwords = utils.load_stopwords("stopwords/cs.txt")
    return per_document_base(path, stopwords, DocumentCS)


def per_document_en(path: str) -> tuple[InvertedIndex, int]:
    stopwords = utils.load_stopwords("stopwords/en.txt")
    return per_document_base(path, stopwords, DocumentEN)


def experiment(
    lan: str,
    docs_paths_iter: Iterator[str],
    queries_path: str,
    output_file: str,
    run_id: str,
) -> None:
    per_document = per_document_cs if lan == "cs" else per_document_en
    index = InvertedIndex()

    log.timed("Indexing started")

    doc_count = 0
    with Pool() as pool:
        for docs_index, inner_doc_count in pool.imap(
            per_document, docs_paths_iter, chunksize=20
        ):
            print(f"\rRecieved index {doc_count + 1}", end="")
            index.update_with(docs_index)
            doc_count += inner_doc_count

    print()

    log.timed("Indexing complete")

    stopwords = utils.load_stopwords(f"stopwords/{lan}.txt")
    tfidf_weight = functools.partial(terms.tf_idf_weight, doc_count)
    with open(output_file, mode="w", encoding="utf-8") as output:
        for i, query in enumerate(utils.get_query_iter(queries_path, Query)):
            query_terms = terms.extract(query.title, SEPS, stopwords)
            similars = index.get_most_similar(query_terms, tfidf_weight)
            utils.write_qrels(output, similars, query.id, run_id)
            print(f"\rGot similarities for query {i + 1}", end="")

    print()
    log.timed("Done")
