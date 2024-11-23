import itertools
import random

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from pyetr import ArbitraryObject, DependencyRelation, FunctionalTerm, Function
from pyetr.stateset import SetOfStates, Stage, Supposition, State
from pyetr.atoms.abstract import Atom
from pyetr.atoms.predicate import Predicate
from pyetr.atoms.predicate_atom import PredicateAtom
from pyetr.atoms.terms.term import Term
from pyetr.inference import default_inference_procedure
from pyetr.view import View
from typing import cast, Generator, Optional

from etr_case_generator.ontology import Ontology


from dataclasses import field
from dataclasses_json import config, dataclass_json


@dataclass_json
@dataclass
class ReasoningProblem:
    premises: list[tuple[str, str]]

    # The actual question
    full_prose: str  # The premises and the question_conclusion
    question_conclusion: tuple[
        str, str
    ]  # Note: this is not necessarily the etr_conclusion

    # The ETR conclusion, which is not necessarily what's being asked about
    etr_conclusion: tuple[str, str]
    etr_conclusion_is_categorical: bool

    # Structured data which makes of the strings. Exclude them because Views aren't serializable.
    premise_views: list[View] = field(metadata=config(exclude=lambda x: True))
    etr_conclusion_view: View = field(metadata=config(exclude=lambda x: True))
    question_conclusion_view: View = field(metadata=config(exclude=lambda x: True))

    # Is the question conclusion ETR? Is it logically correct?
    question_conclusion_is_etr_conclusion: Optional[bool] = (
        None  # The conclusion has one state, no disjunction
    )
    classically_valid_conclusion: Optional[bool] = None

    # More information about the problem
    vocab_size: Optional[int] = None
    max_disjuncts: Optional[int] = None
    num_variables: Optional[int] = None
    num_disjuncts: Optional[int] = None
    num_premises: Optional[int] = None


class ETRCaseGenerator:
    def __init__(self, ontology: Ontology):
        self.ontology = ontology
        self._num_constants = len(self.ontology.objects)
        self._constants = self.ontology.objects

        # For now, predicates only ever have arity 1
        self._num_predicates = len(self.ontology.predicates)
        self._predicates = self.ontology.predicates

    @property
    def num_constants(self):
        return self._num_constants

    @num_constants.setter
    def num_constants(self, value):
        max_constants = len(self.ontology.objects)
        if value > max_constants:
            raise ValueError(
                f"Ontology {self.ontology.name} is only set up to handle at most "
                f"{max_constants} distinct constant values."
            )
        self._num_constants = value
        # Reset constants to be only the first `value` constants
        self._constants = self.ontology.objects[:value]

    @property
    def num_predicates(self):
        return self._num_predicates

    @num_predicates.setter
    def num_predicates(self, value):
        max_constants = len(self.ontology.objects)
        if value > max_constants:
            raise ValueError(
                f"Ontology {self.ontology.name} is only set up to handle at most "
                f"{max_constants} distinct constant values."
            )
        self._num_predicates = value
        # Reset constants to be only the first `value` constants
        self._predicates = self.ontology.predicates[:value]

    def generate_view(
        self,
        max_disjuncts: int = 3,
        max_conjuncts: int = 3,
        generate_supposition: bool = False,
        neg_prob: float = 0.2,
        quantifier: Optional[str] = None,
    ) -> View:
        """Generate a view with a random stage and supposition.

        Args:
            max_disjuncts (int, optional): The maximum number of states in the stage.
                Defaults to 3.
            max_conjuncts (int, optional): The maximum number of atoms in each state.
                Defaults to 3.
            generate_supposition (bool, optional): Whether to generate a supposition.
                Defaults to False.
            neg_prob (float, optional): The (independent) probability of negating each
                atom in the stage. Defaults to 0.2.
            quantifier: Which quantifier to use. Must be one of "universal",
                "existential", or None, otherwise we throw an error.

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

        # Predicates are what ultimately constitute atoms, so cap our domain size at the
        # total number of predicates. Pick a random number to consider for this view.
        domain_size = random.randint(1, self.num_predicates)

        predicates = random.sample(self._predicates, domain_size)
        terms: list[FunctionalTerm | ArbitraryObject] = [
            FunctionalTerm(
                f=Function(name=c, arity=0),
                t=(),
            )
            for c in self._constants
        ]

        # If we'll be adding a quantifier, add an arbitrary object to the terms
        if quantifier:
            terms.append(ArbitraryObject(name="x"))

        atoms = [
            PredicateAtom(
                predicate=p,
                terms=(random.sample(terms, k=1)[0],),
            )
            # TODO: this should be a double for including all possible terms, too
            for p in predicates
        ]

        max_conjuncts = min([max_conjuncts, domain_size])

        # First, generate the stage
        stage = generate_set_of_states(atoms, max_conjuncts, max_disjuncts)

        # Next, generate the supposition if necessary
        supposition = SetOfStates([State()])
        if generate_supposition:
            supposition = generate_set_of_states(atoms, max_conjuncts, max_disjuncts)

        # Finally, add the quantifier if requested
        dep_rel = DependencyRelation(set(), set(), set())
        if ArbitraryObject(name="x") in [
            term
            for atom in stage.atoms | supposition.atoms
            for term in cast(PredicateAtom, atom).terms
        ]:
            if quantifier == "existential":
                dep_rel = DependencyRelation(
                    universals=[],
                    existentials=[ArbitraryObject(name="x")],
                    dependencies=[],
                )
            elif quantifier == "universal":
                dep_rel = DependencyRelation(
                    universals=[ArbitraryObject(name="x")],
                    existentials=[],
                    dependencies=[],
                )
        return View.with_defaults(
            stage=stage, supposition=supposition, dependency_relation=dep_rel
        )

    def view_to_natural_language(
        self, view: View, obj_map: dict[str, str] = {}
    ) -> tuple[str, dict[str, str]]:
        """Take a View and convert it into a natural language string.
        TODO: For now, we don't consider quantification past a single quantifier, and
        we don't think about predicate arities except for 1.

        The natural language string returned has no ending punctuation, and doesn't
        capitalize words except for proper nouns.

        Args:
            view (View): The view to convert.
            obj_map (dict[str, str]): A map from variable names to objects in the
                ontology. Defaults to {}.

        Returns:
            str: A string describing the View in natural language.
            dict[str, str]: The object map transformed as a result of running this new
                conversion. This can be useful if you want to transform multiple views
                according to the same variable interpretations.
        """

        def atom_to_natural_language(atom: PredicateAtom) -> str:
            if atom.predicate.arity != 1:
                raise ValueError("Currently only working with unary predicates.")

            neg = ""
            if not atom.predicate.verifier:
                neg = "not"

            term = atom.terms[
                0
            ]  # We can do this because we only consider unary predicates for now

            # Predicate is of the form "x is P"
            # Get names for predicate and term, and check if they are already mapped
            predicate_name = atom.predicate.name
            term_name = str(term)

            if predicate_name in obj_map.keys():
                predicate_nl = obj_map[predicate_name]
            else:
                # For now, since these predicates are all arity 1, we just take the
                # name property straightaway
                available_predicates = [
                    p
                    for p in self.ontology.predicates
                    if p.name not in obj_map.values()
                ]
                predicate_nl = random.sample(available_predicates, k=1)[0].name
                obj_map[predicate_name] = predicate_nl

            # Check if term is arbitrary or not
            if type(term) == ArbitraryObject:
                # For now, for arbitrary terms we just use their variables (uppercased)
                term_nl = str(term).upper()

            else:
                if term_name in obj_map.keys():
                    term_nl = obj_map[term_name]
                else:
                    available_terms = [
                        t for t in self.ontology.objects if t not in obj_map.values()
                    ]
                    term_nl = random.sample(available_terms, k=1)[0]
                    obj_map[term_name] = term_nl

            return " ".join(" ".join([term_nl, "is", neg, predicate_nl]).split())

        def state_to_natural_language(state: State) -> str:
            ret = ""
            atoms = [
                atom_to_natural_language(cast(PredicateAtom, atom)) for atom in state
            ]

            # Sort atoms so that atoms beginning with "not" come last -- this helps the
            # natural language not read ambiguous, e.g. like "there is not an ace and a
            # ten"
            atoms.sort(key=lambda atom: atom.startswith("not"))

            return ret + " and ".join(atoms)

        # TODO: first, we'll consider very simple quantifiers where there aren't
        # suppositions
        # Universals: "everything is P"
        # Existentials: "something is P"
        universals = view.dependency_relation.universals
        existentials = view.dependency_relation.existentials
        all_quantifiers = universals | existentials
        if len(all_quantifiers) > 1:
            raise ValueError(
                "Currently not considering cases with multiple quantifiers."
            )

        quantifier_str = ""
        q_name = ""
        if len(all_quantifiers) > 0:
            q_name = str(list(all_quantifiers)[0]).upper()
        if len(universals) > 0:
            quantifier_str = f"for all {q_name}, "
        if len(existentials) > 0:
            quantifier_str = f"there is a(n) {q_name} such that "

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

        return quantifier_str + stage_str, obj_map

    def generate_views(
        self,
        n: int,
        max_disjuncts: int = 3,
        max_conjuncts: int = 3,
        supposition_prob: float = 0.2,
        neg_prob: float = 0.2,
    ) -> list[View]:
        """Generate a list of n Views. Uses the generator's properties `num_constants`
        and `num_predicates` to determine the vocabulary domain.

        Args:
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
                max_disjuncts=max_disjuncts,
                max_conjuncts=max_conjuncts,
                generate_supposition=random.random() < supposition_prob,
                neg_prob=neg_prob,
                # The way this works currently, we sample equally among the three.
                # This could presumably be tweaked.
                quantifier=random.sample(["universal", "existential", None], k=1)[0],
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
            question_conclusion_is_etr_conclusion = True

            # The full prose
            full_prose = "Consider the following premises:\n"

            p1_prose, _ = self.view_to_natural_language(p1)
            p1_prose = p1_prose[0].upper() + p1_prose[1:] + "."
            full_prose += f"1. {p1_prose}\n"

            p2_prose, _ = self.view_to_natural_language(p2)
            p2_prose = p2_prose[0].upper() + p2_prose[1:] + "."
            full_prose += f"2. {p2_prose}\n\n"

            try:
                etr_prose, _ = self.view_to_natural_language(question_conclusion_view)
            except ValueError:
                # Conclusion is in a form we cannot represent yet; skip this case
                continue

            full_prose += f"Does it follow that {etr_prose}?\n\n"
            full_prose += "Answer using 'YES' or 'NO' ONLY."

            yield ReasoningProblem(
                full_prose=full_prose,
                premises=[
                    (
                        p1.to_str(),
                        self.view_to_natural_language(p1)[0],
                    ),
                    (
                        p2.to_str(),
                        self.view_to_natural_language(p2)[0],
                    ),
                ],
                premise_views=[p1, p2],
                # Annotations about the question_conclusion
                question_conclusion_is_etr_conclusion=question_conclusion_is_etr_conclusion,
                # classically_valid_conclusion # This will be computed externally
                # Possible conclusions from the premises
                etr_conclusion_view=c_etr,
                question_conclusion_view=question_conclusion_view,
                etr_conclusion=(
                    c_etr.to_str(),
                    self.view_to_natural_language(c_etr)[0],
                ),
                question_conclusion=(
                    question_conclusion_view.to_str(),
                    self.view_to_natural_language(question_conclusion_view)[0],
                ),
                # Metadata about the problem
                vocab_size=vocab_size,
                max_disjuncts=max_disjuncts,
                etr_conclusion_is_categorical=len(c_etr.stage) == 1,
                num_variables=num_variables,
                num_disjuncts=num_disjuncts,
                num_premises=2,  # Currently hardcoded as we only use 2 premises
            )
