"""
Lumo - Text-based Chat Interface
A simple offline text conversation with the local LLM model.
"""
from gpt4all import GPT4All
import sys
import threading
import time
import itertools

class Spinner:
    """Professional loading spinner for processing indication."""
    def __init__(self, message="Processing"):
        self.message = message
        self.running = False
        self.thread = None
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def spin(self):
        for frame in itertools.cycle(self.frames):
            if not self.running:
                break
            sys.stdout.write(f"\r{frame} {self.message}...")
            sys.stdout.flush()
            time.sleep(0.1)
    
    def start(self, message=None):
        if message:
            self.message = message
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r" + " " * 50 + "\r")  # Clear spinner line
        sys.stdout.flush()

# Initialize spinner
spinner = Spinner()

print("\n" + "="*50)
print("  🤖 LUMO - Offline AI Chat")
print("="*50)

# Loading LLM
spinner.start("Loading LLM model")
llm = GPT4All(
    model_name="orca-mini-3b-gguf2-q4_0.gguf",
    model_path="models/llm",
    allow_download=False
)
spinner.stop()

print("✅ Model loaded: orca-mini-3b-gguf2-q4_0.gguf")
print("📁 Path: models/llm/")
print("\n💡 Type 'exit' or 'quit' to end the conversation")
print("="*50 + "\n")

# Conversation history for context
conversation_history = []

while True:
    try:
        # Get user input
        user_input = input("You: ").strip()
        
        # Exit conditions
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
            print("\n👋 Goodbye! Have a great day!")
            break
        
        # Add to conversation history
        conversation_history.append(f"User: {user_input}")
        
        # Keep only last 2 exchanges for faster context
        recent_history = conversation_history[-2:]
        context = "\n".join(recent_history)
        
        # Build prompt
        prompt = f"""You are Lumo, a helpful and knowledgeable AI assistant.
Provide detailed, thorough, and informative responses. Explain concepts clearly with examples when helpful.

{context}
Lumo:"""
        
        # Show processing spinner
        spinner.start("Lumo is thinking")
        response = llm.generate(prompt, max_tokens=2000)
        response = response.strip()
        spinner.stop()
        
        # Store response in history
        conversation_history.append(f"Lumo: {response}")
        
        # Display response with typing effect
        print(f"Lumo: {response}\n")
        
    except KeyboardInterrupt:
        spinner.stop()
        print("\n\n👋 Goodbye! Have a great day!")
        break
