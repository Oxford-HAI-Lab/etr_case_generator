from dataclasses import dataclass
import random
from pyetr.stateset import SetOfStates, Stage, Supposition, State
from pyetr.atoms.predicate import Predicate
from pyetr.atoms.predicate_atom import PredicateAtom
from pyetr.view import View

# Cards are constants (0-ary predicates) referring to cards in a deck
cards = [
    PredicateAtom(predicate=Predicate(name=card, arity=0), terms=())
    for card in [
        "Ace",
        "One",
        "Two",
        "Three",
        "Four",
        "Five",
        "Six",
        "Seven",
        "Eight",
        "Nine",
        "Ten",
        "Jack",
        "Queen",
        "King",
    ]
]


def generate_views(
    n_views: int = 10,
    max_domain_size: int = 14,
    max_disjuncts: int = 3,
    max_conjuncts: int = 3,
    generate_supposition: bool = False,
    neg_prob: float = 0.2,
):
    """_summary_

    Args:
        n_views (int, optional): _description_. Defaults to 10.
        max_domain_size (int, optional): _description_. Defaults to 14, the number of
            cards in a deck.
    """

    def generate_set_of_states(
        domain: list[PredicateAtom],
        max_conjuncts: int,
        max_disjuncts: int,
    ) -> SetOfStates:
        ret = []

        for _ in range(random.randint(1, max_disjuncts)):
            disjunct = random.sample(domain, random.randint(1, max_conjuncts))
            disjunct = [
                ~atom if random.random() < neg_prob else atom for atom in disjunct
            ]
            ret.append(State(disjunct))

        return SetOfStates(ret)

    views = []

    for _ in range(n_views):
        domain_size = random.randint(1, min([max_domain_size, len(cards)]))
        domain = random.sample(cards, domain_size)

        max_conjuncts = min([max_conjuncts, domain_size])

        # First, generate the stage
        stage = generate_set_of_states(domain, max_conjuncts, max_disjuncts)

        # Next, generate the supposition if necessary
        supposition = SetOfStates()
        if generate_supposition:
            supposition = generate_set_of_states(domain, max_conjuncts, max_disjuncts)

        views.append(View.with_defaults(stage=stage, supposition=supposition))
    return views


def view_to_natural_language(view: View) -> str:
    """_summary_

    Args:
        view (View): _description_

    Returns:
        str: _description_
    """

    def atom_to_natural_language(atom: PredicateAtom) -> str:
        neg = ""
        if not atom.predicate.verifier:
            neg = "not "

        article = "a"
        # Bit of a hack: only use "an" for "ace" and "eight", since we know the domain
        # precisely here
        if atom.predicate.name.lower()[0] in ["a", "e"]:
            article = "an"

        return neg + article + " " + atom.predicate.name.lower()

    def state_to_natural_language(state: State) -> str:
        ret = "there is "
        atoms = [atom_to_natural_language(atom) for atom in state]

        # Sort atoms so that atoms beginning with "not" come last -- this helps the
        # natural language not read ambiguous, e.g. like "there is not an ace and a ten"
        atoms.sort(key=lambda atom: atom.startswith("not"))

        return ret + " and ".join(atoms)

    states_for_stage = [state_to_natural_language(state) for state in view.stage]
    stage_str = ", or ".join(states_for_stage)
    if len(states_for_stage) > 1:
        stage_str = "either " + stage_str

    # TODO: this SetOfStates object should have an .empty method
    if len(view.supposition) > 0:
        states_for_supposition = [
            state_to_natural_language(state) for state in view.supposition
        ]
        supposition_str = ", or ".join(states_for_supposition)
        if len(states_for_supposition) > 1:
            supposition_str = "either " + supposition_str
        stage_str = "if " + stage_str + ", then " + supposition_str

    return stage_str


if __name__ == "__main__":
    views = generate_views(generate_supposition=True)
    for view in views:
        print(view_to_natural_language(view))
        print()
