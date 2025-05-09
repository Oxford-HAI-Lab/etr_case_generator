
#!/bin/bash
set -o pipefail

# Source project-specific API keys
source "$(dirname "$0")/source_keys.sh"

# Verify required API key is available
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: OPENAI_API_KEY is missing"
    echo "Please ensure OPENAI_API_KEY is set in keys.env"
    exit 1
fi

# Define model configurations
# Note that "deepseek" has some special handling in run_evaluation.sh
declare -A MODEL_CONFIGS=(
    ["openai-chat-completions"]="gpt-3.5-turbo-0125 \
                                gpt-4o-mini \
                                gpt-4-turbo"
    ["anthropic-chat-completions"]="claude-3-5-haiku-20241022 \
                                  claude-3-opus-20240229 \
                                  claude-3-5-sonnet-20241022 \
                                  claude-3-haiku-20240307"
    ["deepseek"]="deepseek-r1"
)
# Other models: claude-3-haiku-20240307, claude-3-sonnet-20240229

# Dataset paths
# TODO NOTE: !!! Also change the regex in run_evaluation !!!
DATASETS=(
    "/home/keenan/Dev/etr_case_generator/datasets/250302/multiview_open_ended.jsonl"
#    "/home/keenan/Dev/etr_case_generator/datasets/fully_balanced_yes_no.jsonl"
)

# Create a log directory
LOG_DIR="evaluation_logs"
mkdir -p "$LOG_DIR"

# Function to run evaluation for a model
run_evaluation() {
    local model_class="$1"
    local model="$2"
    local dataset="$3"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local dataset_type=$(basename "$dataset" | sed 's/multiview_\(.*\)\.jsonl/\1/')  # TODO Change me! If you changed the DATASETS.
    local log_file="${LOG_DIR}/${model_class}_${model}_${dataset_type}_${timestamp}.log"
    
    echo "Running evaluation for ${model_class} - ${model} on ${dataset_type}"
    echo "Logging to: ${log_file}"
    
    # Run the evaluation command and tee output to both terminal and log file
    ./scripts/run_evaluation.sh \
        --dataset "$dataset" \
        -c "$model_class" \
        -m "$model" \
        --good 2>&1 | tee "$log_file"
    
    # Need to check the exit status of the evaluation command, not tee
    # This uses bash's pipefail option to get the first command's status
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✓ Evaluation completed successfully for ${model_class} - ${model} on ${dataset_type}"
    else
        echo "✗ Evaluation failed for ${model_class} - ${model} on ${dataset_type}. Check ${log_file} for details"
    fi
}

# Iterate through model configurations
for model_class in "${!MODEL_CONFIGS[@]}"; do
    # Get the models for this class and split them into an array
    IFS=' ' read -r -a models <<< "${MODEL_CONFIGS[$model_class]}"
    
    for model in "${models[@]}"; do
        for dataset in "${DATASETS[@]}"; do
            run_evaluation "$model_class" "$model" "$dataset"
        done
    done
done

echo "All evaluations completed. Logs are available in ${LOG_DIR}/"
