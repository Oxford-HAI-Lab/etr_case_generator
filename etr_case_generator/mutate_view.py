import random
import string

from pyetr.atoms import Atom
from pyetr.atoms.predicate import Predicate
from pyetr.atoms.predicate_atom import PredicateAtom
from pyetr.stateset import State, SetOfStates
from pyetr.atoms.terms.function import Function
from pyetr.atoms.terms.term import FunctionalTerm
from pyetr.view import View


ALPHABET = list(set(string.ascii_uppercase))


def negate_atom(view: View) -> View:
    """Negates one atom of one state in the view's stage or supposition."""

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

    # Cannot negate anything in an empty view
    if len(view.atoms) == 0:
        return view

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


def negate_view(view: View) -> View:
    """Negate the view."""
    return view.negation()


def remove_noncommital_states(view: View) -> View:
    """Remove noncommital states from the view. E.g., {p, q, 0} becomes {p, q}."""
    new_stage = set()
    new_sup = set()
    for state in view.stage:
        if len(state) > 0:
            new_stage.add(state)
    for state in view.supposition:
        if len(state) > 0:
            new_sup.add(state)
    return View.with_restriction(
        stage=SetOfStates(new_stage),
        supposition=SetOfStates(new_sup),
        dependency_relation=view.dependency_relation,
        issue_structure=view.issue_structure,
        weights=view.weights,
    )


def factor_atom(view: View, atom: Atom) -> View:
    """Factor a specific atom from the view.

    Args:
        atom (Atom): The atom to factor.
    """
    atom_view = View.with_defaults(stage=SetOfStates({State({atom})}))
    view = view.factor(atom_view)
    return remove_noncommital_states(view)


def factor_random_atom(view: View) -> View:
    """Choose a random atom from the view and factor it out."""
    # Cannot factor from an empty view
    if len(view.atoms) == 0:
        return view

    atom = random.choice(list(view.atoms))
    return factor_atom(view, atom)


def disjoin_random_unary_predicate(view: View) -> View:
    """Add a single novel state, containing one unary predicate atom with random
    predicate and term names, to the View's stage.
    """
    new_stage = set(view.stage)

    predicate_name = random.choice(ALPHABET)
    object_name = random.choice(ALPHABET)

    term = FunctionalTerm(f=Function(name=object_name, arity=0), t=())
    new_atom = PredicateAtom(
        predicate=Predicate(predicate_name, arity=1), terms=(term,)
    )
    new_stage.add(State([new_atom]))

    return View(
        stage=SetOfStates(new_stage),
        supposition=view.supposition,
        dependency_relation=view.dependency_relation,
        issue_structure=view.issue_structure,
        weights=None,
    )


def merge_random_unary_predicate(view: View) -> View:
    """Create a random unary predicate and merge it to either the supposition or
    stage.
    The letters may correspond to existing predicates / objects in the view, or they
    may not.
    """
    predicate_letter, term_letter = random.sample(list(ALPHABET), k=2)

    return view.merge(View.from_str("{" + f"{predicate_letter}({term_letter}())" + "}"))


def universal_quantify(view: View) -> View:
    """Pick a random term occurring in the view and replace it with a universally
    quantified variable."""
    # Cannot work with an empty view
    if len(view.atoms) == 0:
        return view

    # TODO: should be list of terms
    atom = random.choice(list(view.atoms))

    # TODO
    return view


def add_disjunction_from_existing_atoms(view: View):
    pass


def remove_disjunct(view: View):
    pass


def add_novel_conjunction(view: View):
    pass


def add_conjunction_with_existing_atom(view: View):
    pass


def mutate_view(View) -> View:
    options = [
        negate_atom,
        disjoin_random_unary_predicate,
        negate_view,
        factor_random_atom,
        merge_random_unary_predicate,
    ]

    return random.choice(options)(View)


if __name__ == "__main__":
    v = mutate_view(View.from_str("{A()B()}"))
    print(v)
