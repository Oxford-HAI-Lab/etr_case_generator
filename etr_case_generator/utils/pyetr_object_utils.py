from pyetr import PredicateAtom, View
from typing import cast, Optional


def predicate_domains_of_view(
    view: View, arity: Optional[int] = None
) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    for atom in view.atoms:
        atom = cast(PredicateAtom, atom)
        if arity and atom.predicate.arity != arity:
            continue
        name = atom.predicate.name
        term_names = [str(t) for t in atom.terms]
        if name in mapping.keys():
            mapping[name] = list(set(mapping[name] + term_names))
        else:
            mapping[name] = list(set(term_names))
    return mapping
