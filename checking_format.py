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
    # Single set of braces, all states comma-separated
    "{~Red(cat()),Furry(cat()),Red(cat()),~Furry(cat())}",
    
    # Nested braces (incorrect format)
    "{~Red(cat()),Furry(cat())},{Red(cat()),~Furry(cat())}",
    
    # Single state with all conditions (incorrect logical form)
    "{~Red(cat())Furry(cat())Red(cat())~Furry(cat())}",
]

if __name__ == "__main__":
    print("Testing different formats for if-and-only-if construction...")
    for fmt in formats:
        test_format(fmt)
