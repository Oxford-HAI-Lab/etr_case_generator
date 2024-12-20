from collections import deque
from dataclasses import dataclass, field
from etr_case_generator.generator2.reified_problem import PartialProblem, ReifiedView
from etr_case_generator.ontology import Ontology
from pyetr import View
from typing import Optional, Generator, Deque

@dataclass
class ETRGenerator:
    """Maintains the state of the ETR problem generator between calls."""
    problem_queue: Deque[PartialProblem] = field(default_factory=deque)
    min_queue_size: int = 5  # Minimum number of problems to maintain in queue
    max_queue_size: int = 10  # Maximum size of the queue
    _generator: Optional[Generator] = None
    max_mutations: int = 50  # Maximum number of mutations before considering the line exhausted

    def initialize_generator(self, ontology: Ontology) -> None:
        """Initialize the problem generator."""
        self._generator = self._generate_problems(ontology)

    def create_starting_problem(self, ontology: Ontology) -> Optional[PartialProblem]:
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
                    logical_form_etr=View.from_str("{ A(a()) B(a()), C(b()) D(b()) }"),
                    english_form=None,  # TODO
                ),
                ReifiedView(
                    logical_form_smt=None,
                    logical_form_smt_fnode=None,
                    logical_form_etr=View.from_str("{ A(a()) }"),
                    english_form=None,  # TODO
                ),
            ],  # TODO
            possible_conclusions_from_logical=None,
            possible_conclusions_from_etr=None,  # TODO
            etr_what_follows=ReifiedView(
                logical_form_smt=None,
                logical_form_smt_fnode=None,
                logical_form_etr=View.from_str("{ B(a()) }"),
                english_form=None,  # TODO
            ),
        )

    def mutate_problem(self, problem: PartialProblem) -> Optional[PartialProblem]:
        """
        Create a new problem by mutating an existing one.
        
        Returns:
            PartialProblem if mutation successful, None if no viable mutation possible
        """
        # TODO: Implement actual mutation logic
        return PartialProblem()  # Placeholder

    def _generate_problems(self, ontology: Ontology) -> Generator[PartialProblem, None, None]:
        """Internal generator function that creates new problems."""
        # First, try to create a starting problem
        seed_problem = self.create_starting_problem(ontology)
        if seed_problem is None:
            # If we can't create a viable seed, the generator exhausts immediately
            return

        # Add the seed problem to the queue
        yield seed_problem

        mutation_count = 0
        while mutation_count < self.max_mutations:
            # Get the most recent problem from the queue to mutate
            if not self.problem_queue:
                # If queue is empty, we've exhausted this line of problems
                return
                
            base_problem = self.problem_queue[-1]  # Look at last problem without removing it
            new_problem = self.mutate_problem(base_problem)
            
            if new_problem is None:
                # If mutation fails, this line is exhausted
                return
                
            mutation_count += 1
            yield new_problem

    def ensure_queue_filled(self, ontology: Ontology) -> None:
        """Ensure the queue has at least min_queue_size problems."""
        if self._generator is None:
            self.initialize_generator(ontology)

        while len(self.problem_queue) < self.min_queue_size:
            try:
                new_problem = next(self._generator)
                if len(self.problem_queue) < self.max_queue_size:
                    self.problem_queue.append(new_problem)
            except StopIteration:
                # Current generator is exhausted, try starting fresh
                self.initialize_generator(ontology)
                try:
                    # Try to get at least one problem from the new generator
                    new_problem = next(self._generator)
                    self.problem_queue.clear()  # Clear old problems from exhausted line
                    self.problem_queue.append(new_problem)
                except StopIteration:
                    # If we still can't generate problems, we're in trouble
                    raise RuntimeError("Unable to generate viable problems after multiple attempts")

    def get_next_problem(self, ontology: Ontology) -> PartialProblem:
        """Get the next problem from the queue, generating more if needed."""
        self.ensure_queue_filled(ontology)
        return self.problem_queue.popleft()

# Global state instance
_etr_generator = ETRGenerator()

def random_etr_problem(ontology: Ontology) -> PartialProblem:
    """
    Generate a random ETR problem, maintaining a queue of pre-generated problems.
    
    Args:
        ontology: The ontology to use for problem generation
        
    Returns:
        A new PartialProblem instance
        
    Raises:
        RuntimeError: If unable to generate viable problems after multiple attempts
    """
    return _etr_generator.get_next_problem(ontology)

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
