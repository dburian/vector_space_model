class RunEvaluation:
    def __init__(self, path: str) -> None:
        self._path = path
        self._parse()

    def _parse(self) -> None:
        with open(self._path, mode="r", encoding="utf-8") as file:
            for line in file:
                key, _, value = map(
                    lambda col: col.strip(" "), line.rstrip("\n").split("\t")
                )
                self.__dict__[key] = value

    @property
    def id(self) -> str:
        return self.runid[:-3]

    @property
    def lan(self) -> str:
        return self.runid[-2:]

    def get_precisions_at(self, nums_of_top: list[int]) -> list[float]:
        prec_atts = [f"P_{num}" for num in nums_of_top]
        return [float(getattr(self, att)) for att in prec_atts]

    def get_recalls_at(self, recall_xs: list[float]) -> list[float]:
        recall_atts = [f"iprec_at_recall_{x:.2f}" for x in recall_xs]
        return [float(getattr(self, att)) for att in recall_atts]
