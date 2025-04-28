import argparse
import csv
import glob
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


NONE_STR = "None"


JSON_KEYS = [
    "model_name",
    "doc_id",
    "doc/question",
    "doc/scoring_guide/etr_predicted",
    "doc/scoring_guide/etr_predicted_exact",
    "doc/scoring_guide/etr_predicted_is_classically_correct",
    "doc/scoring_guide/is_logically_equivalent",
    "doc/scoring_guide/generation_details/total_num_atoms",
    "doc/scoring_guide/generation_details/num_disjuncts",
    "doc/scoring_guide/generation_details/num_conjuncts",
    "doc/scoring_guide/generation_details/num_predicates_per_problem",
    "doc/scoring_guide/generation_details/num_objects_per_problem",
    "doc/scoring_guide/generation_details/premises_etr",
    "doc/scoring_guide/generation_details/premises_fnodes",
    "doc/scoring_guide/generation_details/is_chain_of_thought",
    "doc/scoring_guide/open_ended/conclusion_agrees_in_yes_no_case",
    "doc/scoring_guide/yes_no/conclusion_etr",
    "doc/scoring_guide/yes_no/conclusion_is_classically_correct",
    "doc/scoring_guide/yes_no/conclusion_english",
    "doc/scoring_guide/yes_no/conclusion_is_etr_predicted",
    "resps",
    "filtered_resps",
    "correct",
    "is_etr_predicted",
    "is_etr_predicted_exact",
    "len_response",
    "parse_error",
    "model_answer",
    "full_model_response",
    "correct_and_etr",
    "correct_and_not_etr",
    "not_correct_and_etr",
    "not_correct_and_not_etr"
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert JSONL results files to CSV format"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="open_ended",
        help="Pattern to match in filenames (default: 'open_ended')",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="lm_eval/tasks/etr_problems/good_results/all_results.csv",
        help="Output CSV file location (default: good_results/all_results.csv)",
    )
    parser.add_argument(
        "--base-dir",
        type=str,
        default="lm_eval/tasks/etr_problems/good_results",
        help="Base directory to search for JSONL files (default: lm_eval/tasks/etr_problems/good_results)",
    )
    parser.add_argument(
        "--in-past-hours",
        type=float,
        default=24.0,
        help="Only include files modified within this many hours (default: 24)",
    )
    return parser.parse_args()


def load_jsonl_files(pattern: str, base_dir: str, in_past_hours: float = 24.0):
    """Load all JSONL files matching pattern from base_dir and subdirs."""
    
    # Get files in base dir and one level deep that contain "samples"
    search_paths = [
        f"{base_dir}/*samples*{pattern}*.jsonl",
        f"{base_dir}/*/*samples*{pattern}*.jsonl"
    ]
    
    # Get current time for comparison
    now = datetime.now()
    cutoff_time = now - timedelta(hours=in_past_hours)
    
    files = []
    for path in search_paths:
        for file in glob.glob(path):
            # Check file modification time
            mtime = datetime.fromtimestamp(os.path.getmtime(file))
            if mtime >= cutoff_time:
                files.append(file)
            # else:
            #     print(f"Skipping {file} (modified {mtime})")
    
    results = {}
    for file in files:
        with open(file) as f:
            lines = f.readlines()
            results[file] = [json.loads(line) for line in lines]
            
    return results


def write_to_csv(results: dict, output_file: str) -> tuple[int, int, int]:
    """Write JSON data to CSV file using specified keys."""
    rows_written = 0  # Track actual rows written
    prev_line_count = 0  # Track previous line count
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    total_entries = sum(len(data) for data in results.values())
    processed_entries = 0
    skipped_entries = 0
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=JSON_KEYS,
            quoting=csv.QUOTE_MINIMAL,
            quotechar='"',
            doublequote=True
        )
        writer.writeheader()
        
        # Write each JSON entry as a CSV row
        for filename, file_data in results.items():
            # Extract model name from directory path
            model_name = Path(filename).parent.name
            for entry_idx, entry in enumerate(file_data):
                # Count lines before writing
                with open(output_file, 'r', encoding='utf-8') as f:
                    prev_line_count = sum(1 for _ in f)

                processed_entries += 1
                row = {}
                for key in JSON_KEYS:
                    if key == "model_name":
                        row[key] = model_name
                        continue
                    # Handle nested keys (e.g., "doc/question")
                    try:
                        value = entry
                        for k in key.split('/'):
                            if not isinstance(value, dict):
                                value = None
                                break
                            value = value.get(k, None)
                        # Special handling for known list fields
                        if key == "resps":
                            assert isinstance(value, list) and len(value) == 1 and isinstance(value[0], list) and len(value[0]) == 1, \
                                f"Expected resps to be list[list[str]] with single items, got {value}"
                            value = value[0][0]
                        elif key == "filtered_resps":
                            assert isinstance(value, list) and len(value) == 1, \
                                f"Expected filtered_resps to be list[str] with single item, got {value}"
                            value = value[0]
                        # Convert other lists to string representation
                        elif isinstance(value, list):
                            value = str(value)
                        # Replace newlines with paragraph mark for readability if string. Do this at the end, to catch resps.
                        if isinstance(value, str):
                            value = " ¶ ".join(line.strip() for line in value.splitlines())
                        row[key] = value if value is not None else NONE_STR
                    except Exception as e:
                        if "open_ended" not in key and "yes_no" not in key:
                            print(f"Error in {filename}, entry {entry_idx}:")
                            print(f"  Key: {key}")
                            print(f"  Value: {value}")
                            print(f"  Error: {str(e)}")
                            skipped_entries += 1
                            # Skip this entry entirely
                            break
                        row[key] = "None"
                        # Continue processing other keys
                        continue
                
                # This happens after all keys have been processed
                # Assert that there are no unescaped new lines in the row
                for k, v in row.items():
                    assert v is not str or "\n" not in v, f"Newline found in {k}: {v}"

                writer.writerow(row)
                csvfile.flush()

                rows_written += 1
                if rows_written % 100 == 0:
                    print(f"Wrote {rows_written} rows...")

                # Check if line count increased by exactly 1
                with open(output_file, 'r', encoding='utf-8') as f:
                    current_lines = sum(1 for _ in f)
                if current_lines != prev_line_count + 1 and rows_written > 1:  # Skip first row
                    print(f"ERROR: Line count changed from {prev_line_count} to {current_lines}")
                    print("Contents of row:")
                    print(row)
        
        print("\nDebug Statistics:")
        print(f"Rows written (counted): {rows_written}")
        
        # Check CSV file directly
        with open(output_file, 'r', encoding='utf-8') as f:
            actual_lines = sum(1 for _ in f)
        print(f"Actual lines in CSV file: {actual_lines}")
        
        return total_entries, processed_entries, skipped_entries


def main():
    args = parse_args()
    
    # Load matching files
    results = load_jsonl_files(args.pattern, args.base_dir, args.in_past_hours)
    
    # Print stats
    print(f"\nFound {len(results)} files matching pattern '{args.pattern}':")
    for file, data in results.items():
        print(f"{file}: {len(data)} samples")

    print(f"Total entries: {sum(len(data) for data in results.values())}")
    
    # Write results to CSV
    total_entries, processed_entries, skipped_entries = write_to_csv(results, args.output)
    print(f"\nWrote results to: {args.output}")
    print(f"Total entries: {total_entries}")
    print(f"Processed entries: {processed_entries}")
    print(f"Skipped entries: {skipped_entries}")
    print(f"Written entries: {processed_entries - skipped_entries}")


if __name__ == "__main__":
    main()
