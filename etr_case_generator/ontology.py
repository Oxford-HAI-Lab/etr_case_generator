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
    # For identity predicates, P(x) is converted to "x is a P"
    identity_predicates: Optional[list[Predicate]]

    # For action predicates, P(x) is converted to "x Ps"
    action_predicates: Optional[list[Predicate]]

    # For descriptive predicates, P(x) is converted to "x is P"
    descriptive_predicates: Optional[list[Predicate]]


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
    identity_predicates=None,
    action_predicates=None,
    descriptive_predicates=[
        Predicate(name="red", arity=1),
        Predicate(name="black", arity=1),
    ],
)

ANIMALS = Ontology(
    objects=[
        "Alice",
        "Bob",
        "Charlie",
        "David",
        "Eve",
        "Frank",
        "Grace",
        "Hannah",
        "Ivy",
        "Jack",
        "Karen",
        "Liam",
        "Mia",
        "Noah",
        "Olivia",
        "Paul",
        "Quinn",
        "Rachel",
        "Sam",
        "Tom",
    ],
    identity_predicates=[
        Predicate(name="cat", arity=1),
        Predicate(name="dog", arity=1),
        Predicate(name="elephant", arity=1),
        Predicate(name="giraffe", arity=1),
        Predicate(name="lion", arity=1),
        Predicate(name="tiger", arity=1),
        Predicate(name="bear", arity=1),
        Predicate(name="wolf", arity=1),
        Predicate(name="fox", arity=1),
        Predicate(name="rabbit", arity=1),
        Predicate(name="deer", arity=1),
        Predicate(name="zebra", arity=1),
        Predicate(name="cheetah", arity=1),
        Predicate(name="kangaroo", arity=1),
        Predicate(name="panda", arity=1),
        Predicate(name="penguin", arity=1),
        Predicate(name="owl", arity=1),
        Predicate(name="dolphin", arity=1),
        Predicate(name="whale", arity=1),
        Predicate(name="gazelle", arity=1),
    ],
    action_predicates=[
        Predicate(name="prances", arity=1),
        Predicate(name="purrs", arity=1),
        Predicate(name="runs", arity=1),
        Predicate(name="jumps", arity=1),
        Predicate(name="dances", arity=1),
        Predicate(name="sleeps", arity=1),
        Predicate(name="sings", arity=1),
        Predicate(name="barks", arity=1),
        Predicate(name="climbs", arity=1),
        Predicate(name="swims", arity=1),
        Predicate(name="flies", arity=1),
        Predicate(name="digs", arity=1),
        Predicate(name="hops", arity=1),
        Predicate(name="roars", arity=1),
        Predicate(name="chirps", arity=1),
        Predicate(name="crawls", arity=1),
        Predicate(name="gallops", arity=1),
        Predicate(name="slithers", arity=1),
        Predicate(name="waddles", arity=1),
        Predicate(name="growls", arity=1),
    ],
    descriptive_predicates=[
        Predicate(name="fluffy", arity=1),
        Predicate(name="striped", arity=1),
        Predicate(name="spotted", arity=1),
        Predicate(name="sleek", arity=1),
        Predicate(name="shiny", arity=1),
        Predicate(name="furry", arity=1),
        Predicate(name="scaly", arity=1),
        Predicate(name="smooth", arity=1),
        Predicate(name="rough", arity=1),
        Predicate(name="colorful", arity=1),
        Predicate(name="bright", arity=1),
        Predicate(name="dark", arity=1),
        Predicate(name="swift", arity=1),
        Predicate(name="playful", arity=1),
        Predicate(name="agile", arity=1),
        Predicate(name="graceful", arity=1),
        Predicate(name="courageous", arity=1),
        Predicate(name="curious", arity=1),
        Predicate(name="gentle", arity=1),
        Predicate(name="ferocious", arity=1),
    ]
)
