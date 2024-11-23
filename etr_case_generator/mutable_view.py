import random

from pyetr import View, SetOfStates


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

    def mutate(self):
        """Perform a random mutation on the view."""
        options = [self.negate]
        random.choice(options)()
