from pyetr import View
from pyetr.inference import default_inference_procedure

from etr_case_generator.reified_problem import FullProblem, ReifiedView


def get_etr_conclusion(views: list[ReifiedView]) -> ReifiedView:
    view_strings = [view.logical_form_etr for view in views]
    view_objects: list[View] = []
    for view_string in view_strings:
        view_objects.append(View.from_str(view_string))
    etr_predicted_conclusion: View = default_inference_procedure(tuple(view_objects))
    view = ReifiedView(logical_form_etr=etr_predicted_conclusion.__str__())
    return view

