from typing import Literal, Optional
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

    natural_to_short_name_mapping: Optional[dict[str, str]] = None
    """
    For all object names and predicate names, we want to shorten them using the `natural_name_to_logical_name` function. 
    This is for mapping in the other direction.
    """
    
    def fill_mapping(self):
        self.natural_to_short_name_mapping = {}
        for obj in self.objects:
            self.natural_to_short_name_mapping[natural_name_to_logical_name(obj)] = obj
        for pred in self.predicates:
            self.natural_to_short_name_mapping[natural_name_to_logical_name(pred.name)] = pred.name

        # Assert that the mapping is bijective, i.e. that the size of the set of keys is the same as the size of the set of values.
        assert len(self.natural_to_short_name_mapping.keys()) == len(set(self.natural_to_short_name_mapping.values()))

    def create_smaller_ontology(self, num_predicates, num_objects) -> Ontology:
        ...


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

MAGICAL_CREATURES = Ontology(
    name="Magical Creatures",
    introduction="I'm a magizoologist studying unusual creatures in my sanctuary. I need to understand their behaviors and characteristics through logical reasoning. Here's what I've observed so far:",
    objects=[
        "phoenixling", "shadowdrake", "moonwolf", "crystalspider", "stormgriffin", 
        "dreamweaver", "frostwyrm", "sunlion", "etherealsnake", "timefox"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "fire_breathing", "shadow_walking", "moonlight_glowing", "crystal_forming",
            "storm_controlling", "dream_affecting", "ice_generating", "light_emitting",
            "phase_shifting", "time_bending", "telepathic", "healing_aura",
            "invisibility_capable", "shape_changing"
        ]
    ]
)

ENCHANTED_ARTIFACTS = Ontology(
    name="Enchanted Artifacts",
    introduction="I'm an arcane researcher cataloging mysterious magical items. I need to understand their properties through careful logical analysis. Here's what I've documented so far:",
    objects=[
        "timekeepers_compass", "void_mirror", "dreamcatcher_ring", "starlight_pendant",
        "shadow_cloak", "crystal_orb", "phoenix_feather_quill", "moonstone_bracelet",
        "dragon_scale_shield", "wisdom_crown"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "time_altering", "dimension_bridging", "dream_walking", "starlight_channeling",
            "shadow_concealing", "future_seeing", "truth_revealing", "mind_protecting",
            "magic_nullifying", "wisdom_enhancing"
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
            "time_reversing", "memory_storing", "gravity_defying", "consciousness_affecting",
            "dimension_folding", "quantum_entangling", "void_creating", "omnipresent",
            "paradox_inducing", "infinite_energy_containing"
        ]
    ]
)

CYBER_PROGRAMS = Ontology(
    name="Cyber Programs",
    introduction="I'm a digital archaeologist studying ancient AI programs from a forgotten digital civilization. I need to understand their functions through logical deduction. Here's what I've found:",
    objects=[
        "alpha_mind", "beta_sentinel", "gamma_weaver", "delta_guardian",
        "epsilon_architect", "omega_oracle", "sigma_hunter", "theta_healer",
        "lambda_shifter", "pi_calculator"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "self_evolving", "network_protecting", "data_weaving", "system_guarding",
            "reality_building", "future_predicting", "virus_hunting", "code_healing",
            "form_shifting", "quantum_computing"
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
            "reality_bending", "nightmare_inducing", "dream_walking",
            "memory_weaving", "consciousness_shifting", "time_distorting",
            "emotion_affecting", "thought_reading", "dream_shaping",
            "reality_bridging"
        ]
    ]
)

ALCHEMICAL_SUBSTANCES = Ontology(
    name="Alchemical Substances",
    introduction="I'm an alchemist studying mysterious substances in my laboratory. I need to understand their properties through logical reasoning. Here's what I've discovered:",
    objects=[
        "philosophers_stone", "universal_solvent", "vital_mercury", "prima_materia",
        "celestial_water", "astral_salt", "ethereal_oil", "cosmic_dust",
        "void_essence", "time_crystal"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "transmuting", "dissolving_all", "life_giving", "form_changing",
            "spirit_affecting", "consciousness_expanding", "reality_altering",
            "time_bending", "void_creating", "immortality_granting"
        ]
    ]
)

DIMENSIONAL_ZONES = Ontology(
    name="Dimensional Zones",
    introduction="I'm a dimensional cartographer mapping regions of parallel universes. I need to understand their properties through logical analysis. Here's what I've mapped:",
    objects=[
        "void_nexus", "time_spiral", "dream_realm", "crystal_dimension",
        "shadow_plane", "quantum_zone", "infinity_space", "chaos_domain",
        "mirror_world", "probability_realm"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "time_warping", "reality_bending", "consciousness_altering",
            "matter_crystallizing", "light_absorbing", "probability_shifting",
            "infinity_containing", "chaos_emanating", "reality_reflecting",
            "possibility_branching"
        ]
    ]
)

PSYCHIC_POWERS = Ontology(
    name="Psychic Powers",
    introduction="I'm a researcher studying newly discovered psychic abilities. I need to understand their interactions through logical reasoning. Here's what we know:",
    objects=[
        "telepathy", "precognition", "psychokinesis", "clairvoyance",
        "empathy", "astral_projection", "mind_control", "psychometry",
        "teleportation", "reality_warping"
    ],
    predicates=[
        Predicate(name=p, arity=1) for p in [
            "mind_reading", "future_seeing", "matter_moving", "distance_viewing",
            "emotion_sensing", "soul_traveling", "will_imposing", "object_reading",
            "space_bending", "reality_changing"
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
            "self_evolving", "machine_integrating", "shape_shifting",
            "swarm_forming", "consciousness_developing", "quantum_computing",
            "time_manipulating", "life_creating", "network_forming",
            "energy_converting"
        ]
    ]
)


def natural_name_to_logical_name(name: str, shorten: Literal["none", "short", "first"] = "none") -> str:
    if shorten=="none":
        # View.from_str appears to have an issue with underscores
        name = name.replace(" ", "").replace("-", "").lower()
        # name = name.replace("_", "")  # PyETR appears to require no underscores
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
