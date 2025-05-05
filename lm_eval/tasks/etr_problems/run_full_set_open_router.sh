#!/bin/bash
set -o pipefail

# Source project-specific API keys
source "$(dirname "$0")/source_keys.sh"

# Verify required API keys are available
if [ -z "$OPENROUTER_API_KEY" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo "Error: Required API keys are missing"
    echo "Please ensure both OPENROUTER_API_KEY and OPENAI_API_KEY are set in keys.env"
    exit 1
fi

# Define OpenRouter model configurations
declare -A MODELS=(
# Batch 3
    # High ELO
    ["deepseek/deepseek-r1"]="DeepSeek-R1"
    ["nvidia/llama-3.3-nemotron-super-49b-v1"]="Llama-3.3-Nemotron-Super-49B-v1"
    ["x-ai/grok-2"]="Grok-2-08-13"
    # Upper-Mid ELO
    ["microsoft/phi-4"]="Phi-4"
    ["meta-llama/llama-3.1-70b-instruct"]="Llama-3.1-70B-Instruct"
    # Mid ELO
    ["anthropic/claude-3-haiku"]="Claude 3 Haiku"
    ["01-ai/yi-1.5-34b-chat"]="Yi-1.5-34B-Chat"
    ["mistralai/mixtral-8x22b-instruct"]="Mixtral-8x22b-Instruct-v0.1"
    ["anthropic/claude-2.0"]="Claude-2.0"
    # Lower-Mid ELO
    ["mistralai/mixtral-8x7b-instruct"]="Mixtral-8x7B-Instruct-v0.1"
    ["anthropic/claude-instant-1"]="Claude-Instant-1"
    ["snowflake/snowflake-arctic-instruct"]="Snowflake Arctic Instruct"
    ["mistralai/mistral-7b-instruct-v0.2"]="Mistral-7B-Instruct-v0.2"
    ["meta-llama/llama-2-7b-chat"]="Llama-2-7B-chat"
    # Low ELO
    ["allenai/olmo-7b-instruct"]="OLMo-7B-instruct"
    ["qwen/qwen-4b-chat"]="Qwen1.5-4B-Chat"
    ["mosaicml/mpt-7b-chat"]="MPT-7B-Chat"
    ["thudm/chatglm2-6b"]="ChatGLM2-6B"
    ["OpenAssistant/pythia-12b-sft-v8-7k-steps"]="OpenAssistant-Pythia-12B"
    ["databricks/dolly-v2-12b"]="Dolly-V2-12B"

## Comprehensive List of OpenRouter models with known Arena Scores, see discussion here: https://claude.ai/share/b0fb4bf0-b85d-4137-ac7c-31f797a30883
#    ["openai/chatgpt-4o-latest"]="ChatGPT-4o-latest (2025-03-26)"
#    ["openai/gpt-4.5-preview"]="GPT-4.5-Preview"
#    ["google/gemini-2.5-flash-preview"]="Gemini-2.5-Flash-Preview-04-17"
#    ["deepseek/deepseek-chat-v3-0324"]="DeepSeek-V3-0324"
#    ["deepseek/deepseek-r1"]="DeepSeek-R1"
#    ["google/gemma-3-27b-it"]="Gemma-3-27B-it"
#    ["qwen/qwq-32b"]="QwQ-32B"
#    ["openai/o1-mini"]="o1-mini"
#    ["nvidia/llama-3.3-nemotron-super-49b-v1"]="Llama-3.3-Nemotron-Super-49B-v1"
#    ["anthropic/claude-3.7-sonnet"]="Claude 3.7 Sonnet"
#    ["x-ai/grok-2"]="Grok-2-08-13"
#    ["anthropic/claude-3.5-sonnet"]="Claude 3.5 Sonnet (20241022)"
#    ["openai/gpt-4o-mini-2024-07-18"]="GPT-4o-mini-2024-07-18"
#    ["google/gemini-1.5-flash"]="Gemini-1.5-Flash-002"
#    ["nvidia/llama-3.1-nemotron-70b-instruct"]="Llama-3.1-Nemotron-70B-Instruct"
#    ["deepseek/deepseek-chat"]="DeepSeek-V3"
#    ["mistralai/mistral-large-2407"]="Mistral-Large-2407"
#    ["meta-llama/llama-3.1-70b-instruct"]="Llama-3.1-70B-Instruct"
#    ["anthropic/claude-3-opus"]="Claude 3 Opus"
#    ["mistralai/mistral-small-24b-instruct-2501"]="Mistral-Small-24B-Instruct-2501"
#    ["anthropic/claude-3-sonnet"]="Claude 3 Sonnet"
#    ["microsoft/phi-4"]="Phi-4"
#    ["anthropic/claude-3-haiku"]="Claude 3 Haiku"
#    ["openai/gpt-4-0314"]="GPT-4-0314"
#    ["openai/gpt-4"]="GPT-4-0613"
#    ["01-ai/yi-1.5-34b-chat"]="Yi-1.5-34B-Chat"
#    ["meta-llama/llama-3-8b-instruct"]="Llama-3-8B-Instruct"
#    ["anthropic/claude-1"]="Claude-1"
#    ["cohere/command-r-04-2024"]="Command R (04-2024)"
#    ["mistralai/mixtral-8x22b-instruct"]="Mixtral-8x22b-Instruct-v0.1"
#    ["mistralai/mistral-medium"]="Mistral Medium"
#    ["qwen/qwen-72b-chat"]="Qwen1.5-72B-Chat"
#    ["anthropic/claude-2.0"]="Claude-2.0"
#    ["qwen/qwen-32b-chat"]="Qwen1.5-32B-Chat"
#    ["microsoft/phi-3-medium-4k-instruct"]="Phi-3-Medium-4k-Instruct"
#    ["anthropic/claude-2.1"]="Claude-2.1"
#    ["mistralai/mixtral-8x7b-instruct"]="Mixtral-8x7B-Instruct-v0.1"
#    ["qwen/qwen-14b-chat"]="Qwen1.5-14B-Chat"
#    ["01-ai/yi-34b-chat"]="Yi-34B-Chat"
#    ["anthropic/claude-instant-1"]="Claude-Instant-1"
#    ["openai/gpt-3.5-turbo-0613"]="GPT-3.5-Turbo-0613"
#    ["openai/gpt-3.5-turbo-0125"]="GPT-3.5-Turbo-0125"
#    ["databricks/dbrx-instruct"]="DBRX-Instruct-Preview"
#    ["meta-llama/llama-3.2-3b-instruct"]="Meta-Llama-3.2-3B-Instruct"
#    ["microsoft/phi-3-mini-128k-instruct"]="Phi-3-Small-8k-Instruct"
#    ["snowflake/snowflake-arctic-instruct"]="Snowflake Arctic Instruct"
#    ["google/gemma-7b-it"]="Gemma-1.1-7B-it"
#    ["nousresearch/nous-hermes-2-mixtral-8x7b-dpo"]="Nous-Hermes-2-Mixtral-8x7B-DPO"
#    ["teknium/openhermes-2.5-mistral-7b"]="OpenHermes-2.5-Mistral-7B"
#    ["mistralai/mistral-7b-instruct-v0.2"]="Mistral-7B-Instruct-v0.2"
#    ["qwen/qwen-7b-chat"]="Qwen1.5-7B-Chat"
#    ["openai/gpt-3.5-turbo-1106"]="GPT-3.5-Turbo-1106"
#    ["meta-llama/llama-2-13b-chat"]="Llama-2-13b-chat"
#    ["meta-llama/llama-3.2-1b-instruct"]="Meta-Llama-3.2-1B-Instruct"
#    ["huggingfaceh4/zephyr-7b-beta"]="Zephyr-7B-beta"
#    ["meta-llama/codellama-34b-instruct"]="CodeLlama-34B-instruct"
#    ["meta-llama/codellama-70b-instruct"]="CodeLlama-70B-instruct"
#    ["lmsys/vicuna-13b"]="Vicuna-13B"
#    ["google/gemma-7b-it"]="Gemma-7B-it"
#    ["meta-llama/llama-2-7b-chat"]="Llama-2-7B-chat"
#    ["qwen/qwen-14b-chat"]="Qwen-14B-Chat"
#    ["google/gemma-2b-it"]="Gemma-1.1-2b-it"
#    ["togethercomputer/stripedhyena-nous-7b"]="StripedHyena-Nous-7B"
#    ["allenai/olmo-7b-instruct"]="OLMo-7B-instruct"
#    ["mistralai/mistral-7b-instruct-v0.1"]="Mistral-7B-Instruct-v0.1"
#    ["lmsys/vicuna-7b"]="Vicuna-7B"
#    ["google/palm-2-chat-bison"]="PaLM-Chat-Bison-001"
#    ["qwen/qwen-4b-chat"]="Qwen1.5-4B-Chat"
#    ["mosaicml/mpt-7b-chat"]="MPT-7B-Chat"
#    ["thudm/chatglm2-6b"]="ChatGLM2-6B"
#    ["rwkv/rwkv-5-world-3b"]="RWKV-4-Raven-14B"
#    ["OpenAssistant/pythia-12b-sft-v8-7k-steps"]="OpenAssistant-Pythia-12B"
#    ["thudm/chatglm-6b"]="ChatGLM-6B"
#    ["databricks/dolly-v2-12b"]="Dolly-V2-12B"
#    ["meta-llama/llama-13b"]="LLaMA-13B"

##    # Batch 2
#     ["openai/gpt-4.5-preview"]="GPT-4.5 Preview"
#     ["anthropic/claude-3.7-sonnet"]="Claude 3.7 Sonnet"
#     ["meta-llama/llama-3.2-1b-instruct"]="Llama-3.2 1B Instruct"

#    # Batch 1
#    ["openai/chatgpt-4o-latest"]="ChatGPT-4o-latest"      #
#    ["google/gemini-2.5-flash-preview"]="Gemini 2.5 Flash"   #
#    ["google/gemma-3-27b-it"]="Gemma 3 27B"
#    ["anthropic/claude-3.5-sonnet"]="Claude 3.5 Sonnet"  #
#    ["anthropic/claude-3-opus"]="Claude 3 Opus" #
#    ["google/gemma-2-9b-it"]="Gemma 2 9B" #
#    ["openai/gpt-3.5-turbo-1106"]="GPT-3.5-Turbo-1106" #
#    ["meta-llama/llama-3.2-1b-instruct"]="Llama-3.2 1B" #
#    ["meta-llama/llama-2-13b-chat"]="Llama-13B" #

    # Problems with these, they seem to not exist
#    ["google/gemini-2.5-pro-preview-03-25"]="Gemini 2.5 Pro" # Many of its responses are empty string
#    ["openai/gpt-4-0125-preview"]="GPT-4 (0125)" # DNE
#    ["openai/gpt-4-0613"]="GPT-4-0613" # DNE
#    ["thudm/chatglm-6b"]="ChatGLM 6B" # DNE
)

# Dataset paths
DATASETS=(
#    "/home/keenan/Dev/etr_case_generator/datasets/smallset_open_ended.jsonl"
    "/home/keenan/Dev/etr_case_generator/datasets/largeset_open_ended.jsonl"
#    "/home/keenan/Dev/etr_case_generator/datasets/250302/multiview_open_ended.jsonl"
#    "/home/keenan/Dev/etr_case_generator/datasets/fully_balanced_yes_no.jsonl"
)

# Create a log directory
LOG_DIR="evaluation_logs"
mkdir -p "$LOG_DIR"

# Function to run evaluation for a model
run_evaluation() {
    local model="$1"
    local model_name="$2"
    local dataset="$3"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local dataset_type=$(basename "$dataset" | sed 's/multiview_\(.*\)\.jsonl/\1/')
    local log_file="${LOG_DIR}/openrouter_${model_name}_${dataset_type}_${timestamp}.log"
    
    echo "Running evaluation for OpenRouter model: ${model_name} (${model}) on ${dataset_type}"
    echo "Logging to: ${log_file}"
    
    # Run the evaluation command and tee output to both terminal and log file
    ./lm_eval/tasks/etr_problems/run_evaluation_open_router.sh \
        --dataset "$dataset" \
        -m "$model" \
        --good 2>&1 | tee "$log_file"
    
    # Need to check the exit status of the evaluation command, not tee
    # This uses bash's pipefail option to get the first command's status
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✓ Evaluation completed successfully for ${model_name} on ${dataset_type}"
    else
        echo "✗ Evaluation failed for ${model_name} on ${dataset_type}. Check ${log_file} for details"
    fi
}

# Iterate through models
for model in "${!MODELS[@]}"; do
    model_name="${MODELS[$model]}"
    for dataset in "${DATASETS[@]}"; do
        run_evaluation "$model" "$model_name" "$dataset"
    done
done

echo "All evaluations completed. Logs are available in ${LOG_DIR}/"
