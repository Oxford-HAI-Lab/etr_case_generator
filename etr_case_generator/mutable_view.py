import random
import string

from pyetr import (
    SetOfStates,
    State,
    View,
    PredicateAtom,
    Predicate,
    FunctionalTerm,
    Function,
)
from pyetr.atoms import Atom
from typing import cast


ALPHABET = set(string.ascii_uppercase)


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
        """Factor a specific atom from the view.

        Args:
            atom (Atom): The atom to factor.
        """
        atom_view = View.with_defaults(stage=SetOfStates({State({atom})}))
        self.view = self.view.factor(atom_view)
        self.remove_noncommital_states()

    def factor_random_atom(self):
        """Choose a random atom from the view and factor it out."""
        # Cannot factor from an empty view
        if len(self.view.atoms) == 0:
            return

        atom = random.choice(list(self.view.atoms))
        self.factor_atom(atom)

    def merge_random_unary_predicate(self):
        """Create a random unary predicate and merge it to either the supposition or
        stage.
        The letters may correspond to existing predicates / objects in the view, or they
        may not.
        """

        predicate_letter, term_letter = random.sample(list(ALPHABET), k=2)

        new_predicate = PredicateAtom(
            predicate=Predicate(name=predicate_letter, arity=1),
            terms=(FunctionalTerm(f=Function(name=term_letter, arity=0), t=()),),
        )

        self.view = self.view.merge(
            View.with_defaults(
                stage=SetOfStates({State({new_predicate})}),
            )
        )

    def mutate(self):
        """Perform a random mutation on the view."""
        options = [
            self.negate,
            self.factor_random_atom,
            self.merge_random_unary_predicate,
        ]
        random.choice(options)()
