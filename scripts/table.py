import argparse

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
parser.add_argument("-o", "--output", type=str, help="Output .tex table file.")

COLS = [
    "map",
    # "num_ret",
    "num_rel",
    "num_rel_ret",
    "recip_rank",
    # "iprec_at_recall_0.00",
    # "iprec_at_recall_0.50",
    # "iprec_at_recall_1.00",
    # "P_5",
    # "P_30",
    # "P_200",
]

COLS_RENAME = {
    "map": "MAP",
    "num_ret": r"\#returned",
    "num_rel": r"\#relevant",
    "num_rel_ret": r"\#rel. \& ret.",
    "recip_rank": "MRR",
    "iprec_at_recall_0.00": "IRPA@0.00",
    "iprec_at_recall_0.50": "IRPA@0.50",
    "iprec_at_recall_1.00": "IRPA@1.00",
    "P_5": "P@5",
    "P_30": "P@30",
    "P_200": "P@200",
}
LANS = ["cs", "en"]
LANS_RENAME = {"cs": "Czech", "en": "English"}


def main(args: argparse.Namespace) -> None:
    runs = {}
    for input_file in args.input:
        run = RunEvaluation(input_file)
        runs[run.id] = runs.get(run.id, {})
        runs[run.id][run.lan] = run

    with open(args.output, mode="w", encoding="utf-8") as out:
        col_config = "c " * len(COLS)
        print(r"\begin{tabular}{ l | " + col_config + "| " + col_config + "}", file=out)
        for lan in LANS_RENAME.values():
            print(
                r" & \multicolumn{" + str(len(COLS)) + "}{ | c}{" + lan + "}",
                end="",
                file=out,
            )
        print(r"\\", file=out)
        print(r"\cline{2-" + str(2 * len(COLS) + 1) + "}", file=out)
        print(r"run ID", end="", file=out)
        for _ in LANS:
            for col in COLS:
                col_name = COLS_RENAME[col]
                print(f" & {col_name}", end="", file=out)

        print(r"\\", file=out)
        print(r"\hline", file=out)
        for run_id, runs_by_lan in runs.items():
            print(f"{run_id}", end="", file=out)
            for lan in LANS:
                for col in COLS:
                    value = (
                        getattr(runs_by_lan[lan], col) if lan in runs_by_lan else "-"
                    )
                    print(f" & {value}", end="", file=out)

            print(r"\\", file=out)

        print(r"\end{tabular}", file=out)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
