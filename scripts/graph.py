import argparse

import matplotlib.pyplot as plt
from common import RunEvaluation

parser = argparse.ArgumentParser()

parser.add_argument(
    "-i",
    "--input",
    type=str,
    action="extend",
    nargs="+",
    help="Input evaluation file.",
    required=True,
)
parser.add_argument(
    "-o", "--output", type=str, help="Output .tex table file.", required=True
)

PRECISION_XS = [5, 10, 15, 20, 30, 100, 200, 500, 1000]
RECALL_XS = [0.1 * i for i in range(11)]


def main(args: argparse.Namespace) -> None:
    runs = []
    for input_file in args.input:
        runs.append(RunEvaluation(input_file))

    fig, (p_axis, r_axis) = plt.subplots(1, 2, figsize=(16, 7))

    for run in runs:
        p_axis.plot(PRECISION_XS, run.get_precisions_at(PRECISION_XS), label=run.runid)

    p_axis.legend()
    p_axis.set_xlabel("Number of top relevant documents considered.")
    p_axis.set_ylabel("Precision")
    p_axis.set_title("Precision")

    for run in runs:
        r_axis.plot(RECALL_XS, run.get_recalls_at(RECALL_XS), label=run.runid)

    r_axis.legend()
    r_axis.set_title("11-point interpolated precision-recall average")
    r_axis.set_xlabel("Recall")
    r_axis.set_ylabel("Precision")

    fig.tight_layout()
    fig.savefig(args.output)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
