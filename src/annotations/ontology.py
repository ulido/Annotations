from __future__ import annotations
from collections.abc import MutableMapping

from annotations import Annotation, AnnotationCollection


class OntologyEntry:
    name: str
    synonyms: tuple[str]
    comment: str | None
    ident: str | None
    goterm: str | None
    children: set[OntologyEntry]
    parent: OntologyEntry | None
    examples: list[str]

    def __init__(
        self,
        name: str,
        synonyms: tuple[str] | None = None,
        comment: str | None = None,
        ident: str | None = None,
        goterm: str | None = None,
        examples: list[str] | None = None,
    ):
        self.name = name
        if synonyms is not None:
            self.synonyms = tuple(synonyms)
        else:
            self.synonyms = tuple()
        self.comment = comment
        self.ident = ident
        self.goterm = goterm
        self.children = set()
        self.parent = None
        if examples is not None:
            self.examples = examples
        else:
            self.examples = []

    def set_parent(self, parent: OntologyEntry):
        self.parent = parent

    def add_child(self, child: OntologyEntry):
        self.children.add(child)

    def __hash__(self):
        return hash((self.__class__, self.name))

    def match_term(self, term: str, recursive: bool = True) -> bool:
        if self.name == term:
            return True
        if recursive and self.parent is not None:
            return self.parent.match_term(term, recursive=True)
        return False


class OntologyEntryCollection(MutableMapping):
    def __init__(self):
        self._entries: dict[str, OntologyEntry] = {}

    def __setitem__(self, key: str, value: OntologyEntry):
        self._entries[key.lower()] = value

    def __getitem__(self, key: str):
        return self._entries[key.lower()]

    def __delitem__(self, key: str):
        del self._entries[key.lower()]

    def __iter__(self):
        return iter(self._entries)

    def __len__(self):
        return len(self._entries)


class Ontology:
    root_entries: list[OntologyEntry]
    entries: OntologyEntryCollection

    def __init__(self):
        self.root_entries = []
        self.entries = OntologyEntryCollection()


class OntologyAnnotation(Annotation):
    def __init__(self, annotation_string: str, ontology: Ontology):
        super().__init__(annotation_string)
        self.ontology_entry = ontology.entries[self.term]

    def _match_term(self, term, recursive: bool = True):
        return self.ontology_entry.match_term(term, recursive=recursive)


class OntologyAnnotationCollection(AnnotationCollection):
    def __init__(self, annotations_string: str, ontology: Ontology):
        super().__init__(
            annotations_string,
            lambda a_str: OntologyAnnotation(a_str, ontology)
        )
