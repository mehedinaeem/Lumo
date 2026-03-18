"""
Lumo - Text-to-Speech Test Script
Tests Piper TTS engine with sample text
"""
import subprocess
import os
import winsound
import sys

# TTS Configuration
PIPER_PATH = "piper\\piper\\piper.exe"
MODEL_PATH = "models\\tts\\en_US-amy-medium.onnx"
OUTPUT_FILE = "test_output.wav"

def check_requirements():
    """Check if TTS requirements are met"""
    if not os.path.exists(PIPER_PATH):
        print(f"❌ Piper executable not found at: {PIPER_PATH}")
        return False
    
    if not os.path.exists(MODEL_PATH):
        print(f"❌ TTS model not found at: {MODEL_PATH}")
        print("\n📥 To download the voice model:")
        print("   1. Go to: https://github.com/rhasspy/piper/releases")
        print("   2. Download: en_US-amy-medium.onnx")
        print("   3. Also download: en_US-amy-medium.onnx.json")
        print(f"   4. Place both files in: {os.path.abspath('models/tts/')}")
        print("\n   Or run this command:")
        print("   curl -L -o models/tts/en_US-amy-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx")
        print("   curl -L -o models/tts/en_US-amy-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json")
        return False
    
    print("✅ All requirements met!")
    return True

def speak(text):
    """Convert text to speech and play it"""
    print(f"📝 Text: {text}")
    print("🔄 Generating speech...")
    
    # Sanitize text for shell safety
    safe_text = text.replace('"', '').replace("'", "").replace('\n', ' ').replace('&', 'and')
    
    output_path = os.path.abspath(OUTPUT_FILE)
    
    # Run Piper TTS
    result = subprocess.run(
        f'echo {safe_text} | {PIPER_PATH} --model {MODEL_PATH} --output_file "{output_path}" --quiet',
        shell=True,
        capture_output=True
    )
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr.decode()}")
        return False
    
    print("✅ Speech generated!")
    print(f"📁 Output: {output_path}")
    print("🔊 Playing audio...")
    
    # Play the audio
    try:
        winsound.PlaySound(output_path, winsound.SND_FILENAME)
        print("✅ Playback complete!")
        return True
    except Exception as e:
        print(f"❌ Playback error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("  🔊 LUMO - Text-to-Speech Test")
    print("="*50 + "\n")
    
    # Check requirements first
    if not check_requirements():
        print("\n❌ Please install missing requirements and try again.")
        sys.exit(1)
    
    # Interactive mode
    print("\n" + "="*50)
    print("  💬 Interactive Mode (type 'exit' to quit)")
    print("="*50)
    
    while True:
        try:
            user_text = input("\nEnter text to speak: ").strip()
            if user_text.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break
            if user_text:
                speak(user_text)
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
