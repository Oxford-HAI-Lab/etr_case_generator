from pyetr import View

def test_format(s: str) -> None:
    print(f"\nTesting: {s}")
    try:
        view = View.from_str(s)
        print("SUCCESS! View parsed as:")
        print(view)
    except Exception as e:
        print(f"FAILED with error: {str(e)}")

# Test different formats for "cat is red if and only if furry"
formats = [
    # Original format
    "{~Red(cat()),Furry(cat()),Red(cat()),~Furry(cat())}",
    
    # With parentheses grouping implications
    "{(~Red(cat()),Furry(cat())),(~Furry(cat()),Red(cat()))}",
    
    # With parentheses around each atom pair
    "{(~Red(cat()),Furry(cat())),(~Furry(cat()),Red(cat()))}",
    
    # With parentheses and no commas between grouped atoms
    "{(~Red(cat())Furry(cat()))(~Furry(cat())Red(cat()))}",
    
    # With nested parentheses
    "{((~Red(cat()),Furry(cat())),(~Furry(cat()),Red(cat())))}",
    
    # With parentheses but still using commas
    "{(~Red(cat())),Furry(cat()),(~Furry(cat())),Red(cat())}",
]

if __name__ == "__main__":
    print("Testing different formats for if-and-only-if construction...")
    for fmt in formats:
        test_format(fmt)
