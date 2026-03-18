# 🤖 LUMO - Offline AI Voice & Chat Assistant

A fully **offline AI assistant** for Windows that combines Speech-to-Text, a Local LLM, and Text-to-Speech for voice interactions, plus a text-based chat interface.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🔇 **100% Offline** - No internet required after setup
- 🎤 **Voice Assistant** - Speak and get spoken responses
- 💬 **Text Chat** - Type-based conversation interface
- 🧠 **Conversation Memory** - Remembers context across exchanges
- ⚡ **Fast Response** - Optimized for CPU inference

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        LUMO                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│   │   STT   │───▶│   LLM   │───▶│   TTS   │                │
│   │  VOSK   │    │ GPT4All │    │  Piper  │                │
│   └─────────┘    └─────────┘    └─────────┘                │
│        │              │              │                      │
│   Microphone     Local Model    Speaker                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Components

### 1. Speech-to-Text (STT) - VOSK
| Property | Value |
|----------|-------|
| Library | [VOSK](https://alphacephei.com/vosk/) |
| Model | `vosk-model-small-en-us-0.15` |
| Path | `models/stt/vosk-model-small-en-us-0.15/` |
| Sample Rate | 16000 Hz |

### 2. Large Language Model (LLM) - GPT4All
| Property | Value |
|----------|-------|
| Library | [GPT4All](https://gpt4all.io/) |
| Model | `orca-mini-3b-gguf2-q4_0.gguf` |
| Path | `models/llm/orca-mini-3b-gguf2-q4_0.gguf` |
| Size | ~1.9 GB |
| Quantization | Q4_0 (4-bit) |

### 3. Text-to-Speech (TTS) - Piper
| Property | Value |
|----------|-------|
| Library | [Piper](https://github.com/rhasspy/piper) |
| Voice | `en_US-amy-medium` |
| Path | `models/tts/en_US-amy-medium.onnx` |
| Format | ONNX |

---

## 📁 Project Structure

```
Lumo/
├── main.py              # 🎤 Voice assistant (STT + LLM + TTS)
├── chat.py              # 💬 Text chat interface
├── bangla_tts.py        # 🗣️ Bangla TTS script
├── debug_main.py        # 🔧 Debug version with verbose logging
├── requirements.txt     # 📦 Project dependencies
│
├── dataset/             # 🗃️ Speech evaluation datasets and metadata
│   ├── metadata.csv     # 📊 Dataset transcriptions and structure
│   ├── english/         # 🇬🇧 English audio files
│   └── bangla/          # 🇧🇩 Bangla audio files
│
├── tests/               # 🧪 Testing and evaluation scripts
│   ├── test_llm.py
│   ├── test_stt.py
│   ├── test_tts.py
│   ├── test_bangla_stt.py
│   └── test_bangla_tts.py
│
├── models/
│   ├── llm/
│   │   └── orca-mini-3b-gguf2-q4_0.gguf   # Local LLM (1.9GB)
│   ├── stt/
│   │   └── vosk-model-small-en-us-0.15/   # Speech recognition
│   └── tts/
│       ├── en_US-amy-medium.onnx          # Voice model
│       └── en_US-amy-medium.onnx.json     # Voice config
│
├── piper/
│   └── piper/
│       └── piper.exe    # TTS executable
│
└── venv/                # Python virtual environment
```

---

## 🚀 Usage

### Voice Assistant
```bash
python main.py
```
- Speak into your microphone
- Say "exit", "quit", "goodbye" to stop

### Text Chat
```bash
python chat.py
```
- Type your messages
- Type "exit" or "quit" to stop

---

## 🧪 Evaluation & Testing

For paper reviewers and researchers interested in reproducing the pipeline or testing individual components:
The test scripts have been placed in the `tests/` directory. You can run them from the root of the repository.

1. **Test STT (Speech-to-Text)**:
```bash
python tests/test_stt.py
```
2. **Test Bangla STT explicitly**:
```bash
python tests/test_bangla_stt.py
```
3. **Test LLM (Local Text Generation)**:
```bash
python tests/test_llm.py
```
4. **Test TTS (Text-to-Speech)**:
```bash
python tests/test_tts.py
```

---

## 📜 Scripts Detail

### `main.py` - Voice Assistant

```python
# Key components:
from vosk import Model, KaldiRecognizer  # Speech-to-Text
from gpt4all import GPT4All              # Local LLM
import winsound                          # Audio playback
import subprocess                        # Piper TTS
```

**Flow:**
1. Captures audio via `sounddevice` at 16kHz
2. Transcribes with VOSK recognizer
3. Generates response with GPT4All (max 80 tokens)
4. Speaks using Piper TTS → `output.wav` → `winsound`

**Features:**
- Feedback prevention (stops listening while speaking)
- Conversation history (last 4 exchanges)
- Audio queue management

---

### `chat.py` - Text Interface

```python
# Key components:
from gpt4all import GPT4All  # Local LLM
import threading             # Async spinner
```

**Features:**
- Professional animated spinner during processing
- Conversation memory (last 2 exchanges for speed)
- Concise responses (max 80 tokens)

**Spinner Animation:**
```python
frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
```

---

## ⚙️ Configuration

### LLM Settings (in both main.py and chat.py)
```python
llm = GPT4All(
    model_name="orca-mini-3b-gguf2-q4_0.gguf",
    model_path="models/llm",
    allow_download=False  # Ensures offline operation
)
```

### Response Generation
```python
response = llm.generate(prompt, max_tokens=80)
```

---

## 📋 Requirements

### Python Packages
```
gpt4all
vosk
sounddevice
```

### System Requirements
- Windows 10/11
- Python 3.10+
- Microphone (for voice mode)
- ~4GB RAM recommended

---

## 🔧 Troubleshooting

### CUDA DLL Warnings
```
Failed to load llamamodel-mainline-cuda.dll
```
**This is normal!** It means GPU acceleration isn't available, so it runs on CPU instead.

### Model Not Found
Ensure the GGUF file exists at:
```
models/llm/orca-mini-3b-gguf2-q4_0.gguf
```

---

## 📝 License

MIT License - Feel free to use and modify!

---

## 🙏 Credits

- [GPT4All](https://gpt4all.io/) - Local LLM inference
- [VOSK](https://alphacephei.com/vosk/) - Offline speech recognition
- [Piper](https://github.com/rhasspy/piper) - Neural text-to-speech
- [Orca Mini](https://huggingface.co/psmathur/orca_mini_3b) - Base LLM model
