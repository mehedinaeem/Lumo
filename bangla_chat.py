"""
Lumo - বাংলা চ্যাট (Bangla Chat Interface)
A Bangla text-based conversation with the local LLM model.
Responds in Bangla when you speak/type in Bangla!

Features:
- Bangla text input
- LLM responds in Bangla
- Bangla Text-to-Speech output
"""

import sys
import os

# Fix Windows console encoding for Bangla text
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from gpt4all import GPT4All
import threading
import time
import itertools

# Import Bangla TTS
try:
    from bangla_tts import speak_bangla
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ Bangla TTS not available. Install with: pip install gtts pygame")


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


def is_bangla_text(text):
    """Check if the text contains Bangla characters"""
    for char in text:
        # Bangla Unicode range: U+0980 to U+09FF
        if '\u0980' <= char <= '\u09FF':
            return True
    return False


def is_greeting(text):
    """Check if the text is a greeting (English or Bangla)"""
    text_lower = text.lower().strip()
    
    # English greetings
    english_greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    for greeting in english_greetings:
        if text_lower == greeting or text_lower.startswith(greeting + " "):
            return True
    
    # Bangla greetings
    bangla_greetings = ["হ্যালো", "হাই", "হেই", "আসসালামু আলাইকুম", "সালাম", "নমস্কার", "শুভ সকাল", "শুভ বিকেল", "শুভ সন্ধ্যা"]
    for greeting in bangla_greetings:
        if greeting in text:
            return True
    
    return False


# Initialize spinner
spinner = Spinner()

print("\n" + "="*50)
print("  🤖 লুমো - বাংলা এ আই চ্যাট")
print("  🤖 LUMO - Bangla AI Chat")
print("="*50)

# Loading LLM
spinner.start("মডেল লোড হচ্ছে (Loading LLM)")
llm = GPT4All(
    model_name="orca-mini-3b-gguf2-q4_0.gguf",
    model_path="models/llm",
    allow_download=False
)
spinner.stop()

print("✅ মডেল লোড হয়েছে!")
print("📁 Path: models/llm/")

# Greeting messages
GREETING_BANGLA = "আমি লুমো, আপনার এ আই সহকারী। আজকে আমি কিভাবে আপনাকে সাহায্য করতে পারি?"
GREETING_ENGLISH = "Hello! I'm Lumo, your AI assistant. How can I help you today?"

# Display startup greeting
print(f"\n🤖 লুমো: {GREETING_BANGLA}")
print(f"\n💡 'exit' টাইপ করুন বন্ধ করতে (Type 'exit' to quit)")
print("="*50 + "\n")

# Conversation history for context
conversation_history = []

# Enable/Disable TTS
tts_enabled = True

while True:
    try:
        # Get user input
        user_input = input("আপনি (You): ").strip()
        
        # Exit conditions
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "bye", "goodbye", "বিদায়", "বাই"]:
            farewell = "বিদায়! আবার দেখা হবে!"
            print(f"\n👋 {farewell}")
            if TTS_AVAILABLE and tts_enabled:
                speak_bangla(farewell)
            break
        
        # Toggle TTS
        if user_input.lower() in ["tts on", "sound on"]:
            tts_enabled = True
            print("🔊 TTS enabled!")
            continue
        if user_input.lower() in ["tts off", "sound off"]:
            tts_enabled = False
            print("🔇 TTS disabled!")
            continue
        
        # Detect if input is Bangla
        is_bangla = is_bangla_text(user_input)
        
        # Check if it's a greeting
        if is_greeting(user_input):
            if is_bangla:
                response = GREETING_BANGLA
            else:
                response = GREETING_ENGLISH
        else:
            # Add to conversation history
            conversation_history.append(f"User: {user_input}")
            
            # Keep only last 2 exchanges for faster context
            recent_history = conversation_history[-2:]
            context = "\n".join(recent_history)
            
            # Build prompt based on language
            if is_bangla:
                prompt = f"""You are Lumo (লুমো), a helpful AI assistant. 
The user is speaking in Bangla (Bengali). You MUST respond ONLY in Bangla script (বাংলা).
Do NOT use any English words. Write everything in Bengali script.
Keep your response concise and helpful (under 100 words).

{context}
লুমো:"""
            else:
                prompt = f"""You are Lumo, a helpful and knowledgeable AI assistant.
Provide detailed, thorough, and informative responses. Explain concepts clearly.

{context}
Lumo:"""
            
            # Show processing spinner
            spinner.start("লুমো ভাবছে (Thinking)")
            response = llm.generate(prompt, max_tokens=500)
            response = response.strip()
            spinner.stop()
            
            # Store response in history
            conversation_history.append(f"Lumo: {response}")
        
        # Display response
        print(f"🤖 লুমো: {response}\n")
        
        # Speak the response if it's Bangla
        if TTS_AVAILABLE and tts_enabled and is_bangla_text(response):
            try:
                speak_bangla(response)
            except Exception as e:
                pass  # Silently skip TTS errors
        
    except KeyboardInterrupt:
        spinner.stop()
        print("\n\n👋 বিদায়! (Goodbye!)")
        break
