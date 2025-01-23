
#!/bin/bash

# Define model configurations
declare -A MODEL_CONFIGS=(
    ["openai-chat-completions"]="gpt-3.5-turbo-0125 gpt-4-turbo"
    ["anthropic-chat-completions"]="claude-3-haiku-20240307 claude-3-sonnet-20240229 claude-3-5-haiku-20241022 claude-3-opus-20240229"
)

# Dataset path
DATASET="/home/keenan/Dev/etr_case_generator/datasets/balance_atoms_open_ended.jsonl"

# Create a log directory
LOG_DIR="evaluation_logs"
mkdir -p "$LOG_DIR"

# Function to run evaluation for a model
run_evaluation() {
    local model_class="$1"
    local model="$2"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local log_file="${LOG_DIR}/${model_class}_${model}_${timestamp}.log"
    
    echo "Running evaluation for ${model_class} - ${model}"
    echo "Logging to: ${log_file}"
    
    # Run the evaluation command and redirect output to log file
    ./lm_eval/tasks/etr_problems/run_evaluation.sh \
        --dataset "$DATASET" \
        -c "$model_class" \
        -m "$model" \
        --good > "$log_file" 2>&1
    
    # Check if the command succeeded
    if [ $? -eq 0 ]; then
        echo "✓ Evaluation completed successfully for ${model_class} - ${model}"
    else
        echo "✗ Evaluation failed for ${model_class} - ${model}. Check ${log_file} for details"
    fi
}

# Iterate through model configurations
for model_class in "${!MODEL_CONFIGS[@]}"; do
    # Get the models for this class and split them into an array
    IFS=' ' read -r -a models <<< "${MODEL_CONFIGS[$model_class]}"
    
    for model in "${models[@]}"; do
        run_evaluation "$model_class" "$model"
    done
done

echo "All evaluations completed. Logs are available in ${LOG_DIR}/"
