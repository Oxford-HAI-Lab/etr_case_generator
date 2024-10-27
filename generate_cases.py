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


@dataclass
class Case:
    id: int
    premises: list[str]
    etr_conclusion: str
    classical_conclusion: str


def generate_views(
    n_views: int = 10,
    max_domain_size: int = 14,
    max_disjuncts: int = 3,
    max_conjuncts: int = 3,
    generate_supposition: bool = False,
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
            ret.append(State(disjunct))

        return SetOfStates(ret)

    views = []

    for _ in range(n_views):
        domain_size = random.randint(1, min([max_domain_size, len(cards)]))
        domain = random.sample(cards, domain_size)

        max_conjuncts = min([max_conjuncts, domain_size])

        # First, generate the stage
        stage = generate_set_of_states(domain, max_conjuncts, max_disjuncts)

        supposition = SetOfStates()
        if generate_supposition:
            supposition = generate_set_of_states(domain, max_conjuncts, max_disjuncts)

        views.append(View.with_defaults(stage=stage, supposition=supposition))
    return views


def generate_cases(
    n=3, max_premises=3, max_domain_size=5, neg_prob: float = 0.5, sup_prob: float = 0.2
):
    cases = []

    # Generate
    for _ in range(n):
        # How many premises will there be?
        n_premises: int = random.randint(1, max_premises)
        premises = []

        # How many objects in our domain?
        n_total_objects: int = random.randint(1, max_domain_size)
        domain = [random.choice(cards) for _ in range(n_total_objects)]

        for _ in range(n_premises):
            # Select some number of domain elements to include in this view
            n_elements = random.randint(1, n_total_objects)
            elements = random.sample(domain, n_elements)

            # Initialize empty stage and supposition (for now, will do quantifiers and arbitrary objects later)
            stage, supposition = list(), list()

            for e in elements:
                # With some probability negate the element
                if random.random() < neg_prob:
                    e = ~e

                # Adding to stage or supposition?
                add_to_stage = True
                if random.random() < sup_prob:
                    add_to_stage = False

                # Add the element to the view in some way
                insertions = ["conjoin", "disjoin"]
                insertion = random.choice(insertions)

                if add_to_stage:
                    if insertion == "conjoin":
                        # Pick one of the states in the stage and conjoin e
                        if len(stage) == 0:
                            # Then we're forced to disjoin with e
                            stage.append([e])
                        else:
                            state = random.choice(stage)
                            state.append(e)
                    else:
                        stage.append([e])
                else:
                    if insertion == "conjoin":
                        # Pick one of the states in the supposition and conjoin e
                        if len(supposition) == 0:
                            # Then we're forced to disjoin with e
                            supposition.append([e])
                        else:
                            state = random.choice(supposition)
                            state.append(e)
                    else:
                        supposition.append([e])

            premises.append((stage, supposition))

        print(premises)


if __name__ == "__main__":
    generate_cases()
