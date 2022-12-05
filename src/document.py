import bs4


class Document:
    def __init__(self, tag: bs4.element.Tag) -> None:
        """
        Initializes `Document` instance.
        """
        self._tag = tag

    @property
    def id(self) -> str:
        """
        Returns unique document number.
        """
        return str(self._tag.DOCNO.string)

    @property
    def str_all(self) -> str:
        """
        Returns all string inside SGML tags.
        """
        string = ""
        for descendant in self._tag.descendants:
            if isinstance(descendant, bs4.NavigableString):
                string += str(descendant)

        return string


class DocumentCS(Document):
    @property
    def str_all(self) -> str:
        string = ""
        for descendant in self._tag.descendants:
            if isinstance(
                descendant, bs4.NavigableString
            ) and descendant.parent.name not in ["DOCNO", "DOCID"]:
                string += str(descendant)

        return string


class DocumentEN(Document):
    def __init__(self, tag: bs4.element.Tag) -> None:
        super().__init__(tag)
        self._tag_blacklist = set(
            [
                "DOCNO",
                "DOCID",
                "SN",
                "PD",
                "PN",
                "PG",
                "PP",
                "WD",
                "SM",
                "SL",
                "CB",
                "IN",
                "FN",
            ]
        )

    @property
    def str_all(self) -> str:
        string = ""
        for descendant in self._tag.descendants:
            if (
                isinstance(descendant, bs4.NavigableString)
                and descendant.parent.name not in self._tag_blacklist
            ):
                string += str(descendant)

        return string
