from concurrent import futures
from multiprocessing import Manager, Queue
from multiprocessing.pool import Pool
from queue import Empty as QueueEmpty
from typing import Iterator

from src import log, terms, utils
from src.document import Document
from src.index import InvertedIndex
from src.query import Query

SEPS = terms.WHSP_SEPS + terms.PUNCT_SEPS


def per_document(path: str) -> InvertedIndex:
    index = InvertedIndex()
    for doc in utils.get_document_iter(path, Document):
        doc_terms = terms.extract(doc.str_all, SEPS)
        for term_str, count in doc_terms.items():
            index.add_posting(term_str, str(doc.id), count)

    return index


def experiment(
    docs_paths_iter: Iterator[str], queries_path: str, output_file: str, run_id: str
) -> None:
    index = InvertedIndex()

    log.timed("Indexing started")
    with Pool() as pool:
        for i, docs_index in enumerate(
            pool.imap(per_document, docs_paths_iter, chunksize=20)
        ):
            print(f"\rRecieved index {i + 1}", end="")
            index.update_with(docs_index)

    print()

    log.timed("Indexing complete")

    with open(output_file, mode="w", encoding="utf-8") as output:
        for i, query in enumerate(utils.get_query_iter(queries_path, Query)):
            query_terms = terms.extract(query.title, SEPS)
            similars = index.get_most_similar(query_terms, terms.natural_weight)
            utils.write_qrels(output, similars, query.id, run_id)
            print(f"\rGot similarities for query {i + 1}", end="")

    print()
    log.timed("Done")


def per_documents(paths: list[str]) -> InvertedIndex:
    index = InvertedIndex()
    for path in paths:
        for doc in utils.get_document_iter(path, Document):
            doc_terms = terms.extract(doc.str_all, SEPS)
            for term_str, count in doc_terms.items():
                index.add_posting(term_str, str(doc.id), count)

    return index


def experiment_with_threads(
    docs_paths_iter: Iterator[str], queries_path: str, output_file: str, run_id: str
) -> None:
    index = InvertedIndex()

    log.timed("Indexing started")

    with futures.ThreadPoolExecutor() as executer:
        future_indexes = [
            executer.submit(per_documents, paths)
            for paths in utils.batch(docs_paths_iter, 20)
        ]
        for i, future_index in enumerate(futures.as_completed(future_indexes)):
            print(f"\rRecieved index {(i + 1) * 20}", end="")
            docs_index = future_index.result()
            index.update_with(docs_index)

    print()

    log.timed("Indexing complete")

    with open(output_file, mode="w", encoding="utf-8") as output:
        for i, query in enumerate(utils.get_query_iter(queries_path, Query)):
            query_terms = terms.extract(query.title, SEPS)
            similars = index.get_most_similar(query_terms, terms.natural_weight)
            utils.write_qrels(output, similars, query.id, run_id)
            print(f"\rGot similarities for query {i + 1}", end="")

    print()
    log.timed("Done")


def per_documents_with_queue(paths: list[str], queue: Queue) -> None:
    index = InvertedIndex()
    for path in paths:
        for doc in utils.get_document_iter(path, Document):
            doc_terms = terms.extract(doc.str_all, SEPS)
            for term_str, count in doc_terms.items():
                index.add_posting(term_str, str(doc.id), count)

    queue.put(index, True)
    print("Inverted index put on queue")


def experiment_with_syncmanager(
    docs_paths_iter: Iterator[str], queries_path: str, output_file: str, run_id: str
) -> None:
    index = InvertedIndex()
    manager = Manager()
    queue = manager.Queue()

    log.timed("Indexing started")

    with Pool() as pool:
        futures = []
        for doc_paths in utils.batch(docs_paths_iter, 20):
            futures.append(
                pool.apply_async(per_documents_with_queue, (doc_paths, queue))
            )

        i = 0
        while len(futures) > 0:
            try:
                while True:
                    print("Trying to get from queue")
                    doc_index = queue.get(True, 1)
                    if doc_index is None:
                        print("No index, retrying")
                        continue
                    print(f"\rRecieved index {i + 1}", end="")
                    i += 1
                    index.update_with(doc_index)
            except QueueEmpty:
                print("Queue empty")
            finally:
                futures = [fut for fut in futures if not fut.ready()]

    print()

    log.timed("Indexing complete")

    with open(output_file, mode="w", encoding="utf-8") as output:
        for i, query in enumerate(utils.get_query_iter(queries_path, Query)):
            query_terms = terms.extract(query.title, SEPS)
            similars = index.get_most_similar(query_terms, terms.natural_weight)
            utils.write_qrels(output, similars, query.id, run_id)
            print(f"\rGot similarities for query {i + 1}", end="")

    print()
    log.timed("Done")
