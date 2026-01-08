import sounddevice as sd
import queue, json, subprocess, time, winsound, os
from vosk import Model, KaldiRecognizer
from gpt4all import GPT4All

RATE = 16000
audio_q = queue.Queue()
is_speaking = False  # Flag to prevent feedback loop

def audio_callback(indata, frames, time_info, status):
    if not is_speaking:  # Only capture audio when not speaking
        audio_q.put(bytes(indata))

# STT
model = Model("models/stt/vosk-model-small-en-us-0.15")
rec = KaldiRecognizer(model, RATE)

# LLM - using local GGUF model for offline operation
llm = GPT4All(
    model_name="orca-mini-3b-gguf2-q4_0.gguf",
    model_path="models/llm",  # Local path to model
    allow_download=False      # Prevent internet access
)

# Conversation history for context
conversation_history = []

def speak(text):
    global is_speaking
    is_speaking = True
    
    # Clear the audio queue to prevent feedback
    while not audio_q.empty():
        try:
            audio_q.get_nowait()
        except:
            pass
    
    # Escape special characters for shell safety
    safe_text = text.replace('"', '').replace("'", "").replace('\n', ' ').replace('&', 'and')
    
    output_path = os.path.abspath("output.wav")
    
    result = subprocess.run(
        f'echo {safe_text} | piper\\piper\\piper.exe '
        f'--model models\\tts\\en_US-amy-medium.onnx '
        f'--output_file "{output_path}" --quiet',
        shell=True,
        capture_output=True
    )
    
    # Play audio SYNCHRONOUSLY using winsound (blocks until done)
    try:
        winsound.PlaySound(output_path, winsound.SND_FILENAME)
    except:
        pass
    
    # Wait a bit after speaking ends
    time.sleep(0.8)
    
    # Clear audio queue again before resuming listening
    while not audio_q.empty():
        try:
            audio_q.get_nowait()
        except:
            pass
    
    # Reset the recognizer to clear any buffered audio
    rec.Reset()
    
    is_speaking = False

print("[*] LUMO is listening... (say 'exit' or 'quit' to stop)")

with sd.RawInputStream(
    samplerate=RATE, blocksize=8000,
    dtype='int16', channels=1, callback=audio_callback
):
    while True:
        if is_speaking:
            time.sleep(0.1)
            continue
            
        data = audio_q.get()
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "").strip()
            
            if not text:
                continue
            
            # Skip if the text is too short (likely noise)
            if len(text) < 3:
                continue
                
            # Exit command
            if text.lower() in ["exit", "quit", "stop", "goodbye", "bye"]:
                print("Goodbye!")
                break
            
            print(f"You: {text}")
            
            # Build prompt with conversation context
            conversation_history.append(f"User: {text}")
            
            # Keep only last 4 exchanges for context
            recent_history = conversation_history[-4:]
            context = "\n".join(recent_history)
            
            prompt = f"""You are Lumo, a helpful offline AI assistant. 
Answer the user's question directly and helpfully. Be concise (under 50 words).

{context}
Lumo:"""
            
            reply = llm.generate(prompt, max_tokens=80)
            reply = reply.strip()
            
            # Store response in history
            conversation_history.append(f"Lumo: {reply}")
            
            print(f"Lumo: {reply}")
            speak(reply)
