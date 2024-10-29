from dataclasses import dataclass
from dataclasses_json import dataclass_json
import itertools
import random
from pyetr.stateset import SetOfStates, Stage, Supposition, State
from pyetr.atoms.predicate import Predicate
from pyetr.atoms.predicate_atom import PredicateAtom
from pyetr.inference import (
    default_inference_procedure,
    classically_valid_inference_procedure,
)
from pyetr.view import View


@dataclass_json
@dataclass
class ReasoningProblem:
    premises: list[tuple[str, str]]
    etr_conclusion: tuple[str, str]
    valid_conclusion: tuple[str, str]
    conclusions_match: bool
    vocab_size: int
    max_disjuncts: int


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
            max_domain_size (int, optional): The maximum number of propositional
                variables to use in the view. Defaults to 14, the number of cards in a
                deck.
            max_disjuncts (int, optional): The maximum number of states in the stage.
                Defaults to 3.
            max_conjuncts (int, optional): The maximum number of atoms in each state.
                Defaults to 3.
            generate_supposition (bool, optional): Whether to generate a supposition.
                Defaults to False.
            neg_prob (float, optional): The (independent) probability of negating each
                atom in the stage. Defaults to 0.2.

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
            # Bit of a hack: only use "an" for "ace" and "eight", since we know the
            # domain precisely here
            if atom.predicate.name.lower()[0] in ["a", "e"]:
                article = "an"

            return neg + article + " " + atom.predicate.name.lower()

        def state_to_natural_language(state: State) -> str:
            ret = "there is "
            atoms = [atom_to_natural_language(atom) for atom in state]

            # Sort atoms so that atoms beginning with "not" come last -- this helps the
            # natural language not read ambiguous, e.g. like "there is not an ace and a
            # ten"
            atoms.sort(key=lambda atom: atom.startswith("not"))

            return ret + " and ".join(atoms)

        states_for_stage = [state_to_natural_language(state) for state in view.stage]
        stage_str = ", or ".join(states_for_stage)
        if len(states_for_stage) > 1:
            stage_str = "either " + stage_str

        # TODO: this SetOfStates object should have an .empty method
        if not view.supposition.is_verum:
            states_for_supposition = [
                state_to_natural_language(state) for state in view.supposition
            ]
            supposition_str = ", or ".join(states_for_supposition)
            if len(states_for_supposition) > 1:
                supposition_str = "either " + supposition_str
            stage_str = "if " + supposition_str + ", then " + stage_str

        return stage_str

    def generate_views(
        self,
        n: int,
        max_domain_size: int = 14,
        max_disjuncts: int = 3,
        max_conjuncts: int = 3,
        supposition_prob: float = 0.2,
        neg_prob: float = 0.2,
    ) -> list[View]:
        """Generate a list of n Views.

        Args:
            max_domain_size (int, optional): The maximum number of propositional
                variables to use in the view. Defaults to 14, the number of cards in a
                deck.
            max_disjuncts (int, optional): The maximum number of states in the stage.
                Defaults to 3.
            max_conjuncts (int, optional): The maximum number of atoms in each state.
                Defaults to 3.
            generate_supposition (bool, optional): Whether to generate a supposition.
                Defaults to False.
            supposition_prob (float, optional): The probability of generating a
                supposition for each independently generated View. Defaults to 0.2.
            neg_prob (float, optional): The (independent) probability of negating each
                atom in the stage. Defaults to 0.2.

        Returns:
            list[View]: A list of n randomly generated Views subject to the specified
                parameters.
        """
        return [
            self.generate_view(
                max_domain_size=max_domain_size,
                max_disjuncts=max_disjuncts,
                max_conjuncts=max_conjuncts,
                generate_supposition=random.random() < supposition_prob,
                neg_prob=neg_prob,
            )
            for _ in range(n)
        ]

    def generate_reasoning_problems(
        self,
        n_views: int,
        require_categorical_etr: bool = False,
        require_conclusion_match: bool = False,
        n_trials_timeout: int = 1000,
        verbose: bool = False,
    ):
        """Generate a list of reasoning problems.

        Returns:
            list[ReasoningProblem]: A list of reasoning problems.
        """

        # First generate n_views and their corresponding natural language
        # representations
        views = self.generate_views(n=n_views)

        # For now, consider just problems with 2 premises. Take all n_views^2 possible
        # pairs of views as premise pairs.
        premises = list(itertools.combinations(views, 2))
        if verbose:
            print(f"Generated {len(premises)} premise pairs.")

        trials = 0
        for p1, p2 in premises:
            if trials == n_trials_timeout:
                print(f"Timed out after {trials} trials.")
                return

            c_etr = default_inference_procedure((p1, p2))

            # Don't consider trivial conclusions interesting
            if c_etr.is_verum or c_etr.is_falsum:
                trials += 1
                continue

            # Don't consider cases where conclusions contain falsum
            for state in c_etr.stage:
                # Falsum
                if len(state) == 0:
                    trials += 1
                    continue

            # If required, only continue if the ETR conclusion is categorical
            if require_categorical_etr and not len(c_etr.stage) == 1:
                trials += 1
                continue

            c_valid = classically_valid_inference_procedure((p1, p2))

            # Check if we require matching conclusions
            if require_conclusion_match and c_etr != c_valid:
                trials += 1
                continue

            def get_vocab_size(view: View) -> int:
                return len(
                    list(set([a if a.predicate.verifier else ~a for a in view.atoms]))
                )

            vocab_size = max(
                [
                    get_vocab_size(p1),
                    get_vocab_size(p2),
                    get_vocab_size(c_etr),
                    get_vocab_size(c_valid),
                ]
            )
            max_disjuncts = max(
                [len(p1.stage), len(p2.stage), len(c_etr.stage), len(c_valid.stage)]
            )

            if verbose:
                print(f"Tried {trials} times to get valid problem.")

            yield ReasoningProblem(
                premises=[
                    (
                        p1.to_str(),
                        self.view_to_natural_language(p1),
                    ),
                    (
                        p2.to_str(),
                        self.view_to_natural_language(p2),
                    ),
                ],
                etr_conclusion=(c_etr.to_str(), self.view_to_natural_language(c_etr)),
                valid_conclusion=(
                    c_valid.to_str(),
                    self.view_to_natural_language(c_valid),
                ),
                conclusions_match=c_etr == c_valid,
                vocab_size=vocab_size,
                max_disjuncts=max_disjuncts,
            )


if __name__ == "__main__":
    g = ETRCaseGenerator()
    for p in g.generate_reasoning_problems(
        n_views=20,
        require_categorical_etr=True,
        require_conclusion_match=True,
        n_trials_timeout=1000,
        verbose=True,
    ):
        print(p)
        print()
