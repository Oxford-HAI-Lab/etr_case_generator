import random

from etr_case_generator.generator2.reified_problem import PartialProblem, ReifiedView
from pyetr import View


def create_starting_problems() -> list[PartialProblem]:
    """
    Create a list of initial seed problems.

    Returns:
        list[PartialProblem]: A shuffled list of basic logical problems
    """
    starter_problems: list[PartialProblem] = [
        # Modus ponens -- from e32_1
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }^{ B(a()) }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ B(a()) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ A(a()) }")
            ),
            seed_id="e32_1"
        ),
        # Modus tollens -- from e41
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }^{ B(a()) }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ ~A(a()) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ ~B(a()) }")
            ),
            seed_id="e41"
        ),
        # Quantified modus ponens -- from e51
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("Ax { A(x*) }^{ B(x*) }")),
                ReifiedView(logical_form_etr_view=View.from_str("Ax { B(x*) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("Ax { A(x*) }")
            ),
            seed_id="e51"
        ),
        # Disjunction fallacy -- from e13
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(a()), C(b()) D(b()) }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ B(a()) }")
            ),
            seed_id="e13"
        )
    ]

    potential_starter_problems: list[PartialProblem] = [
        # From e3 - Disjunction with negation
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(a()), C(a()) D(a()) }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ ~A(a()) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ C(a()) D(a()) }")
            ),
            seed_id="e3"
        ),
        # From e42 - Only if with negation
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("{ ~A(a()) ~B(a()) }^{ ~B(a()) }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ ~B(a()) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ ~A(a()) }")
            ),
            seed_id="e42"
        ),
        # From e47 - Existential quantifier
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("∃x { B(x) A(x*) }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ A(a()*) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ B(a()) }")
            ),
            seed_id="e47"
        ),
        # From e52 - Universal quantifier with multiple predicates
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("∀x { A(x) B(x*) }^{ A(x) }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ B(a()*) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ B(a()*) A(a()) }")
            ),
            seed_id="e52"
        ),
        # From e57 - Universal and existential mix
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("∀x { B(x*) A(x) }^{ B(x*) }")),
                ReifiedView(logical_form_etr_view=View.from_str("∃x { B(x*) C(x) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("∃y { A(y) C(y) B(y*) }")
            ),
            seed_id="e57"
        ),
    ]

    # These seem good but they have problems :(
    error_problems: list[PartialProblem] = [
        # From e54 - Universal quantifier with optional case
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("∀x { 0, A(x*) B(x) }^{ A(x*) }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ A(a()*) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ A(a()*) B(a()) }")
            ),
            seed_id="e54"
        ),
        # From e61 - Universal with existential
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("∀x ∃y { ~A(x), B(y*) A(x) C(x,y) }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ B(b()*) }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("∀x ∃y { B(b()*) B(y*) A(x) C(x,y), B(b()*) ~A(x) }")
            ),
            seed_id="e61"
        ),
        # From e15 - Negation of conjunction
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("{ ~A() ~B() ~C() }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ A() }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ ~B(), ~C() }")
            ),
            seed_id="e15"
        ),
        # From e40i - Mutual exclusivity
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("{ ~A() ~B() C(), A() ~B() ~C(), ~A() B() ~C() }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ D() C() }^{ D() }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ B() }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ 0 }")
            ),
            seed_id="e40i"
        ),
        # From e28 - Basic step with multiple premises
        PartialProblem(
            premises=[
                ReifiedView(logical_form_etr_view=View.from_str("{ ~A(), A() }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ B() A() }^{ A() }")),
                ReifiedView(logical_form_etr_view=View.from_str("{ B() }"))
            ],
            etr_what_follows=ReifiedView(
                logical_form_etr_view=View.from_str("{ A() B() }")
            ),
            seed_id="e28"
        ),
    ]

    all_problems = starter_problems + potential_starter_problems
    random.shuffle(all_problems)
    return all_problems
