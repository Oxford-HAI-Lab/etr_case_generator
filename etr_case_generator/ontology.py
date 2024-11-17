from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class Predicate:
    name: str
    arity: int


@dataclass
class Ontology:
    name: str

    objects: list[str]
    """
    The basic objects in the ontology. In mathematical terms this object is a set, but
    we will use a list for convenience in python (for example, when restricting the
    ontology to a subset of objects, order can help us select the same restricted
    subset across different generations).
    """

    predicates: list[Predicate]
    """
    Predicates, consisting of a name and an arity.
    These should all be phrased as adjectives, e.g. P(x) is converted to "x is P."
    Note that for now, these predicates cannot be exhaustive, meaning for any P and Q,
    it must be possible to have P(x)Q(x).
    """


CARDS = Ontology(
    name="Cards",
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
        Predicate(name="square", arity=1),
    ],
)

ELEMENTS = Ontology(
    name="Materials",
    objects=[
        "elementium",
        "zycron",
        "phantasmite",
        "mystarium",
        "oblivium",
        "luminite",
        "darkonium",
        "velocium",
        "quasarium",
        "chronium",
        "aetherium",
        "voidite",
        "pyroflux",
        "cryon",
        "nebulium",
        "solarium",
        "eclipsium",
        "stellarite",
        "fluxium",
        "gravitron",
        "xylozine",
        "ignisium",
        "aurorium",
        "shadowium",
        "plasmor",
        "terranite",
        "harmonium",
        "zenthium",
        "celestium",
        "radionite",
    ],
    predicates=[
        Predicate(name=p, arity=1)
        for p in [
            "radioactive",
            "luminescent",
            "superconductive",
            "magnetic",
            "corrosive",
            "volatile",
            "plasma-like",
            "gravity-enhancing",
            "dimension-warping",
            "time-dilating",
            "self-repairing",
            "shape-shifting",
            "anti-matter reactive",
            "bio-compatible",
            "crystal-forming",
            "acidic",
            "alkaline",
            "liquid at room temperature",
            "gas under high pressure",
            "solidifies in vacuum",
            "quantum-stable",
            "emotion-reactive",
            "thermal-conductive",
            "electrically insulating",
            "transparent to visible light",
            "dark energy absorbing",
            "neutrino-emitting",
            "anti-gravity generating",
            "sound-absorbing",
        ]
    ],
)
