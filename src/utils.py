import io
import os
from typing import Callable, Iterator

import bs4
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
