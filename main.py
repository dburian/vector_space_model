import argparse
import sys
from functools import partial
from typing import Callable, Iterator

from src import terms, utils
from src.runs import run_0, run_0_stopwords, run_0_tagblacklist, run_0_tfidf

parser = argparse.ArgumentParser()

parser.add_argument("-q", "--queries", type=str, help="XML topic file in TREC format.")
parser.add_argument(
    "-d",
    "--documents",
    type=str,
    help=(
        "File containing list of documents, where each path is prepended with given"
        " filename without extension as a containing directory."
    ),
    required=True,
)
parser.add_argument(
    "-r", "--run", type=str, default=None, help="Identifier of the run/experiment."
)
parser.add_argument(
    "-o", "--output", type=str, help="Name of the output file.", required=True
)
parser.add_argument(
    "--gen_stopwords",
    type=float,
    default=-1,
    help=(
        "When set to positive number, stopwords will be generated with frequency per"
        " document above the specified number."
    ),
)

Experiment = Callable[[Iterator[str], str, str, str], None]
AVAILABLE_RUNS: dict[str, Experiment] = {
    "run-0_cs": run_0.experiment,
    "run-0_en": run_0.experiment,
    "run-0-tfidf_cs": run_0_tfidf.experiment,
    "run-0-tfidf_en": run_0_tfidf.experiment,
    "run-0-stopwords_cs": partial(run_0_stopwords.experiment, "cs"),
    "run-0-stopwords_en": partial(run_0_stopwords.experiment, "en"),
    "run-0-tagblacklist_cs": partial(run_0_tagblacklist.experiment, "cs"),
    "run-0-tagblacklist_en": partial(run_0_tagblacklist.experiment, "en"),
    "run-1_cs": partial(run_0_stopwords.experiment, "cs"),
    "run-1_en": partial(run_0_stopwords.experiment, "en"),
}


def main(args: argparse.Namespace) -> None:
    doc_dir = args.documents[: args.documents.rfind(".")]
    docs_paths_iter = utils.get_filename_iter(doc_dir, args.documents)

    if args.gen_stopwords > 0:
        utils.generate_stopwords(
            docs_paths_iter,
            terms.WHSP_SEPS + terms.PUNCT_SEPS,
            args.gen_stopwords,
            args.output,
        )
        return

    if args.run is None:
        print("Run must be specified if not generating stopwords.", file=sys.stderr)
        sys.exit(1)

    if args.queries is None:
        print("Topics must be specified if not generating stopwords.", file=sys.stderr)
        sys.exit(1)

    if args.run is None or args.run not in AVAILABLE_RUNS:
        print(
            f"Run {args.run} is not available. Choose one of {AVAILABLE_RUNS.keys()}.",
            file=sys.stderr,
        )
        sys.exit(1)

    experiment = AVAILABLE_RUNS[args.run]
    sys.setrecursionlimit(20000)
    experiment(docs_paths_iter, args.queries, args.output, args.run)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
