import random

# When running with a local build, my linter complains, so tell VSCode to ignore it
from pyetr.atoms import Atom  # type: ignore
from pyetr.view import View  # type: ignore
from pyetr.stateset import State, SetOfStates  # type: ignore


def negate_atom(view: View) -> View:
    # Negates one atom of one state in the view's stage or supposition

    def negate_atom_in_SetOfStates(set_of_states: SetOfStates) -> SetOfStates:
        # Copy supposition to mutable object
        sos: set[State] = set(set_of_states)

        # Pick a random state
        frozen_state: frozenset[Atom] = sos.pop()
        state: set[Atom] = set(frozen_state)

        # Pick a random atom
        atom: Atom = state.pop()

        # Negate
        atom = ~atom

        # Recreate the SetOfStates
        new_state = State(state | {atom})
        new_sos = SetOfStates(sos | {new_state})

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


def permute_view(View) -> View:
    options = [negate_atom]

    return random.choice(options)(View)


if __name__ == "__main__":
    v = permute_view(View.from_str("{A()}"))
    print(v)
