# LUMO Speech Dataset

> **Dataset hosted externally:** The full dataset (audio files + metadata) is available at:  
> 👉 **https://github.com/mehedinaeem/lumo-speech-dataset**

This directory contains the custom multilingual speech dataset collected to evaluate the LUMO offline voice assistant. The dataset is designed to measure automatic speech recognition (ASR) performance (Word Error Rate) for both English and Bangla offline processing.

## Contents
- `metadata.csv`: Mappings of filenames to languages, speakers, and true transcriptions.
- `english/`: Extracted WAV audio recordings of English command phrases.
- `bangla/`: Extracted WAV audio recordings of Bangla command phrases.

## Properties
- **Total Utterances**: 1000
- **Speakers**: 10 (bilingual)
- **Languages**: English (500), Bangla (500)
- **Format**: WAV (Mono, 16kHz)
- **Task Type**: Short command phrases (3-10 words) typical for voice assistants.

## How to Download
Clone the dataset repository into this directory:
```bash
git clone https://github.com/mehedinaeem/lumo-speech-dataset dataset
```
