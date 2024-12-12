from pyetr import View

def complex_inference(views: list[View]):
    new_view = views[0]
    if len(views) == 1:
        return new_view
    for v in views[1:]:
        print(f"New_View is {new_view.to_str()}")
        print(f"Updating on view {v.to_str()}")
        new_view = new_view.update(v, verbose=True).suppose(v, verbose=False)
    return new_view

if __name__ == "__main__":
    # v0 = View.from_str("{X()}")
    # v1 = View.from_str("{Y()}")
    # v2 = View.from_str("{Z()}")
    # v3 = complex_inference([v0,v1,v2])
    v = [
        View.from_str(
            "{KneelingByTheFire(Jane())LookingAtTV(Jane()), PeeringIntoTheGarden(Mark())StandingAtTheWindow(Mark())}"
        ),
        View.from_str("{KneelingByTheFire(Jane())}"),
    ]
    v3 = complex_inference(v)
    print(v3.to_str())  # {KneelingByTheFire(Jane())LookingAtTV(Jane())}^{KneelingByTheFire(Jane())}
    print(v3.to_fol())  # KneelingByTheFire(Jane())→(KneelingByTheFire(Jane()) ∧ LookingAtTV(Jane()))
    # print(v3.to_json())

