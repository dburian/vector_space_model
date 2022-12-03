import bs4


class Query:
    def __init__(self, tag: bs4.element.Tag) -> None:
        self._tag = tag

    @property
    def title(self) -> str:
        return str(self._tag.title.string)

    @property
    def id(self) -> str:
        return str(self._tag.num.string)
