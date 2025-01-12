from collections import deque
from dataclasses import dataclass, field
from etr_case_generator.generator2.reified_problem import PartialProblem, ReifiedView
from etr_case_generator.mutations import get_view_mutations
from etr_case_generator.ontology import Ontology
from pyetr import View
from pyetr.inference import default_inference_procedure
from typing import Optional, Generator, Deque, Tuple, Set

from etr_case_generator.view_to_natural_language import view_to_natural_language

@dataclass
class ETRGenerator:
    """Maintains the state of the ETR problem generator between calls."""
    problem_queue: Deque[PartialProblem] = field(default_factory=deque)
    min_queue_size: int = 5  # Minimum number of problems to maintain in queue
    max_queue_size: int = 10  # Maximum size of the queue
    _generator: Optional[Generator[PartialProblem, None, None]] = None
    max_mutations: int = 50  # Maximum number of mutations before considering the line exhausted

    def initialize_generator(self) -> None:
        """Initialize the problem generator."""
        self._generator = self._generate_problems()

    def create_starting_problem(self) -> PartialProblem:
        """
        Create an initial seed problem.

        Returns:
            PartialProblem: for now, just the initial disjunction fallacy example
        """
        return PartialProblem(
            premises=[
                ReifiedView(
                    logical_form_smt=None,
                    logical_form_smt_fnode=None,
                    logical_form_etr_view=View.from_str("{ A(a()) B(a()), C(b()) D(b()) }"),
                    english_form=None,  # TODO
                ),
                ReifiedView(
                    logical_form_smt=None,
                    logical_form_smt_fnode=None,
                    logical_form_etr_view=View.from_str("{ A(a()) }"),
                    english_form=None,  # TODO
                ),
            ],  # TODO
            possible_conclusions_from_logical=None,
            possible_conclusions_from_etr=None,  # TODO
            etr_what_follows=ReifiedView(
                logical_form_smt=None,
                logical_form_smt_fnode=None,
                logical_form_etr_view=View.from_str("{ B(a()) }"),
                english_form=None,  # TODO
            ),
        )

    def get_mutated_premises(self, problem: PartialProblem) -> Set[Tuple[View, ...]]:
        """
        Get all possible mutations of the premises of a problem.
        
        Returns:
            Set[List[View]]: A set of all possible mutated premises
        """
        mutations = set()
        assert problem.premises is not None
        for i, view in enumerate(problem.premises):
            assert view.logical_form_etr_view is not None
            for mut in get_view_mutations(view.logical_form_etr_view):
                mutations.add(
                    tuple([p.logical_form_etr_view for p in problem.premises[:i]]) +
                    (mut,) +
                    tuple([p.logical_form_etr_view for p in problem.premises[i+1:]])
                )
        mutations.add(
            tuple([p.logical_form_etr_view for p in problem.premises]) +
            (View.from_str("{A(a())}"),)
        )
        return mutations

    def _generate_problems(self) -> Generator[PartialProblem, None, None]:
        """Internal generator function that creates new problems."""
        # First, try to create a starting problem
        seed_problem = self.create_starting_problem()

        # Add the seed problem to the queue
        yield seed_problem

        mutation_count = 0
        while mutation_count < self.max_mutations:
            # Get the most recent problem from the queue to mutate
            if not self.problem_queue:
                # If queue is empty, we've exhausted this line of problems
                return

            base_problem = self.problem_queue[-1]  # Look at last problem without removing it

            possible_mutations = self.get_mutated_premises(base_problem)
            for mutated_premises in possible_mutations:
                etr_what_follows = default_inference_procedure(mutated_premises)
                premises = []
                for p in mutated_premises:
                    premises.append(
                        ReifiedView(
                            logical_form_etr_view=p,
                            # Generator is not responsible for generating English forms,
                            # since it's agnostic to the ontology
                            english_form=None,
                        )
                    )
                new_problem = PartialProblem(
                    premises=premises,
                    possible_conclusions_from_logical=None,
                    possible_conclusions_from_etr=None,
                    etr_what_follows=ReifiedView(
                        logical_form_etr_view=etr_what_follows,
                        # Generator is not responsible for generating English forms,
                        # since it's agnostic to the ontology
                        english_form=None,
                    )
                )
                yield new_problem

            mutation_count += 1

    def ensure_queue_filled(self) -> None:
        """Ensure the queue has at least min_queue_size problems."""
        if self._generator is None:
            self.initialize_generator()

        while len(self.problem_queue) < self.min_queue_size:
            assert self._generator is not None
            new_problem = next(self._generator)
            if len(self.problem_queue) < self.max_queue_size:
                self.problem_queue.append(new_problem)

    def get_next_problem(self) -> PartialProblem:
        """Get the next problem from the queue, generating more if needed."""
        self.ensure_queue_filled()
        return self.problem_queue.popleft()

# Global state instance
_etr_generator = ETRGenerator()

def random_etr_problem() -> PartialProblem:
    """
    Generate a random ETR problem, maintaining a queue of pre-generated problems.
    
    Args:
        ontology: The ontology to use for problem generation
        
    Returns:
        A new PartialProblem instance
        
    Raises:
        RuntimeError: If unable to generate viable problems after multiple attempts
    """
    return _etr_generator.get_next_problem()

def reset_generator_state():
    """Reset the generator state to initial conditions."""
    global _etr_generator
    _etr_generator = ETRGenerator()

def set_queue_sizes(min_size: int, max_size: int):
    """Configure the queue size parameters."""
    if min_size > max_size:
        raise ValueError("min_size must be less than or equal to max_size")
    _etr_generator.min_queue_size = min_size
    _etr_generator.max_queue_size = max_size

def set_max_mutations(max_mutations: int):
    """Set the maximum number of mutations before considering a line exhausted."""
    if max_mutations <= 0:
        raise ValueError("max_mutations must be positive")
    _etr_generator.max_mutations = max_mutations

def get_queue_size() -> int:
    """Get the current size of the problem queue."""
    return len(_etr_generator.problem_queue)
