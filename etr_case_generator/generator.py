import itertools
import random

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from pyetr.stateset import SetOfStates, Stage, Supposition, State
from pyetr.atoms.predicate import Predicate
from pyetr.atoms.predicate_atom import PredicateAtom
from pyetr.inference import default_inference_procedure
from pyetr.view import View
from typing import cast, Generator, Optional

from etr_case_generator.ontology import Ontology


from dataclasses import field
from dataclasses_json import config, dataclass_json

from smt_interface.smt_encoder import check_validity


@dataclass_json
@dataclass
class ReasoningProblem:
    premises: list[tuple[str, str]]

    # The actual question
    full_prose: str  # The premises and the question_conclusion
    question_conclusion: tuple[str, str]  # Note: this is not necessarily the etr_conclusion

    # The ETR conclusion, which is not necessarily what's being asked about
    etr_conclusion: tuple[str, str]
    etr_conclusion_is_categorical: bool

    # Structured data which makes of the strings. Exclude them because Views aren't serializable.
    premise_views: list[View] = field(metadata=config(exclude=lambda x: True))
    etr_conclusion_view: View = field(metadata=config(exclude=lambda x: True))
    question_conclusion_view: View = field(metadata=config(exclude=lambda x: True))

    # Is the question conclusion ETR? Is it logically correct?
    question_conclusion_is_etr_conclusion: Optional[bool] = None  # The conclusion has one state, no disjunction
    classically_valid_conclusion: Optional[bool] = None

    # More information about the problem
    vocab_size: Optional[int] = None
    max_disjuncts: Optional[int] = None
    num_variables: Optional[int] = None
    num_disjuncts: Optional[int] = None
    num_premises: Optional[int] = None


class ETRCaseGenerator:
    def __init__(self, ontology: Ontology):
        self.ontology = Ontology

        # Set up basic objects
        self.objects = [
            PredicateAtom(predicate=Predicate(name=o.capitalize(), arity=0), terms=())
            for o in ontology.objects
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
        restricted_cards = self.objects[:max_domain_size]

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
            atoms = [
                atom_to_natural_language(cast(PredicateAtom, atom)) for atom in state
            ]

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
        categorical_conclusions: Optional[bool] = None,
        n_trials_timeout: int = 1000,
        verbose: bool = False,
    ) -> Generator[ReasoningProblem, object, object]:
        """Generate a list of reasoning problems.

        Args:
            n_views (int): The number of views to generate for the problem.
            categorical_conclusions (Optional[bool], optional): Whether to require the
                ETR conclusion to be categorical. If None, enforce no constraints.
                Defaults to None.
            n_trials_timeout (int, optional): The maximum number of trials to attempt
                before timing out. Defaults to 1000.
            verbose (bool, optional): Whether to print debugging information. Defaults
                to False.

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

        random.shuffle(premises)

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
            if categorical_conclusions == True and not len(c_etr.stage) == 1:
                trials += 1
                continue

            if categorical_conclusions == False and len(c_etr.stage) == 1:
                trials += 1
                continue

            def get_vocab_size(view: View) -> int:
                return len(
                    list(
                        set(
                            [
                                a if cast(PredicateAtom, a).predicate.verifier else ~a
                                for a in view.atoms
                            ]
                        )
                    )
                )

            vocab_size = max(
                [
                    get_vocab_size(p1),
                    get_vocab_size(p2),
                    get_vocab_size(c_etr),
                ]
            )
            max_disjuncts = max([len(p1.stage), len(p2.stage), len(c_etr.stage)])

            # if verbose:
            #     print(f"Tried {trials} times to get a valid problem.")

            # Reset trials once we're able to yield a complete problem
            trials = 0

            # Count unique variables across all views
            all_atoms = set()
            for view in [p1, p2, c_etr]:
                all_atoms.update(view.atoms)
            num_variables = len(all_atoms)

            # Count total number of disjuncts across premises
            num_disjuncts = sum(len(view.stage) for view in [p1, p2])

            # The conclusion to ask about. For now, always use the ETR conclusion. This
            # is a limitation, as we would like to ask about categorical things where
            # ETR predicts nothing categorical, as a kind of control problem.
            question_conclusion_view = c_etr
            # question_conclusion_is_etr_conclusion = random.random() < 1.0  # TODO
            # if not question_conclusion_is_etr_conclusion:
            #     question_conclusion_view = c_etr.negation()
            question_conclusion_is_etr_conclusion = True

            # Check classical validity
            classical_validity = check_validity([p1, p2], [question_conclusion_view])

            # The full prose
            full_prose = "Consider the following premises:\n"

            p1_prose = self.view_to_natural_language(p1)
            p1_prose = p1_prose[0].upper() + p1_prose[1:] + "."
            full_prose += f"1. {p1_prose}\n"

            p2_prose = self.view_to_natural_language(p2)
            p2_prose = p2_prose[0].upper() + p2_prose[1:] + "."
            full_prose += f"2. {p2_prose}\n\n"

            etr_prose = self.view_to_natural_language(question_conclusion_view)

            full_prose += f"Does it follow that {etr_prose}?\n\n"
            full_prose += "Answer using 'YES' or 'NO' ONLY."

            yield ReasoningProblem(
                full_prose=full_prose,
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
                premise_views=[p1, p2],

                # Annotations about the question_conclusion
                question_conclusion_is_etr_conclusion=question_conclusion_is_etr_conclusion,
                classically_valid_conclusion = classical_validity,

                # Possible conclusions from the premises
                etr_conclusion_view=c_etr,
                question_conclusion_view=question_conclusion_view,
                etr_conclusion=(c_etr.to_str(), self.view_to_natural_language(c_etr)),
                question_conclusion=(question_conclusion_view.to_str(), self.view_to_natural_language(question_conclusion_view)),

                # Metadata about the problem
                vocab_size=vocab_size,
                max_disjuncts=max_disjuncts,
                etr_conclusion_is_categorical=len(c_etr.stage) == 1,
                num_variables=num_variables,
                num_disjuncts=num_disjuncts,
                num_premises=2  # Currently hardcoded as we only use 2 premises
            )
