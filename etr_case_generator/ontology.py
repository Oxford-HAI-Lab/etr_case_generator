from dataclasses import dataclass
from typing import Optional


@dataclass
class Predicate:
    name: str
    arity: int


@dataclass
class Ontology:
    # The basic objects in the ontology. In mathematical terms this object is a set, but
    # we will use a list for convenience in python (for example, when restricting the
    # ontology to a subset of objects, order can help us select the same restricted
    # subset across different generations).
    objects: list[str]

    # Predicates, consisting of a name and an arity.
    # TODO eventually we'll want to set up restricted ranges, or some other way for the
    # ontology to express that certain predicates are only valid for certain objects.
    predicates: Optional[list[Predicate]]


CARDS = Ontology(
    objects=[
        "ace",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "jack",
        "queen",
        "king",
    ],
    predicates=[
        Predicate(name="red", arity=1),
        Predicate(name="black", arity=1),
    ],
)
