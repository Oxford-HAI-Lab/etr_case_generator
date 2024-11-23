import random

from pyetr import SetOfStates, State, View
from pyetr.atoms import Atom


class MutableView:
    """A thin wrapper around a pyetr.View object that allows for in-place modifications."""

    def __init__(self, view):
        self.view = view

    def negate(self):
        """Negate the view."""
        self.view = self.view.negation()

    def remove_noncommital_states(self):
        """Remove noncommital states from the view. E.g., {p, q, 0} becomes {p, q}."""
        new_stage = set()
        new_sup = set()
        for state in self.view.stage:
            if len(state) > 0:
                new_stage.add(state)
        for state in self.view.supposition:
            if len(state) > 0:
                new_sup.add(state)
        self.view = View.with_restriction(
            stage=SetOfStates(new_stage),
            supposition=SetOfStates(new_sup),
            dependency_relation=self.view.dependency_relation,
            issue_structure=self.view.issue_structure,
            weights=self.view.weights,
        )

    def factor_atom(self, atom: Atom):
        atom_view = View.with_defaults(stage=SetOfStates({State({atom})}))
        self.view = self.view.factor(atom_view)
        self.remove_noncommital_states()

    def factor_random_atom(self):
        # Cannot factor from an empty view
        if len(self.view.atoms) == 0:
            return

        atom = random.choice(list(self.view.atoms))
        self.factor_atom(atom)

    def mutate(self):
        """Perform a random mutation on the view."""
        options = [self.negate, self.factor_random_atom]
        random.choice(options)()
