from pyetr import View

from pysmt.shortcuts import Symbol, ForAll, Exists, Solver, Not, Real, Or, Times, get_env
from pysmt.typing import BOOL, REAL
from pysmt.logics import QF_LRA

# Example Views:
# {'_stage': {King()Ten(),Five()Seven(),Ace()Seven()Two()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {King()Ten(),Five()Seven(),Ace()Seven()Two()}}
# {'_stage': {King()Ten(),Five()Seven(),Ace()Seven()Two()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {King()Ten(),Five()Seven(),Ace()Seven()Two()}}
# {'_stage': {Nine()King()Two(),~Ace()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Nine()King()Two(),~Ace()}}
# {'_stage': {Ace()Three(),Seven()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Ace()Three(),Seven()}}
# {'_stage': {Ace()Three(),Seven()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Ace()Three(),Seven()}}
# {'_stage': {Queen()Three()Two(),Eight()Three()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Queen()Three()Two(),Eight()Three()}}
# {'_stage': {~Ten(),Jack()Three()Ten()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {~Ten(),Jack()Three()Ten()}}
# {'_stage': {Queen()Nine(),~Eight()~Ten()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Queen()Nine(),~Eight()~Ten()}}
# {'_stage': {Ace()Eight()~Five()}, '_supposition': {~Jack()Four()Seven()}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Ace()Eight()~Five()}}
# {'_stage': {Eight()King()Five(),Eight()King()}, '_supposition': {0}, '_dependency_relation': U={} E={}, '_issue_structure': {}, '_weights': {Eight()King()Five(),Eight()King()}}


def view_to_smt(view: View):
    ...
