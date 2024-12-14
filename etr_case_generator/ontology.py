from typing import Literal
from dataclasses import dataclass
from pyetr.atoms import Predicate


@dataclass
class Ontology:
    name: str
    introduction: str
    """
    Prompting prose for the LLM in which we introduce the logical problem. 
    """

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
    introduction="I'm playing a card game against the computer. It's an unusual game with an unusual deck of cards. I have some clues about what's going on, and I need to figure some more things out through logical reasoning. Here's what I know so far:",
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
    introduction="I'm working in a materials science lab and we've gotten some puzzling results. I need to use logical reasoning to figure out what's going on. Here's what I know so far:",
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
    introduction="I'm an astronomer studying newly discovered celestial bodies. I've made some observations and I need to use logical reasoning to figure out what's going on. Here's what I know so far:",
    objects=[
        "planet X", "planet Y", "planet Z", "asteroid A", "asteroid B", "comet 1", "comet 2", "moon 1", "moon 2", "moon 3"
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


def natural_name_to_logical_name(name: str, shorten: Literal["none", "short", "first"] = "none") -> str:
    if shorten=="none":
        # View.from_str appears to have an issue with underscores
        return name.replace(" ", "").replace("-", "").replace("_", "").lower()
    elif shorten=="short":
        # Find the first letter of each word
        letters = "".join([word[0] for word in name.split(" ")])
        return letters.lower()
    elif shorten=="first":
        return name[0].lower()

def get_all_ontologies() -> list[Ontology]:
    return [CARDS, ELEMENTS, PLANETS, ANIMALS, FOODS]
