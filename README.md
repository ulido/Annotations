# `annotations` package

This package makes it easy to handle and filter lists of items with annotations and modifiers of the kind:

| Name | Annotation |
| ---- | ---------- |
| apple | "fruit[medium],red" |
| orange | "fruit[medium],orange" |
| carrot | "vegetable[long],orange" |
| cherry | "fruit[small],red[dark]" |

## Installation

Install using pip:
```bash
pip install git+https://github.com/ulido/annotations
```

## Simple usage

For illustration purposes, we'll work off an example of a simple list of protein IDs and their intracellular localisations of the form `localisation1[modifier1,modifier2],localisation2[modifier3]`. However, the same procedure applies very broadly for other types of annotations as well, outside of cell biology.

Here is the list of gene IDs and localisations (a protein can have more than one annotation if it has been detected in more than one organelle for example):
```python
raw_localisation_strings = {
    "protein1": "cytoplasm[points]",
    "protein2": "nucleoplasm,cytoplasm[weak]",
    "protein3": "lysosome,endocytic",
    "protein4": "nucleolus",
    "protein5": "cytoplasm,mitochondrion",
    "protein6": "Golgi apparatus",
    "protein7": "nucleoplasm",
    "protein8": "lysosome",
}
```

### Creating collections of annotations
To turn this into versatile [`AnnotationCollection`][annotations.AnnotationCollection] objects, we simply do
```python
from annotations import AnnotationCollection

protein_annotations = {
    protein: AnnotationCollection(annotation_string)
    for protein, annotation_string in raw_annotation_strings.items()
}
```

### Matching annotations
We'll use simple python constructs to manipulate and match these annotations. For example, to find all proteins that localise to the cytoplasm, we use the [`AnnotationCollection.match`][annotations.AnnotationCollection.match] method
```python
print([
    protein
    for protein, localisation in protein_annotations.items()
    if localisation.match("cytoplasm")
])
```
This outputs the following:
```
["protein1", "protein2", "protein5"]
```

### Excluding modifiers
When matching terms, entries can be excluded based on modifiers:
```python
print([
    protein
    for protein, localisation in protein_annotations.items()
    if localisation.match("cytoplasm", exclude_modifiers={"weak"})
])
```
which gives us
```
["protein1", "protein5"]
```

### Requiring modifiers
Conversely, modifiers can also be required:
```python
print([
    protein
    for protein, localisation in protein_annotations.items()
    if localisation.match("cytoplasm", require_modifiers={"points"})
])
```
which gives us
```
["protein1"]
```

### Filtering annotations based on modifiers
We can also use the [`filter_by_modifiers`][annotations.AnnotationCollection.filter_by_modifiers] method to create new [`AnnotationCollection`][annotations.AnnotationCollection]s for proteins:
```python
non_weak_protein_annotations = {
    protein: localisation.filter_by_modifiers(
        exclude_modifiers={"weak"},
    )
    for protein, localisation in protein_annotations.items()
}
```
This leaves everything in place, except it removes the `cytoplasm[weak]` annotation from `protein2`. The same rules regarding required and excluded modifiers from above apply.

## Using annotation ontologies

Annotations often come organised into formalised ontologies, i.e. an annotation hierarchy. An example of this in the above localisations is that both the `nucleolus` and the `nucleoplasm` annotations are considered part of the cell `nucleus`. A common task is then to find all proteins that localise to the nucleus. This is made vastly easier by defining the following ontology:
```python
raw_ontology = [
    [
        {
            "name": "cytoplasm",
            "children": [
                {
                    "name": "endocytic",
                    "children": [
                        {
                            "name": "lysosome",
                            "children": "",
                        },
                    ],
                },
                {
                    "name": "Golgi apparatus",
                    "children": [
                        {
                            "name": "lysosome",
                            "children": "",
                        },
                    ],
                },
            ],
        },
        {
            "name": "mitochondrion",
            "children": [],
        },
        {
            "name": "nucleus",
            "children": [
                {
                    "name": "nucleoplasm",
                    "children": [],
                },
                {
                    "name": "nucleolus",
                    "children": [],
                },
            ]
        }
    ],
]
```

### Creating the ontology
We can turn this into an ontology object by using the [`Ontology`][annotations.Ontology] class and filling it with [`OntologyEntry`][annotations.OntologyEntry] objects:
```python
from annotations import Ontology, OntologyEntry

ontology = Ontology()
def recurse_raw_ontology(entry):
    ontology_entry = OntologyEntry(name=entry["name"])
    ontology.entries[ontology_entry.name] = ontology_entry
    for child in entry["children"]:
        child = recurse_raw_ontology(child)
        child.set_parent(ontology_entry)
        ontology_entry.add_child(child)
    return ontology_entry
for root_entry in raw_ontology:
    ontology.root_entries.append(recurse_raw_ontology(root_entry))
```

### Creating ontology annotations
We then use the ontology to create ontology-connected [`OntologyAnnotationCollection`][annotations.OntologyAnnotationCollection] objects for our proteins:
```python
from annotations import OntologyAnnotationCollection

protein_ontology_annotations = {
    protein: OntologyAnnotationCollection(annotation_string, ontology)
    for protein, annotation_string in raw_annotation_strings.items()
}
```

### Matching based on ontology
As above, we filter our proteins based on a term, this time we use `nucleus`. Note that this term does not occur in the localisation annotations of any of our proteins, but it is the parent of the `nucleoplasm` and `nucleolus` localisations in the ontology.
```python
print([
    protein
    for protein, localisation in protein_ontology_annotations.items()
    if localisation.match("nucleus")
])
```
This outputs:
```
["protein2", "protein4", "protein7"]
```

Again, as with regular annotations, the matching can be adjusted with `require_modifiers` and `exclude_modifiers`.