import argparse
import os
import sys
from typing import Callable, Iterator

from src import alpha, utils
from src.document import Document

parser = argparse.ArgumentParser()

parser.add_argument(
    "-q", "--queries", type=str, help="XML topic file in TREC format.", required=True
)
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
    "-r", "--run", type=str, help="Identifier of the run/experiment.", required=True
)
parser.add_argument(
    "-o", "--output", type=str, help="Name of the output file.", required=True
)

Experiment = Callable[[Iterator[str], str], None]
AVAILABLE_RUNS: dict[str, Experiment] = {"alpha": alpha.experiment}


def main(args: argparse.Namespace) -> None:
    if args.run not in AVAILABLE_RUNS:
        print(
            f"Run {args.run} is not available. Choose one of {AVAILABLE_RUNS.keys()}.",
            file=sys.stderr,
        )
        sys.exit(1)

    doc_dir = args.documents[: args.documents.rfind(".")]
    docs_paths_iter = utils.get_filename_iter(doc_dir, args.documents)

    experiment = AVAILABLE_RUNS[args.run]

    experiment(docs_paths_iter, args.queries, args.output, args.run)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
