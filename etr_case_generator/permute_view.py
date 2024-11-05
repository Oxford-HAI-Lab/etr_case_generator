import random
import string

from pyetr.atoms import Atom
from pyetr.atoms.predicate import Predicate
from pyetr.atoms.predicate_atom import PredicateAtom
from pyetr.stateset import State, SetOfStates
from pyetr.atoms.terms.function import Function
from pyetr.atoms.terms.term import FunctionalTerm
from pyetr.view import View


ALL_LETTERS = set(string.ascii_uppercase)


def negate_atom(view: View) -> View:
    # Negates one atom of one state in the view's stage or supposition

    def negate_atom_in_SetOfStates(set_of_states: SetOfStates) -> SetOfStates:
        # Copy supposition to mutable object
        sos: set[State] = set(set_of_states)

        # Pick a random state
        orig_state: State = random.choice(list(sos))
        state: set[Atom] = set(orig_state)

        # Pick a random atom
        orig_atom: Atom = random.choice(list(state))

        # Negate
        atom = ~orig_atom

        # Recreate the SetOfStates
        new_state = State(state - {orig_atom} | {atom})
        new_sos = SetOfStates(sos - {orig_state} | {new_state})

        return new_sos

    new_stage = view.stage
    new_supposition = view.supposition

    # Check if the stage is empty
    if view.stage.is_verum:

        # Then if the supposition is also empty, return the view unchanged
        if view.supposition.is_verum:
            return view

        # Else pick a random atom from the supposition and negate it
        new_supposition = negate_atom_in_SetOfStates(view.supposition)

    # Otherwise check if the supposition is empty
    elif view.supposition.is_verum:

        # Then pick a random atom from the stage and negate it
        new_stage = negate_atom_in_SetOfStates(view.stage)

    # Otherwise pick randomly between view and supposition
    else:
        if random.choice([True, False]):
            new_stage = negate_atom_in_SetOfStates(view.stage)
        else:
            new_supposition = negate_atom_in_SetOfStates(view.supposition)

    return View(
        stage=new_stage,
        supposition=new_supposition,
        dependency_relation=view.dependency_relation,
        issue_structure=view.issue_structure,
        weights=None,
    )


def add_novel_disjunction(view: View, max_predicate_arity: int = 3) -> View:
    # Add a single novel state, containing one atom, to the View's stage
    new_stage = set(view.stage)

    # Use an unreserved letter to create a new predicate
    vocab = set([atom.predicate.name for atom in view.atoms])
    available_vars = ALL_LETTERS - vocab
    new_predicate_name = available_vars.pop()

    # Pick a random arity and populate objects for those places in the new predicate
    arity = random.randint(1, max_predicate_arity)
    objects = [available_vars.pop() for _ in range(arity)]

    terms = [FunctionalTerm(f=Function(name=o, arity=0), t=()) for o in objects]
    new_atom = PredicateAtom(
        predicate=Predicate(new_predicate_name, arity=arity), terms=tuple(terms)
    )
    new_stage.add(State([new_atom]))

    return View(
        stage=SetOfStates(new_stage),
        supposition=view.supposition,
        dependency_relation=view.dependency_relation,
        issue_structure=view.issue_structure,
        weights=None,
    )


def permute_view(View) -> View:
    options = [negate_atom, add_novel_disjunction]

    return random.choice(options)(View)


if __name__ == "__main__":
    v = permute_view(View.from_str("{A()B()}"))
    print(v)
