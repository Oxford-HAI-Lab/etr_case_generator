#!/usr/bin/env python3
"""
Script to reverse the order of premises in ETR case files.

This script takes a JSONL file containing ETR problems and reverses the order of premises
in each problem, both in the data structure and in the question text.
"""

import json
import argparse
import os
import re
import sys
from typing import Dict, Any, List
import copy


def reverse_premise_lists(problem: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Reverse the order of premises in the problem data structure.
    
    Args:
        problem: A problem dictionary from the JSONL file
        
    Returns:
        The problem with reversed premise lists
    """
    # Make a deep copy to avoid modifying the original (more efficient than JSON serialization)
    result = copy.deepcopy(problem)
    
    # Get the generation details
    gen_details = result["scoring_guide"]["generation_details"]
    
    # Reverse all premise lists
    gen_details["premises_etr"] = gen_details["premises_etr"][::-1]
    gen_details["premises_english"] = gen_details["premises_english"][::-1]
    gen_details["premises_fnodes"] = gen_details["premises_fnodes"][::-1]
    
    return result


def find_and_replace_premises(question: str, premises_english: List[str]) -> str:
    """
    Find and replace premises in the question text with reversed premises.
    
    Args:
        question: The original question text
        premises_english: The list of premises in English (already reversed)
        
    Returns:
        The updated question with reversed premises
    """
    # Get the original premises from the problem before we reversed them
    # This means we need to reverse them again to get the original order
    original_premises = premises_english[::-1]
    
    # Format the original premises as bullet points
    original_bullet_list = "\n* " + "\n* ".join(original_premises)
    
    # Format the reversed premises as bullet points
    reversed_bullet_list = "\n* " + "\n* ".join(premises_english)
    
    # Check if the original bullet list exists in the question
    if original_bullet_list not in question:
        # Try with Windows-style line endings
        original_bullet_list_windows = "\r\n* " + "\r\n* ".join(original_premises)
        if original_bullet_list_windows in question:
            # If Windows line endings are found, use Windows line endings for replacement too
            reversed_bullet_list = "\r\n* " + "\r\n* ".join(premises_english)
            return question.replace(original_bullet_list_windows, reversed_bullet_list)
        
        raise ValueError("Could not find the exact list of premises in the question text.")
    
    # Replace the original bullet list with the reversed one
    return question.replace(original_bullet_list, reversed_bullet_list)


def process_problem(problem: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Process a single problem by reversing its premises.
    
    Args:
        problem: A problem dictionary from the JSONL file
        
    Returns:
        The problem with reversed premises
    """
    # Reverse the premise lists in the data structure
    modified_problem = reverse_premise_lists(problem)
    
    # Get the reversed premises in English
    reversed_premises = modified_problem["scoring_guide"]["generation_details"]["premises_english"]
    
    # Update the question text
    original_question = modified_problem["question"]
    modified_question = find_and_replace_premises(original_question, reversed_premises)
    modified_problem["question"] = modified_question
    
    return modified_problem


def main():
    """Main function to process the input JSONL file."""
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Reverse the order of premises in ETR problem files")
    parser.add_argument("input_file", help="Path to the input JSONL file")
    parser.add_argument("--output-file", help="Path to the output JSONL file (default: 'reverse_<input_file>')")

    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output file name
    input_basename = os.path.basename(args.input_file)
    output_file = args.output_file if args.output_file else os.path.join(
        os.path.dirname(args.input_file), 
        f"reverse_{input_basename}"
    )
    
    print(f"Processing {args.input_file}")
    print(f"Output will be written to {output_file}")
    
    processed_count = 0
    error_count = 0
    
    # Validate that the input file has a valid JSONL format
    with open(args.input_file, 'r') as f_in:
        first_line = f_in.readline().strip()
        if first_line:
            json.loads(first_line)  # Test parse the first line
    
    # Count total lines for progress reporting
    total_lines = sum(1 for line in open(args.input_file) if line.strip())
    print(f"Found {total_lines} non-empty lines in file")

    # Process the input file line by line and write output
    with open(args.input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        for line_num, line in enumerate(f_in, 1):
            if line_num % 100 == 0:
                print(f"Processing line {line_num}/{total_lines}...")
                
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            # Parse the JSON object (will crash on error)
            problem = json.loads(line)
            
            # Process the problem (will crash on error)
            modified_problem = process_problem(problem)
            
            # Write the modified problem to the output file
            f_out.write(json.dumps(modified_problem) + '\n')
            processed_count += 1
    
    print(f"Processing complete. Successfully processed {processed_count} problems.")


if __name__ == "__main__":
    main()
