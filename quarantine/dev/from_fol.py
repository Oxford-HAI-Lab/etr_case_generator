from pyetr import View

def test_view_conversion():
    # Simple examples
    views = [
        "{King()Ace()}",
        "{~Ace()}",
        "{Jack()Queen()}",
        "{k()}",
        "{a()k()}",
        "{KneelingByTheFire(Jane())LookingAtTV(Jane()), PeeringIntoTheGarden(Mark())StandingAtTheWindow(Mark())}",
        "{KneelingByTheFire(Jane())}",
        "{LookingAtTV(Jane())}",
        "{T()K(),Q()A()}",
        "{K()}",
        "{T()}",
        "{King()Ace(),Jack()Queen()}",
        "{~Ace()}",
        "{Jack()Queen()}",
        "{p2()r1()q2()s1(),s2()r1()r2()s1(),s2()p1()q1()r2(),p2()p1()q1()q2()}",
        "{a()}",
        "{k()}",
        "{a()k()}",
        "{Smokes(j()),Smokes(m())}"
    ]

    print("Testing View conversion:")
    print("-" * 40)
    
    for view_str in views:
        print(f"\nOriginal view string: {view_str}")
        
        # Create View from string
        view = View.from_str(view_str)
        
        # Convert to FOL
        fol_str = view.to_fol()
        print(f"As FOL: {fol_str}")
        
        # Convert back to View
        view_from_fol = View.from_fol(fol_str)
        print(f"Back to view: {view_from_fol}")
        
        # Verify they match
        print(f"Views match: {view == view_from_fol}")

if __name__ == "__main__":
    test_view_conversion()
