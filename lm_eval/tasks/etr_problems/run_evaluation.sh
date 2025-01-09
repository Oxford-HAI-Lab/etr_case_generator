#!/bin/bash

# Help text function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "Run ETR problems evaluation with specified parameters."
    echo
    echo "Options:"
    echo "  -m, --model MODEL      Model to use (default: gpt-4-turbo)"
    echo "  -p, --path PATH        Path to lm-evaluation-harness directory"
    echo "  -i, --include PATH     Path to include for task definitions"
    echo "  -d, --dataset PATH     Path to dataset JSONL file to evaluate"
    echo "  -v, --verbosity LEVEL  Verbosity level (default: WARNING)"
    echo "  -h, --help            Show this help message"
    echo
    echo "Example:"
    echo "  $0 -m gpt-4-turbo -p /path/to/lm-evaluation-harness"
}

# Default values
MODEL_CLASS="openai-chat-completions"
MODEL="gpt-4-turbo"
EVAL_PATH="/home/keenan/Dev/lm-evaluation-harness/"
INCLUDE_PATH="/home/keenan/Dev/etr_case_generator/"
DATASET=""
TASK="etr_problems"
VERBOSITY="WARNING"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -p|--path)
            EVAL_PATH="$2"
            shift 2
            ;;
        -i|--include)
            INCLUDE_PATH="$2"
            shift 2
            ;;
        -d|--dataset)
            DATASET="$2"
            shift 2
            ;;
        -v|--verbosity)
            VERBOSITY="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Handle dataset routing if specified
if [ -n "$DATASET" ]; then
    if [[ $DATASET == *"yes_no"* ]]; then
        TASK="etr_problems"
    elif [[ $DATASET == *"open_ended"* ]]; then
        TASK="etr_problems_open_ended"
    elif [[ $DATASET == *"multiple_choice"* ]]; then
        echo "Error: multiple-choice questions are not yet implemented"
        exit 1
    else
        echo "Warning: Dataset filename does not contain 'yes_no', 'open_ended', or 'multiple_choice'"
        echo "Defaulting to yes/no questions task configuration"
        TASK="etr_problems"
    fi

    # Copy dataset to the root datasets directory
    mkdir -p "datasets"
    cp "$DATASET" "datasets/etr_for_lm_eval.jsonl"
    echo "Copied $DATASET to datasets/etr_for_lm_eval.jsonl"
fi

# Assert that EVAL_PATH is a real directory
if [ ! -d "$EVAL_PATH" ]; then
    echo "Error: $EVAL_PATH is not a valid directory, please rerun with the '--path' option. Sorry for hardcoding my own."
    exit 1
fi

# Assert that INCLUDE_PATH is a real directory
if [ ! -d "$INCLUDE_PATH" ]; then
    echo "Error: $INCLUDE_PATH is not a valid directory, please rerun with the '--include' option. Sorry for hardcoding my own."
    exit 1
fi

# Export PYTHONPATH if needed
if [ -n "$EVAL_PATH" ]; then
    export PYTHONPATH="${EVAL_PATH}:${PYTHONPATH:+:$PYTHONPATH}"
fi

echo "Configuration:"
echo "  Model Class: $MODEL_CLASS"
echo "  Model: $MODEL"
echo "  Evaluation harness path: $EVAL_PATH"
echo "  Include path: $INCLUDE_PATH"
echo "  Task: $TASK"
echo ""

# Run evaluation
lm_eval --model $MODEL_CLASS \
    --model_args model=$MODEL \
    --include_path "$INCLUDE_PATH" \
    --tasks $TASK \
    --num_fewshot 0 \
    --batch_size 1 \
    --output_path lm_eval/tasks/etr_problems/results \
    --apply_chat_template \
    --log_samples \
    --write_out \
    ${VERBOSITY:+--verbosity "$VERBOSITY"}

# Uncomment to use Anthropic's Claude model instead
# TODO Make this an argument
#lm_eval --model anthropic-chat-completions \
#    --model_args model=claude-3-5-sonnet-20240620 \
