import random
from typing import cast
from pyetr import ArbitraryObject, FunctionalTerm, PredicateAtom, View


def get_object_sets_for_view(
    view: View,
) -> tuple[dict[str, set[str]], set[str], set[str]]:
    """Take a view and return sets of predicates (at different arities), constants, and
        arbitrary objects used in the view.

    Args:
        view (View): The View to parse.

    Raises:
        ValueError: If we ever handle a FunctionalTerm with a nonzero arity.
        ValueError: If we ever handle a term that's neither an ArbitraryObject nor a
            Functional Term

    Returns:
        tuple[dict[str, set[str]], set[str], set[str]]:
            dict[str, set[str]]: Predicates, mapping arity to a set of letters
            set[str]: Constants
            set[str]: Arbitrary objects
    """
    predicates: dict[str, set[str]] = {}
    constants: set[str] = set()
    arb_objs: set[str] = set()

    for state in view.weights._weights.keys():
        for atom in state:
            atom = cast(PredicateAtom, atom)
            arity = str(atom.predicate.arity)
            name = str(atom.predicate.name)
            if arity not in predicates.keys():
                predicates[arity] = set([name])
            else:
                predicates[arity].add(name)

            for term in atom.terms:
                if type(term) == ArbitraryObject:
                    arb_objs.add(term.name)
                elif type(term) == FunctionalTerm:
                    if term.f.arity != 0:
                        raise ValueError
                    constants.add(term.f.name)
                else:
                    raise ValueError

    return predicates, constants, arb_objs


def atom_to_str(atom) -> str:
    return str(atom)[:-1] + "())"


def state_to_str(state) -> str:
    return "".join([atom_to_str(a) for a in state])


def set_of_states_to_str(set_of_states) -> str:
    return "{" + ",".join([state_to_str(s) for s in set_of_states]) + "}"


def get_view_mutations(view: View, only_increase: bool = False, only_do_one: bool = False) -> set[View]:
    """_summary_

    Args:
        view (View): The base View to mutate.
        only_increase (bool, optional): If set to True, will only return views that are
        larger than view in terms of number of atoms. Defaults to False.
        only_do_one (bool, optional): If set to True, will only return one mutation, in a set of size 1. Defaults to False.

    Raises:
        ValueError: _description_

    Returns:
        set[View]: _description_
    """
    mutation_strings = set[str]()

    # Assemble lists of strings of predicates, constants, and arbitrary objects
    predicates, constants, arb_objs = get_object_sets_for_view(view)

    if len(predicates.keys()) > 1:
        raise ValueError
    predicates = predicates["1"]  # For now we only do unary predicates

    max_predicate = max(predicates) # From P, Q, R, you get R
    new_predicate = chr(ord(max_predicate) + 1)  # This would give S

    if len(arb_objs) == 0:
        arb_objs = set(["a"])
        new_arb_obj = "a"
    else:
        max_arb_obj = max(arb_objs)
        new_arb_obj = chr(ord(max_arb_obj) + 1)

    if not only_increase:
        for o in constants:
            # Also append problems where the variable is taken to be at issue in all
            # occurrences (can I do this with issue only occurring sometimes?)
            for is_at_issue in [new_arb_obj, new_arb_obj + "*"]:
                mutation_strings.add(
                    f"A{new_arb_obj} " + view.to_str().replace(o + "()", is_at_issue)
                )
                mutation_strings.add(
                    f"E{new_arb_obj} " + view.to_str().replace(o + "()", is_at_issue)
                )

    if len(constants) == 0:
        constants = set(["a"])
        new_constant = "a"
    else:
        max_constant = max(constants)
        new_constant = chr(ord(max_constant) + 1)

    predicates.add(new_predicate)  # Now, e.g., predicates are P, Q, R, S
    constants.add(new_constant)

    atoms = [
        f"{p}({o}())" for p in predicates for o in constants
    ]

    # If only_increase is set to true, filter atoms to the set of atoms that are not
    # already in the view
    if only_increase:
        existing_atoms = set([atom_to_str(a) for a in view.atoms])
        atoms = [a for a in atoms if a not in existing_atoms]
    else:
        atoms += [atom_to_str(a) for a in view.atoms]
        atoms = list(set(atoms))

    # We also don't do anything with suppositions in this version
    # TODO: prepend all possible quantifier strings given the current set of arbitrary
    # objects
    for atom in atoms:
        atom_at_issue = atom[:-1] + "*)"
        # All conjunctions
        for i in range(len(list(view.stage))):
            new_state_str = state_to_str(list(view.stage)[i]) + atom
            new_stage_str = (
                "{"
                + ",".join(
                    list([state_to_str(s) for s in view.stage])[:i]
                    + [new_state_str]
                    + list([state_to_str(s) for s in view.stage])[i + 1 :]
                )
                + "}"
            )
            mutation_strings.add(new_stage_str)

            # Also add one where the new atom is at issue -- this can also be done
            # before the for loop with atoms (same as below TODO)
            new_state_str = state_to_str(list(view.stage)[i]) + atom_at_issue
            new_stage_str = (
                "{"
                + ",".join(
                    list([state_to_str(s) for s in view.stage])[:i]
                    + [new_state_str]
                    + list([state_to_str(s) for s in view.stage])[i + 1 :]
                )
                + "}"
            )
            mutation_strings.add(new_stage_str)

        # TODO add a mutation where this atom is dropped entirely

        # Disjunctions
        mutation_strings.add(
            "{"
            + ",".join(list([state_to_str(s) for s in view.stage]) + [atom])
            + "}"
        )
        mutation_strings.add(
            "{"
            + ",".join(
                list([state_to_str(s) for s in view.stage]) + [atom_at_issue]
            )
            + "}"
        )
    
        # TODO: refactor to only have to loop once (negate every atom before for loop)
        # Now, negate
        if atom[0] == "~":
            atom = atom[1:]
        else:
            atom = "~" + atom

        atom_at_issue = atom[:-1] + "*)"
        # All conjunctions
        for i in range(len(list(view.stage))):
            # Add atom directly into state string (P(a()) becomes P(a())Q(a()))
            new_state_str = state_to_str(list(view.stage)[i]) + atom
            new_stage_str = (
                "{"
                + ",".join(  # Now that we're disjoining, the delimiter is a comma
                    list([state_to_str(s) for s in view.stage])[:i]
                    + [new_state_str]
                    + list([state_to_str(s) for s in view.stage])[i + 1 :]
                )
                + "}"
            )
            mutation_strings.add(new_stage_str)

            # Also add one where the new atom is at issue
            new_state_str = state_to_str(list(view.stage)[i]) + atom_at_issue
            new_stage_str = (
                "{"
                + ",".join(
                    list([state_to_str(s) for s in view.stage])[:i]
                    + [new_state_str]
                    + list([state_to_str(s) for s in view.stage])[i + 1 :]
                )
                + "}"
            )
            mutation_strings.add(new_stage_str)

        # Disjunctions
        mutation_strings.add(
            "{"
            + ",".join(list([state_to_str(s) for s in view.stage]) + [atom])
            + "}"
        )
        mutation_strings.add(
            "{"
            + ",".join(
                list([state_to_str(s) for s in view.stage]) + [atom_at_issue]
            )
            + "}"
        )

    # Convert strings to Views at the end
    if only_do_one and mutation_strings:
        # If we only need one, randomly select a string and convert just that one
        chosen_string = random.choice(list(mutation_strings))
        mutations = {View.from_str(chosen_string)}
    else:
        # Convert all strings to Views
        mutations = {View.from_str(s) for s in mutation_strings}

    # Add an assertion that if only_increase is passed as True, we only return views
    # that are larger than the original view
    if only_increase:
        # Count the number of mutations with more, fewer, and the same number of atoms
        num_atoms = len(view.atoms)
        num_less = 0
        num_more = 0
        num_same = 0
        for m in mutations:
            if len(m.atoms) > num_atoms:
                num_more += 1
            elif len(m.atoms) < num_atoms:
                num_less += 1
            else:
                num_same += 1
        assert all([len(m.atoms) >= len(view.atoms) for m in mutations]), f"Original num atoms: {len(view.atoms)}, Num Less: {num_less}, Num Same: {num_same}, Num More: {num_more}"

    return mutations

if __name__ == "__main__":
    print(get_view_mutations(View.from_str("{A(a())}")))
