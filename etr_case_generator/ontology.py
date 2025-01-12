from typing import Literal, Optional
from dataclasses import dataclass, field
from pyetr.atoms import Predicate


NameShorteningScheme = Literal["none", "short", "first"]


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

    logical_placeholder_to_short_name: dict[str, str] = field(default_factory=dict)
    """
    When mapping from logical form to natural language, we need to replace the
    placeholders in the logical form with more readable variable names, e.g. "A(b())" ->
    "red(ace())" for "the ace is red."
    """

    short_name_to_full_name: dict[str, str] = field(default_factory=dict)
    """
    For all object names and predicate names, we want to shorten them using the `natural_name_to_logical_name` function. 
    This is for mapping in the other direction.
    """

    preferred_name_shortening_scheme: NameShorteningScheme = "short"

    def fill_mapping(self):
        # self.short_name_to_full_name = {}
        for obj in self.objects:
            s = natural_name_to_logical_name(obj, self.preferred_name_shortening_scheme)
            self.short_name_to_full_name[s] = obj
        for pred in self.predicates:
            s = natural_name_to_logical_name(pred.name, self.preferred_name_shortening_scheme)
            self.short_name_to_full_name[s] = pred.name

        # Assert that the mapping is bijective, i.e. that the size of the set of keys is the same as the size of the set of values.
        assert len(self.short_name_to_full_name.keys()) == len(set(self.short_name_to_full_name.values()))

        # Also add some other ways that it might appear. This makes it not bijective, but hopefully that's okay. The reason for this is that ETR doesn't like underscores in names.
        for obj in self.objects:
            s = natural_name_to_logical_name(obj, self.preferred_name_shortening_scheme)
            self.short_name_to_full_name[s.replace("_", " ")] = obj
        for pred in self.predicates:
            s = natural_name_to_logical_name(pred.name, self.preferred_name_shortening_scheme)
            self.short_name_to_full_name[s.replace("_", " ")] = pred.name

    def create_smaller_ontology(self, num_predicates: int, num_objects: int) -> 'Ontology':
        """Create a new smaller ontology by randomly selecting predicates and objects.
        
        Args:
            num_predicates: Number of predicates to include in new ontology
            num_objects: Number of objects to include in new ontology
            
        Returns:
            New Ontology instance with randomly selected subset of predicates and objects
        """
        import random
        
        # Ensure we don't try to select more items than available
        num_predicates = min(num_predicates, len(self.predicates))
        num_objects = min(num_objects, len(self.objects))
        
        # Randomly select predicates and objects
        selected_predicates = random.sample(self.predicates, num_predicates)
        selected_objects = random.sample(self.objects, num_objects)
        
        # Create new ontology with same name and introduction but smaller sets
        onto = Ontology(
            name=self.name,
            introduction=self.introduction,
            objects=selected_objects,
            predicates=selected_predicates,
            preferred_name_shortening_scheme=self.preferred_name_shortening_scheme,
        )

        onto.fill_mapping()

        return onto


CARDS = Ontology(
    name="Cards",
    introduction="I'm playing a card game against the computer. It's an unusual game with an unusual deck of cards. I have some clues about what's going on, and I need to figure some more things out through logical reasoning. Here's what I know so far:",
    objects=[
        "the ace",
        "the one",
        "the two",
        "the three",
        "the four",
        "the five",
        "the six",
        "the seven",
        "the eight",
        "the nine",
        "the ten",
        "the jack",
        "the queen",
        "the king",
    ],
    predicates=[
        # These must be able to apply to any card, so "face" is not a good predicate.
        Predicate(name="red", arity=1),
        Predicate(name="square", arity=1),
        Predicate(name="marked", arity=1),
        Predicate(name="yellow", arity=1),
        Predicate(name="round", arity=1),
        Predicate(name="castable", arity=1),
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
            "rocky", "gaseous", "ringed", "within a habitable zone",
            "orbited by satellites", "in retrograde orbit", "elliptically-orbiting",
            "visible to the naked eye", "atmospheric",
            "shielded by a magnetic field", "tidally locked"
        ]
    ]
)

MAGICAL_CREATURES = Ontology(
    name="Magical Creatures",
    introduction="I'm a magizoologist studying unusual creatures in my sanctuary. I need to understand their behaviors and characteristics through logical reasoning. Here's what I've observed so far:",
    objects=[
        "phoenixling", "shadowdrake", "moonwolf", "crystalspider", "stormgriffin", 
        "dreamweaver", "frostwyrm", "sunlion", "etherealsnake", "timefox"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "firebreathing", "shadow-walking", "moonlight-glowing", "crystal-forming",
            "storm-controlling", "dream-affecting", "ice-generating", "light-emitting",
            "phase-shifting", "time-bending", "telepathic", "aura-healing",
            "able to turn invisible", "shapeshifting"
        ]
    ]
)

ENCHANTED_ARTIFACTS = Ontology(
    name="Enchanted Artifacts",
    introduction="I'm an arcane researcher cataloging mysterious magical items. I need to understand their properties through careful logical analysis. Here's what I've documented so far:",
    objects=[
        "Timekeeper's Compass", "Void Mirror", "Dreamcatcher Ring", "Starlight Pendant",
        "Shadow Cloak", "Crystal Orb", "Phoenix Feather Quill", "Moonstone Bracelet",
        "Dragon Scale Shield", "Wisdom Crown"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "time-altering", "dimension-bridging", "dreamwalking", "starlight-channeling",
            "shadow-concealing", "future_seeing", "truth-revealing", "mind-protecting",
            "magic-nullifying", "wisdom-enhancing"
        ]
    ]
)

QUANTUM_PARTICLES = Ontology(
    name="Quantum Particles",
    introduction="I'm a quantum physicist studying newly theorized particles in an alternate universe. I need to use logic to understand their properties. Here's what we've discovered so far:",
    objects=[
        "chronoton", "memeton", "gravion", "psychon", "dimensium",
        "quantix", "voidon", "omnion", "paradox", "infinitum"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "time-reversing", "memory-storing", "gravity-defying", "consciousness-affecting",
            "dimension-folding", "quantum-entangling", "void-creating", "omnipresent",
            "paradox-inducing", "infinite-energy-producing"
        ]
    ]
)

CYBER_PROGRAMS = Ontology(
    name="Cyber Programs",
    introduction="I'm a digital archaeologist studying ancient AI programs from a forgotten digital civilization. I need to understand their functions through logical deduction. Here's what I've found:",
    objects=[
        "Alpha Mind", "Beta Sentinel", "Gamma Weaver", "Delta Guardian",
        "Epsilon Architect", "Omega Oracle", "Sigma Hunter", "Theta Healer",
        "Lambda Shifter", "PI Calculator"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "self-evolving", "a network protector", "a data weaver", "a system guarder",
            "reality-building", "a future predictor", "a virus hunter", "a code healer",
            "form-shifting", "quantum computing"
        ]
    ]
)

DREAM_ENTITIES = Ontology(
    name="Dream Entities",
    introduction="I'm a dream researcher studying beings that appear in shared dreams. I need to understand their nature through logical analysis. Here's what we've observed:",
    objects=[
        "morpheus", "sandman", "nightmare", "daydream", "lucidus",
        "dreamweaver", "sleepwalker", "visionkeeper", "mindshaper", "dreamborn"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "reality-bending", "nightmare-inducing", "dreamwalking",
            "memory-weaving", "consciousness-shifting", "time-distorting",
            "emotion-affecting", "thought-reading", "dream-shaping",
            "reality-bridging"
        ]
    ]
)

ALCHEMICAL_SUBSTANCES = Ontology(
    name="Alchemical Substances",
    introduction="I'm an alchemist studying mysterious substances in my laboratory. I need to understand their properties through logical reasoning. Here's what I've discovered:",
    objects=[
        "The Philosopher's Stone", "Universal Solvent", "vital mercury", "Prima Materia",
        "celestial water", "astral salt", "ethereal oil", "cosmic dust",
        "void essence", "Time Crystal"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "transmuting", "corrosive to all materials", "lifegiving", "form-changing",
            "spirit-affecting", "consciousness-expanding", "reality-altering",
            "time-bending", "void-creating", "immortality-granting"
        ]
    ]
)

DIMENSIONAL_ZONES = Ontology(
    name="Dimensional Zones",
    introduction="I'm a dimensional cartographer mapping regions of parallel universes. I need to understand their properties through logical analysis. Here's what I've mapped:",
    objects=[
        "Void Nexus", "Time Spiral", "Dream Realm", "Crystal Dimension",
        "Shadow Plane", "Quantum Zone", "Infinity Space", "Chaos Domain",
        "Mirror World", "Probability Realm"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "time-warping", "reality-bending", "consciousness-altering",
            "matter-crystallizing", "light-absorbing", "probability-shifting",
            "infinity-containing", "chaos-emanating", "reality-reflecting",
            "possibility-branching"
        ]
    ]
)

PSYCHIC_POWERS = Ontology(
    name="Psychic Powers",
    introduction="I'm a researcher studying newly discovered psychic abilities. I need to understand their interactions through logical reasoning. Here's what we know:",
    objects=[
        "telepathy", "precognition", "psychokinesis", "clairvoyance",
        "empathy", "astral projection", "mind control", "psychometry",
        "teleportation", "reality warping"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "mindreading", "future-seeing", "matter-moving", "prescient",
            "emotionally sensitive", "soul-traveling", "imposing", "object-reading",
            "space-bending", "reality-changing"
        ]
    ]
)

BIOTECH_ORGANISMS = Ontology(
    name="Biotech Organisms",
    introduction="I'm a synthetic biology researcher studying advanced bioengineered life forms. I need to understand their capabilities through logical analysis. Here's what we've created:",
    objects=[
        "neurovore", "biomech", "synthoid", "nanohive", "metacell",
        "quantumorg", "chronoplast", "biomatrix", "neuronet", "vitaform"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "self-evolving", "machine-integrating", "shapeshifting",
            "swarm-forming", "consciousness-developing", "quantum-computing",
            "time-manipulating", "life-creating", "network forming",
            "energy-converting"
        ]
    ]
)


def natural_name_to_logical_name(name: str, shorten: NameShorteningScheme = "none") -> str:
    if shorten=="none":
        name = name.replace("_", " ")  # PyETR appears to require no underscores
        name = name.replace("-", " ")
        name = name.replace("'", "")  # Remove apostrophes

        # format name in lowerCamelCase
        name_list = name.split(" ")
        name_list = [name_list[0].lower()] + [word.capitalize() for word in name_list[1:]]
        name = "".join(name_list)
        return name
    elif shorten=="short":
        # Find the first letter of each word
        letters = "".join([word[0] for word in name.split(" ")])
        return letters.lower()
    elif shorten=="first":
        return name[0].lower()


def get_all_ontologies() -> list[Ontology]:
    return [
        CARDS, ELEMENTS, PLANETS,
        MAGICAL_CREATURES, ENCHANTED_ARTIFACTS, QUANTUM_PARTICLES,
        CYBER_PROGRAMS, DREAM_ENTITIES, ALCHEMICAL_SUBSTANCES,
        DIMENSIONAL_ZONES, PSYCHIC_POWERS, BIOTECH_ORGANISMS
    ]
