from typing import Literal
from dataclasses import dataclass
from pyetr.atoms import Predicate


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
            "gaseous under high pressure",
            "solid in vacuum",
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

PLANETS = Ontology(
    name="Celestial Bodies",
    objects=[
        "mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune",
        "pluto", "ceres", "eris", "makemake", "haumea", "sedna", "planet x", "planet nine", "quaoar", "charon",
    ],
    predicates=[
        Predicate(name=p, arity=1)
        for p in [
            "rocky", "gaseous", "ringed", "habitable_zone",
            "has_moons", "retrograde_orbit", "elliptical_orbit",
            "visible_to_naked_eye", "has_atmosphere",
            "has_magnetic_field", "tidally_locked"
        ]
    ]
)

ANIMALS = Ontology(
    name="Animals",
    objects=[
        "lion", "elephant", "dolphin", "eagle", "penguin", "octopus",
        "kangaroo", "platypus", "chameleon", "bat", "whale", "cobra",
        "butterfly", "scorpion", "owl", "beaver"
    ],
    predicates=[
        Predicate(name=p, arity=1)
        for p in [
            "warm_blooded", "carnivorous", "nocturnal", "venomous",
            "can_fly", "aquatic", "hibernates", "migratory",
            "has_scales", "has_fur", "has_feathers", "egg_laying",
            "social", "territorial", "camouflaged"
        ]
    ]
)

FOODS = Ontology(
    name="Cuisine",
    objects=[
        "sushi", "pizza", "curry", "pasta", "taco", "sushi",
        "burger", "salad", "soup", "steak", "bread", "cake",
        "yogurt", "cheese", "chocolate", "rice"
    ],
    predicates=[
        Predicate(name=p, arity=1)
        for p in [
            "vegetarian", "spicy", "fermented", "raw", "baked",
            "fried", "dairy_based", "gluten_free", "sweet",
            "savory", "high_protein", "contains_nuts",
            "requires_refrigeration", "shelf_stable"
        ]
    ]
)


def natural_name_to_logical_name(name: str, shorten: Literal["none", "short", "first"] = "none") -> str:
    if shorten=="none":
        # View.from_str appears to have an issue with underscores
        return name.replace(" ", "").replace("-", "").lower()
    elif shorten=="short":
        # Find the first letter of each word
        letters = "".join([word[0] for word in name.split(" ")])
        return letters.lower()
    elif shorten=="first":
        return name[0].lower()

def get_all_ontologies() -> list[Ontology]:
    return [CARDS, ELEMENTS, PLANETS, ANIMALS, FOODS]
