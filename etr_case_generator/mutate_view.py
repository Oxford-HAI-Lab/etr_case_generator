import random
import string

from pyetr import State, SetOfStates, View, DependencyRelation, ArbitraryObject
from pyetr.atoms import Atom
from pyetr.atoms.predicate import Predicate
from pyetr.atoms.predicate_atom import PredicateAtom
from pyetr.stateset import State, SetOfStates, Stage, Supposition
from pyetr.atoms.terms.function import Function
from pyetr.atoms.terms.term import FunctionalTerm, Term
from typing import cast

ALPHABET = list(set(string.ascii_uppercase))


def negate_atom(view: View) -> View:
    """Negates one atom of one state in the view's stage or supposition."""

    def negate_atom_in_SetOfStates(set_of_states: SetOfStates) -> SetOfStates:
        # Can't negate anything in an empty set of states
        if len(set_of_states) == 0:
            return set_of_states

        # Copy supposition to mutable object
        sos: set[State] = set(set_of_states)

        # Pick a random state
        orig_state: State = random.choice(list(sos))
        state: set[Atom] = set(orig_state)

        if len(state) == 0:
            return set_of_states

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
    # Cannot factor an atom if it contains quantified terms
    if any(
        [
            t in cast(PredicateAtom, atom).terms
            for t in view.dependency_relation.universals
        ]
        + [
            t in cast(PredicateAtom, atom).terms
            for t in view.dependency_relation.existentials
        ]
    ):
        return view
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


def replace_term_in_atom(
    atom: PredicateAtom,
    replacement_term: Term,
    term_to_replace: FunctionalTerm,
) -> PredicateAtom:
    new_terms = tuple(
        [replacement_term if term == term_to_replace else term for term in atom.terms]
    )
    return PredicateAtom(predicate=atom.predicate, terms=new_terms)


def replace_term_in_set_of_states(
    set_of_states: SetOfStates,
    replacement_term: Term,
    term_to_replace: FunctionalTerm,
) -> SetOfStates:
    return SetOfStates(
        [
            State(
                [
                    replace_term_in_atom(
                        cast(PredicateAtom, atom), replacement_term, term_to_replace
                    )
                    for atom in state
                ]
            )
            for state in set_of_states
        ]
    )


def replace_term_in_view(
    view: View, term_to_replace, replacement_term
) -> tuple[Stage, Supposition]:
    """Replace a term in a view with another term.

    Args:
        view (View): The view to modify.
        term_to_replace: The term to replace.
        replacement_term: The term to replace with.

    Returns:
        tuple[Stage, Supposition]: The modified stage and supposition.
    """

    new_stage = Stage(
        [
            State(
                [
                    replace_term_in_atom(
                        cast(PredicateAtom, atom), replacement_term, term_to_replace
                    )
                    for atom in state
                ]
            )
            for state in view.stage
        ]
    )
    new_supposition = Supposition(
        [
            State(
                [
                    replace_term_in_atom(
                        cast(PredicateAtom, atom), replacement_term, term_to_replace
                    )
                    for atom in state
                ]
            )
            for state in view.supposition
        ]
    )
    return new_stage, new_supposition


def add_quantification_to_view(
    view: View,
    quantify: str,
    new_stage: Stage,
    new_supposition: Supposition,
    arb_obj_name: str,
) -> View:
    """Add quantification to a view.

    Args:
        view (View): The view to add quantification to.
        quantify (str): The quantification to add. Must be one of "universal" or
            "existential".

    Returns:
        View: The view with quantification added.
    """
    if quantify not in ["universal", "existential"]:
        raise ValueError("Quantification must be one of 'universal' or 'existential'.")

    terms = set(
        [
            t
            for atom in new_stage.atoms | new_supposition.atoms
            for t in cast(PredicateAtom, atom).terms
        ]
    )

    if quantify == "universal":
        return View.with_defaults(
            stage=new_stage,
            supposition=new_supposition,
            dependency_relation=view.dependency_relation.fusion(
                DependencyRelation(
                    universals=[ArbitraryObject(name=arb_obj_name)],
                    existentials=[],
                    dependencies=[],
                )
            ).restriction(set([t for t in terms if isinstance(t, ArbitraryObject)])),
        )

    else:
        return View.with_defaults(
            stage=new_stage,
            supposition=new_supposition,
            dependency_relation=view.dependency_relation.fusion(
                DependencyRelation(
                    universals=[],
                    existentials=[ArbitraryObject(name=arb_obj_name)],
                    dependencies=[],
                )
            ).restriction(
                set(
                    [
                        t
                        for t in terms | set([ArbitraryObject(name=arb_obj_name)])
                        if isinstance(t, ArbitraryObject)
                    ]
                )
            ),
        )


def replace_random_term_in_view(
    view: View,
) -> tuple[Stage, Supposition, str]:
    """Replace a random term in the view with an arbitrary object.

    Args:
        view (View): The view to modify.

    Returns:
        tuple[Stage, Supposition]: The modified stage and supposition.
    """

    # Take all functional terms that appear in the view and choose one at random
    # to replace with an arbitrary object
    atoms = view.stage.atoms | view.supposition.atoms
    terms = set([term for atom in atoms for term in cast(PredicateAtom, atom).terms])
    term_to_replace = random.choice(list(terms))
    arb_obj_name = random.choice(
        list(
            set(ALPHABET)
            - set(
                [u.name.upper() for u in view.dependency_relation.universals]
                + [e.name.upper() for e in view.dependency_relation.existentials]
            )
        )
    ).lower()
    stage, supposition = replace_term_in_view(
        view, term_to_replace, ArbitraryObject(name=arb_obj_name)
    )

    return stage, supposition, arb_obj_name


def random_universal_quantify(view: View) -> View:
    """Replace a random term in the view with an arbitrary object and universally
    quantify it.

    Args:
        view (View): The view to add quantification to.

    Returns:
        View: The view with quantification added.
    """
    if len(view.atoms) == 0:
        return view

    new_stage, new_supposition, arb_obj_name = replace_random_term_in_view(view)
    return add_quantification_to_view(
        view=view,
        quantify="universal",
        new_stage=new_stage,
        new_supposition=new_supposition,
        arb_obj_name=arb_obj_name,
    )


def random_existential_quantify(view: View) -> View:
    """Replace a random term in the view with an arbitrary object and existentially
    quantify it.

    Args:
        view (View): The view to add quantification to.

    Returns:
        View: The view with quantification added.
    """
    if len(view.atoms) == 0:
        return view

    new_stage, new_supposition, arb_obj_name = replace_random_term_in_view(view)
    return add_quantification_to_view(
        view=view,
        quantify="existential",
        new_stage=new_stage,
        new_supposition=new_supposition,
        arb_obj_name=arb_obj_name,
    )


def mutate_view(View) -> View:
    options = [
        negate_atom,
        disjoin_random_unary_predicate,
        negate_view,
        factor_random_atom,
        merge_random_unary_predicate,
        random_universal_quantify,
        random_existential_quantify,
    ]

    return random.choice(options)(View)


if __name__ == "__main__":
    v = mutate_view(View.from_str("{A()B()}"))
    print(v)
