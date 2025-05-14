from __future__ import annotations
from collections.abc import Collection

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


class Ontology:
    root_entries: list[OntologyEntry]
    entries: dict[str, OntologyEntry]

    def __init__(self):
        self.root_entries = []
        self.entries = {}


class OntologyAnnotation(Annotation):
    def __init__(self, annotation_string: str, ontology: Ontology):
        super().__init__(annotation_string)
        self.ontology_entry = ontology.entries[self.term]

    def _match_term(self, term, recursive: bool = True):
        return self.ontology_entry.match_term(term, recursive=recursive)


class OntologyAnnotationCollection(AnnotationCollection):
    def __init__(self, annotations_string: str, ontology: Ontology):
        self.ontology = ontology
        super().__init__(
            annotations_string,
            lambda a_str: OntologyAnnotation(a_str, ontology)
        )

    def __and__(self, other: OntologyAnnotationCollection):
        intersection = self._annotations & other._annotations
        result = OntologyAnnotationCollection("", self.ontology)
        result._annotations = intersection
        return result

    def __or__(self, other: OntologyAnnotationCollection):
        union = self._annotations | other._annotations
        result = OntologyAnnotationCollection("", self.ontology)
        result._annotations = union
        return result

    def new_from_collection(
        self,
        annotations: Collection[OntologyAnnotation],
    ):
        new = OntologyAnnotationCollection("", self.ontology)
        new._annotations = frozenset(annotations)
        return new
