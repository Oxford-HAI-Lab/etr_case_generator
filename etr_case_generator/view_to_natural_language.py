import random

from etr_case_generator.ontology import Ontology
from pyetr import View, PredicateAtom, ArbitraryObject, State
from typing import cast


def view_to_natural_language(
    ontology: Ontology, view: View, obj_map: dict[str, str] = {}
) -> tuple[str, dict[str, str]]:
    """Take a View and convert it into a natural language string.

    The natural language string returned has no ending punctuation, and doesn't
    capitalize words except for proper nouns.

    Args:
        view (View): The view to convert.
        obj_map (dict[str, str]): A map from variable names to objects in the
            ontology. Defaults to {}.

    Returns:
        str: A string describing the View in natural language.
        dict[str, str]: The object map transformed as a result of running this new
            conversion. This can be useful if you want to transform multiple views
            according to the same variable interpretations.
    """

    def atom_to_natural_language(atom: PredicateAtom) -> str:
        if atom.predicate.arity != 1:
            raise ValueError("Currently only working with unary predicates.")

        neg = ""
        if not atom.predicate.verifier:
            neg = "not"

        term = atom.terms[
            0
        ]  # We can do this because we only consider unary predicates for now

        # Predicate is of the form "x is P"
        # Get names for predicate and term, and check if they are already mapped
        predicate_name = atom.predicate.name
        term_name = str(term)

        if predicate_name in obj_map.keys():
            predicate_nl = obj_map[predicate_name]
        else:
            # For now, since these predicates are all arity 1, we just take the
            # name property straightaway
            available_predicates = [
                p for p in ontology.predicates if p.name not in obj_map.values()
            ]
            predicate_nl = random.sample(available_predicates, k=1)[0].name
            obj_map[predicate_name] = predicate_nl

        # Check if term is arbitrary or not
        if type(term) == ArbitraryObject:
            # For now, for arbitrary terms we just use their variables (uppercased)
            term_nl = str(term).upper()

        else:
            if term_name in obj_map.keys():
                term_nl = obj_map[term_name]
            else:
                available_terms = [
                    t for t in ontology.objects if t not in obj_map.values()
                ]
                term_nl = random.sample(available_terms, k=1)[0]
                obj_map[term_name] = term_nl

        return " ".join(" ".join([term_nl, "is", neg, predicate_nl]).split())

    def state_to_natural_language(state: State) -> str:
        ret = ""
        atoms = [atom_to_natural_language(cast(PredicateAtom, atom)) for atom in state]

        # Sort atoms so that atoms beginning with "not" come last -- this helps the
        # natural language not read ambiguous, e.g. like "there is not an ace and a
        # ten"
        atoms.sort(key=lambda atom: atom.startswith("not"))

        return ret + " and ".join(atoms)

    # TODO: first, we'll consider very simple quantifiers where there aren't
    # suppositions
    # Universals: "everything is P"
    # Existentials: "something is P"
    universals = view.dependency_relation.universals
    existentials = view.dependency_relation.existentials
    all_quantifiers = universals | existentials
    if len(all_quantifiers) > 1:
        raise ValueError("Currently not considering cases with multiple quantifiers.")

    quantifier_str = ""
    q_name = ""
    if len(all_quantifiers) > 0:
        q_name = str(list(all_quantifiers)[0]).upper()
    if len(universals) > 0:
        quantifier_str = f"for all {q_name}, "
    if len(existentials) > 0:
        quantifier_str = f"there is a(n) {q_name} such that "

    states_for_stage = [state_to_natural_language(state) for state in view.stage]
    stage_str = ", or ".join(states_for_stage)
    if len(states_for_stage) > 1:
        stage_str = "either " + stage_str

    # TODO: this SetOfStates object should have an .empty method
    if not view.supposition.is_verum:
        states_for_supposition = [
            state_to_natural_language(state) for state in view.supposition
        ]
        supposition_str = ", or ".join(states_for_supposition)
        if len(states_for_supposition) > 1:
            supposition_str = "either " + supposition_str
        stage_str = "if " + supposition_str + ", then " + stage_str

    return quantifier_str + stage_str, obj_map
