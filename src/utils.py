import io
import os
from itertools import zip_longest
from math import log
from multiprocessing.pool import Pool
from typing import Any, Callable, Iterator

import bs4

from src import log, terms
from src.document import Document
from src.query import Query


def get_filename_iter(dir_name: str, file_with_filenames: str) -> Iterator[str]:
    """
    Returns iterator over lines in `file_with_filenames` with `dir_name` prepended.
    """
    with open(file_with_filenames, mode="r", encoding="utf-8") as file:
        for filename in file:
            yield os.path.join(dir_name, filename[:-1])


def get_document_iter(
    doc_path: str, create_doc: Callable[[bs4.element.Tag], Document]
) -> Iterator[Document]:
    with open(doc_path, mode="r", encoding="utf-8") as file_handle:
        soup = bs4.BeautifulSoup(file_handle, "xml")
        for doc_tag in soup.find_all("DOC"):
            yield create_doc(doc_tag)


def get_query_iter(
    queries_path: str, create_query: Callable[[bs4.element.Tag], Query]
) -> Iterator[Query]:
    with open(queries_path, mode="r", encoding="utf-8") as file_handle:
        soup = bs4.BeautifulSoup(file_handle, "xml")
        for query_tag in soup.find_all("top"):
            yield create_query(query_tag)


def write_qrels(
    out: io.TextIOBase,
    similar_docs: list[tuple[float, str]],
    query_id: str,
    run_id: str,
) -> None:
    for rank, (sim, doc_id) in enumerate(similar_docs):
        print("\t".join([query_id, "0", doc_id, str(rank), str(sim), run_id]), file=out)


def batch(iterable: Iterator[Any], batch_size: int) -> Iterator[list[Any]]:
    batch = []
    for element in iterable:
        batch.append(element)
        if len(batch) == batch_size:
            yield batch
            batch = []

    if len(batch) > 0:
        yield batch


def load_stopwords(path: str) -> set[str]:
    with open(path, mode="r", encoding="utf-8") as file:
        return set(file.read().splitlines())


def gen_stopwords_per_document(args: tuple[str, str]) -> dict[str, int]:
    doc_path, separators = args
    term_counts = {}
    doc_count = 0
    for doc in get_document_iter(doc_path, Document):
        doc_terms = terms.extract(doc.str_all, separators)
        doc_count += 1
        for term_str, count in doc_terms.items():
            term_counts[term_str] = term_counts.get(term_str, 0) + count

    return term_counts, doc_count


def generate_stopwords(
    docs_paths_iter: Iterator[str],
    separators: str,
    threshold_freq: float,
    output_file: str,
) -> None:
    log.timed("Parsing documents...")

    term_counts = {}
    doc_count = 0
    with Pool() as pool:
        for docs_term_counts, doc_count in pool.imap(
            gen_stopwords_per_document,
            zip_longest(docs_paths_iter, [], fillvalue=separators),
            chunksize=20,
        ):
            doc_count += doc_count
            print(f"\rParsed doc {doc_count}", end="")
            for term, count in docs_term_counts.items():
                term_counts[term] = term_counts.get(term, 0) + count

    print()

    log.timed("Parsing complete")

    with open(output_file, mode="w", encoding="utf-8") as stopword_file:
        for term, count in term_counts.items():
            if count / doc_count > threshold_freq:
                print(term, file=stopword_file)
