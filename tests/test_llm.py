from gpt4all import GPT4All

# LLM - using local GGUF model for offline operation
llm = GPT4All(
    model_name="orca-mini-3b-gguf2-q4_0.gguf",
    model_path="models/llm",
    allow_download=False
)

print(llm.generate(
    "You are Lumo, an offline assistant. Explain edge AI in one sentence.",
    max_tokens=60
))
