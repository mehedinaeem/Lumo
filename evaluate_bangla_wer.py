import os
import csv
import time
import wave
import numpy as np
import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import jiwer

dataset_dir = "dataset"
metadata_file = os.path.join(dataset_dir, "metadata.csv")

def evaluate_bangla():
    print("Loading BanglaASR model...")
    model_path = "models/stt/BanglaASR"
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}. Exiting.")
        return
        
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = WhisperProcessor.from_pretrained(model_path)
    model = WhisperForConditionalGeneration.from_pretrained(model_path).to(device)
    model.eval()
    
    true_texts = []
    pred_texts = []
    total_latency = 0
    count = 0

    print("Reading metadata.csv...")
    with open(metadata_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['language'] == 'bangla':
                audio_path = os.path.join(dataset_dir, "bangla", row['speaker'], row['filename'])
                if not os.path.exists(audio_path):
                    continue
                
                # Load audio using wave and numpy
                try:
                    wf = wave.open(audio_path, "rb")
                    n_frames = wf.getnframes()
                    audio_data = wf.readframes(n_frames)
                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    wf.close()
                except Exception as e:
                    print(f"Skipping bad file {audio_path}: {e}")
                    continue
                
                start_time = time.time()
                inputs = processor(audio_np, sampling_rate=16000, return_tensors="pt")
                input_features = inputs.input_features.to(device)
                forced_decoder_ids = processor.get_decoder_prompt_ids(language="bengali", task="transcribe")
                
                with torch.no_grad():
                    predicted_ids = model.generate(
                        input_features,
                        forced_decoder_ids=forced_decoder_ids,
                        max_new_tokens=80,
                        repetition_penalty=1.5,
                        no_repeat_ngram_size=3,
                        do_sample=False,
                        num_beams=1,
                    )
                
                pred_text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0].strip()
                end_time = time.time()
                
                true_text = row['transcript']
                
                true_texts.append(true_text)
                pred_texts.append(pred_text)
                total_latency += (end_time - start_time)
                count += 1
                
                if count % 10 == 0:
                    print(f"Processed {count} Bangla phrases...")
                
                if count >= 50:
                    print("Reached subset limit of 50 for quick evaluation.")
                    break
                    
    if count == 0:
        print("No Bangla audio files found.")
        return
        
    wer = jiwer.wer(true_texts, pred_texts)
    avg_latency = total_latency / count
    print("\n" + "="*40)
    print("BANGLA EVALUATION RESULTS")
    print("="*40)
    print(f"Total phrases evaluated: {count}")
    print(f"Word Error Rate (WER): {wer * 100:.2f}%")
    print(f"Average STT Latency: {avg_latency:.3f} s")
    print("="*40)

if __name__ == "__main__":
    evaluate_bangla()
