from dataclasses import dataclass
import random
from pyetr.stateset import SetOfStates, Stage, Supposition, State
from pyetr.atoms.predicate import Predicate
from pyetr.atoms.predicate_atom import PredicateAtom
from pyetr.view import View


class ETRCaseGenerator:
    def __init__(self):
        # Cards are constants (0-ary predicates) referring to cards in a deck
        self.card_predicates = [
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

    def generate_view(
        self,
        max_domain_size: int = 14,
        max_disjuncts: int = 3,
        max_conjuncts: int = 3,
        generate_supposition: bool = False,
        neg_prob: float = 0.2,
    ) -> View:
        """Generate a view with a random stage and supposition.

        Args:
            max_domain_size (int, optional): The maximum number of propositional variables
                to use in the view. Defaults to 14, the number of cards in a deck.
            max_disjuncts (int, optional): The maximum number of states in the stage.
                Defaults to 3.
            max_conjuncts (int, optional): The maximum number of atoms in each state.
                Defaults to 3.
            generate_supposition (bool, optional): Whether to generate a supposition.
                Defaults to False.
            neg_prob (float, optional): The (independent) probability of negating each atom
                in the stage. Defaults to 0.2.

        Returns:
            View: A randomly generated view subject to the specified parameters.

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

        # Select a subset of cards to work with for this generation call
        restricted_cards = self.card_predicates[:max_domain_size]

        domain_size = random.randint(1, len(restricted_cards))
        domain = random.sample(restricted_cards, domain_size)

        max_conjuncts = min([max_conjuncts, domain_size])

        # First, generate the stage
        stage = generate_set_of_states(domain, max_conjuncts, max_disjuncts)

        # Next, generate the supposition if necessary
        supposition = SetOfStates([State()])
        if generate_supposition:
            supposition = generate_set_of_states(domain, max_conjuncts, max_disjuncts)

        return View.with_defaults(stage=stage, supposition=supposition)

    def view_to_natural_language(self, view: View) -> str:
        """Take a View and convert it into a natural language string.

        Args:
            view (View): The view to convert. This method assumes the View is generated
                by this class, meaning it uses sentential reasoning to talk about cards
                present in a deck. Arbitrary Views passed will likely have errors.

        Returns:
            str: A string describing the View in natural language.
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
            stage_str = "if " + supposition_str + ", then " + stage_str

        return stage_str


if __name__ == "__main__":
    generator = ETRCaseGenerator()
    view = generator.generate_view(generate_supposition=True)
    print(generator.view_to_natural_language(view))
    print()
