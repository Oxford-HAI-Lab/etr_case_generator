import itertools
import random

from etr_case_generator.ontology import Ontology

# from etr_case_generator.reasoning_problem import ReasoningProblem
from pyetr import ArbitraryObject, DependencyRelation, FunctionalTerm, Function
from pyetr.atoms.predicate_atom import PredicateAtom
from pyetr.inference import default_inference_procedure
from pyetr.stateset import SetOfStates, State
from pyetr.view import View
from typing import cast, Generator, Optional


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

    # def generate_reasoning_problems(
    #     self,
    #     n_views: int,
    #     categorical_conclusions: Optional[bool] = None,
    #     n_trials_timeout: int = 1000,
    #     verbose: bool = False,
    # ) -> Generator[ReasoningProblem, object, object]:
    #     """Generate a list of reasoning problems.

    #     Args:
    #         n_views (int): The number of views to generate for the problem.
    #         categorical_conclusions (Optional[bool], optional): Whether to require the
    #             ETR conclusion to be categorical. If None, enforce no constraints.
    #             Defaults to None.
    #         n_trials_timeout (int, optional): The maximum number of trials to attempt
    #             before timing out. Defaults to 1000.
    #         verbose (bool, optional): Whether to print debugging information. Defaults
    #             to False.

    #     Returns:
    #         list[ReasoningProblem]: A list of reasoning problems.
    #     """

    #     # First generate n_views and their corresponding natural language
    #     # representations
    #     views = self.generate_views(n=n_views)

    #     # For now, consider just problems with 2 premises. Take all n_views^2 possible
    #     # pairs of views as premise pairs.
    #     premises = list(itertools.combinations(views, 2))
    #     if verbose:
    #         print(f"Generated {len(premises)} premise pairs.")

    #     trials = 0
    #     for p1, p2 in premises:
    #         if trials == n_trials_timeout:
    #             print(f"Timed out after {trials} trials.")
    #             return

    #         c_etr = default_inference_procedure((p1, p2))

    #         # Don't consider trivial conclusions interesting
    #         if c_etr.is_verum or c_etr.is_falsum:
    #             trials += 1
    #             continue

    #         # Don't consider cases where conclusions contain falsum
    #         for state in c_etr.stage:
    #             # Falsum
    #             if len(state) == 0:
    #                 trials += 1
    #                 continue

    #         # If required, only continue if the ETR conclusion is categorical
    #         if categorical_conclusions == True and not len(c_etr.stage) == 1:
    #             trials += 1
    #             continue

    #         if categorical_conclusions == False and len(c_etr.stage) == 1:
    #             trials += 1
    #             continue

    #         def get_vocab_size(view: View) -> int:
    #             return len(
    #                 list(
    #                     set(
    #                         [
    #                             a if cast(PredicateAtom, a).predicate.verifier else ~a
    #                             for a in view.atoms
    #                         ]
    #                     )
    #                 )
    #             )

    #         vocab_size = max(
    #             [
    #                 get_vocab_size(p1),
    #                 get_vocab_size(p2),
    #                 get_vocab_size(c_etr),
    #             ]
    #         )
    #         max_disjuncts = max([len(p1.stage), len(p2.stage), len(c_etr.stage)])

    #         # if verbose:
    #         #     print(f"Tried {trials} times to get a valid problem.")

    #         # Reset trials once we're able to yield a complete problem
    #         trials = 0

    #         # Count unique variables across all views
    #         all_atoms = set()
    #         for view in [p1, p2, c_etr]:
    #             all_atoms.update(view.atoms)
    #         num_variables = len(all_atoms)

    #         # Count total number of disjuncts across premises
    #         num_disjuncts = sum(len(view.stage) for view in [p1, p2])

    #         # The conclusion to ask about. For now, always use the ETR conclusion. This
    #         # is a limitation, as we would like to ask about categorical things where
    #         # ETR predicts nothing categorical, as a kind of control problem.
    #         question_conclusion_view = c_etr
    #         question_conclusion_is_etr_conclusion = True

    #         # The full prose
    #         full_prose = "Consider the following premises:\n"

    #         p1_prose, _ = self.view_to_natural_language(p1)
    #         p1_prose = p1_prose[0].upper() + p1_prose[1:] + "."
    #         full_prose += f"1. {p1_prose}\n"

    #         p2_prose, _ = self.view_to_natural_language(p2)
    #         p2_prose = p2_prose[0].upper() + p2_prose[1:] + "."
    #         full_prose += f"2. {p2_prose}\n\n"

    #         try:
    #             etr_prose, _ = self.view_to_natural_language(question_conclusion_view)
    #         except ValueError:
    #             # Conclusion is in a form we cannot represent yet; skip this case
    #             continue

    #         full_prose += f"Does it follow that {etr_prose}?\n\n"
    #         full_prose += "Answer using 'YES' or 'NO' ONLY."

    #         yield ReasoningProblem(
    #             full_prose=full_prose,
    #             premises=[
    #                 (
    #                     p1.to_str(),
    #                     self.view_to_natural_language(p1)[0],
    #                 ),
    #                 (
    #                     p2.to_str(),
    #                     self.view_to_natural_language(p2)[0],
    #                 ),
    #             ],
    #             premise_views=[p1, p2],
    #             # Annotations about the question_conclusion
    #             question_conclusion_is_etr_conclusion=question_conclusion_is_etr_conclusion,
    #             # classically_valid_conclusion # This will be computed externally
    #             # Possible conclusions from the premises
    #             etr_conclusion_view=c_etr,
    #             question_conclusion_view=question_conclusion_view,
    #             etr_conclusion=(
    #                 c_etr.to_str(),
    #                 self.view_to_natural_language(c_etr)[0],
    #             ),
    #             question_conclusion=(
    #                 question_conclusion_view.to_str(),
    #                 self.view_to_natural_language(question_conclusion_view)[0],
    #             ),
    #             # Metadata about the problem
    #             vocab_size=vocab_size,
    #             max_disjuncts=max_disjuncts,
    #             etr_conclusion_is_categorical=len(c_etr.stage) == 1,
    #             num_variables=num_variables,
    #             num_disjuncts=num_disjuncts,
    #             num_premises=2,  # Currently hardcoded as we only use 2 premises
    #         )
