
from pyetr import View
from etr_case_generator.reified_problem import PartialProblem, ReifiedView


ILLUSORY_INFERENCE_FROM_DISJUNCTION: list[PartialProblem] = [
    PartialProblem(
        seed_id="target1",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(a()), C(b()) D(b()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ B(a()) }")
        )
    ),
    PartialProblem(
        seed_id="target2",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(b()), C(c()) D(d()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ B(b()) }")
        )
    ),
    PartialProblem(
        seed_id="target3",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) A(b()), A(c()) A(d()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ A(b()) }")
        )
    ),
    PartialProblem(
        seed_id="control1",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(a()), C(b()) D(b()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ ~A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ C(b()) D(b()) }")
        )
    ),
    PartialProblem(
        seed_id="control2",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(b()), C(c()) D(d()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ ~A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ C(c()) D(d()) }")
        )
    ),
    PartialProblem(
        seed_id="control3",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) A(b()), A(c()) A(d()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ ~A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ A(c()) A(d()) }")
        )
    ),
]

ILLUSORY_INFERENCE_FROM_DISJUNCTION_REVERSE_PREMISES_TEST: list[PartialProblem] = [
    PartialProblem(
        seed_id="target1",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(a()), C(b()) D(b()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ B(a()) }")
        )
    ),
    PartialProblem(
        seed_id="target2",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(b()), C(c()) D(d()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ B(b()) }")
        )
    ),
    PartialProblem(
        seed_id="target3",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) A(b()), A(c()) A(d()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ A(b()) }")
        )
    ),
    PartialProblem(
        seed_id="target4",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) A(b()), A(c()) A(d()), A(e()) A(f()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ A(b()) }")
        )
    ),
    PartialProblem(
        seed_id="target5",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) A(b()), A(c()), A(d()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }"))
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ A(b()) }")
        )
    ),
    PartialProblem(
        seed_id="control1",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(a()), C(b()) D(b()) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{B(a()),C(b())D(b())}")
        )
    ),
    PartialProblem(
        seed_id="control2",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) B(b()), C(c()) D(d()) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{B(b()),C(c())D(d())}")
        )
    ),
    PartialProblem(
        seed_id="control3",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) A(b()), A(c()) A(d()) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{A(b()),A(c())A(d())}")
        )
    ),
    PartialProblem(
        seed_id="control4",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) A(b()), A(c()) A(d()), A(e()) A(f()) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{A(b()),A(c())A(d()),A(e())A(f())}")
        )
    ),
    PartialProblem(
        seed_id="control5",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()) A(b()), A(c()), A(d()) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{A(b()),A(c()),A(d())}")
        )
    ),
]

"""
Source: Salvador Mascarenhas, Philipp Koralus. Illusory inferences with quantifiers.
Thinking and Reasoning, 2016, 23 (1), pp.33-48.

All questions are query questions ("Does it follow that {etr_what_follows}?").
"""
ILLUSORY_INFERENCES_WITH_QUANTIFIERS: list[PartialProblem] = [
    PartialProblem(
        seed_id="indefinite_illusory_inference_target", # p. 129
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("∃x { B(x) A(x*) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()*) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ B(a()) }")
        )
    ),
    PartialProblem(
        seed_id="indefinite_illusory_inference_target_reversed",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ A(a()*) }")),
            ReifiedView(logical_form_etr_view=View.from_str("∃x { B(x) A(x*) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ B(a()) }")
        )
    ),
    PartialProblem(
        seed_id="indefinite_illusory_inference_control",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("∃x { B(x) A(x*) }")),
            ReifiedView(logical_form_etr_view=View.from_str("{ ~A(a()*) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{0}")
        )
    ),
    PartialProblem(
        seed_id="indefinite_illusory_inference_control_reversed",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ ~A(a()*) }")),
            ReifiedView(logical_form_etr_view=View.from_str("∃x { B(x) A(x*) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{0}")
        )
    ),
]

MODUS_PONENS_MODUS_TOLLENS: list[PartialProblem] = [
    PartialProblem(
        seed_id="control",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ P(a()) Q(a()) }^{ P(a()) } ")),
            ReifiedView(logical_form_etr_view=View.from_str("{ P(a()) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ Q(a()) }")
        )
    ),
    PartialProblem(
        seed_id="target",
        premises=[
            ReifiedView(logical_form_etr_view=View.from_str("{ P(a()) Q(a()) }^{ P(a()) } ")),
            ReifiedView(logical_form_etr_view=View.from_str("{ ~Q(a()) }")),
        ],
        etr_what_follows=ReifiedView(
            logical_form_etr_view=View.from_str("{ ~P(a()) }")
        )
    ),
]
