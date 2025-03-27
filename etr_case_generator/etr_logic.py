from pyetr import View
from pyetr.inference import default_inference_procedure

from etr_case_generator.generator2.reified_problem import FullProblem, ReifiedView


def get_etr_conclusion(views: list[ReifiedView]) -> ReifiedView:
    view_strings = [view.logical_form_etr for view in views]
    view_objects: list[View] = []
    for view_string in view_strings:
        # print(f"Parsing view_string: {view_string}")
        view_objects.append(View.from_str(view_string))
    # print("View objects:")
    # print(view_objects)
    etr_predicted_conclusion: View = default_inference_procedure(tuple(view_objects))
    # print("Predicted conclusion:")
    # print(etr_predicted_conclusion)
    view = ReifiedView(logical_form_etr=etr_predicted_conclusion.__str__())
    # TODO Need to convert to PySMT format...
    return view

