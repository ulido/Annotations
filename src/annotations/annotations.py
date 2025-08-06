"""annotations.py

This is a simple module for processing and storing annotation entries of the
form "annotation term[modifier #1,modifier #2]".
"""
from __future__ import annotations
from collections.abc import Callable, Collection, Set
import re

ANNOT_SPLIT_RE = re.compile(r",\s*(?![^\[]*\])")
ANNOT_STRING_RE = (
    re.compile(r"^(?P<term>[^[\]]+)(?:|\[(?P<modifiers>[^\]]+)\])$")
)


class Annotation:
    """Class that holds a single annotation entry.

    Annotation entries are of the type "term[modifier1,modifier2]".
    """
    term: str
    modifiers: "frozenset[str]"

    def __init__(self, annotation_string: str | None):
        """Create an annotation entry object.

        Parameters:
        ===========
        annotation_string: str
            A annotation string of the form "term[modifier1,modifier2]".
        """
        if annotation_string is None:
            self.term = None
            self.modifiers = frozenset()
        else:
            m = ANNOT_STRING_RE.match(annotation_string)
            if not m:
                raise ValueError(
                    f"Not a valid annotation string: '{annotation_string}'.")

            self.term = str(m['term'])
            if m['modifiers'] is None:
                self.modifiers = frozenset()
            else:
                self.modifiers = frozenset(sorted(m['modifiers'].split(',')))

    def __repr__(self):
        r = f"{self.term}"
        if self.modifiers:
            r += f"[{','.join(sorted(self.modifiers))}]"
        return r

    def __eq__(self, other: str | "Annotation"):
        if isinstance(other, str):
            return self == Annotation(other)
        return (
            (self.term == other.term) and
            (self.modifiers == other.modifiers)
        )

    def _match_term(self, term: str):
        return self.term == term

    def match(
        self,
        term: str,
        require_modifiers: set[str] | None,
        exclude_modifiers: set[str] | None,
        *args, **kwargs,
    ):
        if not self._match_term(term, *args, **kwargs):
            return False

        if require_modifiers is None:
            require_modifiers = self.modifiers
        else:
            require_modifiers = set(require_modifiers)
        if exclude_modifiers is None:
            exclude_modifiers = set()
        else:
            exclude_modifiers = set(exclude_modifiers)

        if (
            (
                require_modifiers and
                self.modifiers.isdisjoint(require_modifiers)
            ) or
            not self.modifiers.isdisjoint(exclude_modifiers)
        ):
            return False
        return True

    def strip_modifiers(self, modifiers: set[str] | None = None):
        """Returns a new `Annotation` with the given modifiers removed (if
        present), or all modifiers removed if `modifiers` is None.

        Args:
            modifiers: Set of modifiers to be removed, or `None` if all should
                be removed.
        """
        new_annotation = self.__class__(None)
        new_annotation.term = self.term
        if modifiers is None:
            new_annotation.modifiers = frozenset()
        else:
            new_annotation.modifiers = self.modifiers - modifiers
        return new_annotation

    def __hash__(self):
        return hash((self.term, self.modifiers))


class AnnotationCollection(Set):
    """Class that holds a set of annotation entries."""
    _annotations: frozenset[Annotation]

    def __init__(
        self,
        annotations_string: str,
        annotation_factory: Callable = lambda a_str: Annotation(a_str),
    ):
        if annotations_string != "":
            self._annotations = frozenset([
                annotation_factory(a_str)
                for a_str in ANNOT_SPLIT_RE.split(annotations_string)
            ])
        else:
            self._annotations = frozenset([])

    def __contains__(self: "set[Annotation]", item: str | Annotation):
        if isinstance(item, str):
            annot = Annotation(item)
        else:
            annot = item
        term_re = re.compile(annot.term)
        for entry in self:
            if (
                term_re.match(entry.term) and
                entry.modifiers.issuperset(annot.modifiers)
            ):
                return True
        return False

    def __repr__(self):
        return ','.join(sorted([repr(entry) for entry in self]))

    def __iter__(self):
        return iter(self._annotations)

    def __len__(self):
        return len(self._annotations)

    def new_from_collection(self, annotations: Collection[Annotation]):
        new = AnnotationCollection("")
        new._annotations = frozenset(annotations)
        return new

    def filter_by_modifiers(
        self,
        require_modifiers: set[str] | None = None,
        exclude_modifiers: set[str] | None = None,
    ):
        matches = [
            annot
            for annot in self
            if annot.match(
                annot.term,
                require_modifiers=require_modifiers,
                exclude_modifiers=exclude_modifiers,
            )
        ]
        return self.new_from_collection(matches)

    def match(
        self,
        term: str,
        require_modifiers: set[str] | None,
        exclude_modifiers: set[str] | None,
        *args, **kwargs,
    ):
        for annot in self:
            if annot.match(
                term,
                require_modifiers,
                exclude_modifiers,
                *args, **kwargs
            ):
                return True
        return False

    def strip_modifiers(self, modifiers: set[str] | None = None):
        """Returns a new `AnnotationCollection` with the given modifiers
        removed from the Annotations. Removes all modifiers if `modifiers` is
        `None`.

        Args:
            modifiers: Set of modifiers to be removed, or `None` if all should
                be removed.
        """
        return self.new_from_collection([
            annotation.strip_modifiers(modifiers)
            for annotation in self
        ])
