
# Model classes (-c): MODEL_CLASS="openai-chat-completions"  # Supported model names: local-completions, local-chat-completions, openai-completions, openai-chat-completions, anthropic-completions, anthropic-chat, anthropic-chat-completions, dummy, gguf, ggml, hf-auto, hf, huggingface, hf-multimodal, watsonx_llm, mamba_ssm, nemo_lm, sparseml, deepsparse, neuronx, openvino, textsynth, vllm, vllm-vlm

# TODO: Iterate through these -m models:
# anthropic-chat-completions -- claude-3-haiku-20240307, claude-3-sonnet-20240229, claude-3-5-haiku-20241022, claude-3-opus-20240229
# openai-chat-completions -- gpt-3.5-turbo-0125, gpt-4o-mini, gpt-4-turbo


# TODO Iterate through pairs of model_class and model, running the command for each
# TODO Make sure the command is run in a way that won't crash this script if it crashes
# Command
lm_eval/tasks/etr_problems/run_evaluation.sh --dataset /home/keenan/Dev/etr_case_generator/datasets/balance_atoms_open_ended.jsonl -c anthropic-chat-completions -m claude-3-5-haiku-20241022 --good