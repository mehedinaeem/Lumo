import os
import csv
import json
import wave
import time
from vosk import Model, KaldiRecognizer
import jiwer

dataset_dir = "dataset"
metadata_file = os.path.join(dataset_dir, "metadata.csv")

def evaluate_english():
    print("Loading English VOSK model...")
    model_path = "models/stt/vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Exiting.")
        return
        
    model = Model(model_path)
    
    true_texts = []
    pred_texts = []
    
    total_latency = 0
    count = 0

    print("Reading metadata.csv...")
    with open(metadata_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['language'] == 'english':
                # Reconstruct path. E.g. dataset/english/speaker01/eng_001.wav
                audio_path = os.path.join(dataset_dir, "english", row['speaker'], row['filename'])
                if not os.path.exists(audio_path):
                    continue
                
                try:
                    wf = wave.open(audio_path, "rb")
                    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                        print("Audio file must be WAV format mono PCM.")
                        wf.close()
                        continue
                        
                    rec = KaldiRecognizer(model, wf.getframerate())
                    
                    start_time = time.time()
                    while True:
                        data = wf.readframes(4000)
                        if len(data) == 0:
                            break
                        rec.AcceptWaveform(data)
                    
                    res = json.loads(rec.FinalResult())
                    end_time = time.time()
                except Exception as e:
                    print(f"Skipping bad file {audio_path}: {e}")
                    continue
                
                pred_text = res.get("text", "")
                true_text = row['transcript'].lower() # lowercase for WER
                
                true_texts.append(true_text)
                pred_texts.append(pred_text)
                
                total_latency += (end_time - start_time)
                count += 1
                
                if count % 10 == 0:
                    print(f"Processed {count} English phrases...")
    
    if count == 0:
        print("No English audio files found to evaluate.")
        return

    wer = jiwer.wer(true_texts, pred_texts)
    avg_latency = total_latency / count
    print("\n" + "="*40)
    print("ENGLISH EVALUATION RESULTS")
    print("="*40)
    print(f"Total phrases evaluated: {count}")
    print(f"Word Error Rate (WER): {wer * 100:.2f}%")
    print(f"Average STT Latency: {avg_latency:.3f} s")
    print("="*40)

if __name__ == "__main__":
    evaluate_english()
