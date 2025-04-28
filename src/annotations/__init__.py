"""annotations.py

This is a simple module for processing and storing annotation entries of the
form "annotation term[modifier #1,modifier #2]".
"""
from __future__ import annotations
from collections.abc import Set
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

    def __init__(self, annotation_string):
        """Create an annotation entry object.

        Parameters:
        ===========
        annotation_string: str
            A annotation string of the form "term[modifier1,modifier2]".
        """
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

    def __hash__(self):
        return hash((self.term, self.modifiers))


class AnnotationCollection(Set):
    """Class that holds a set of annotation entries."""
    def __init__(self, annotations_string: str):
        self._annotations = frozenset([
            Annotation(a_str)
            for a_str in ANNOT_SPLIT_RE.split(annotations_string)
        ])

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
