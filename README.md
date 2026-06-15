# TTRPG Session Summarizer

Offline AI pipeline for transforming long tabletop RPG sessions into structured campaign notes.

The project combines **Faster-Whisper**, **PyAnnote**, **Ollama**, and **Qwen** to automatically:

* Transcribe several hours of gameplay
* Identify different speakers
* Align speakers with transcript segments
* Merge the entire session chronologically
* Produce campaign-quality summaries using local LLMs

Everything runs locally after the required models are downloaded.

---

# Pipeline

```
Recording (.m4a / .mp3 / .wav)
            │
            ▼
     transcribe.py
            │
            ▼
 Transcript with timestamps
            │
            ▼
     diarization.py
            │
            ▼
 Speaker timeline
            │
            ▼
      alignment.py
            │
            ▼
 merged_timeline.json
            │
            ▼
       resume.py
            │
            ▼
 campaign_report.md
```

---

# Features

* Local speech recognition using Faster-Whisper
* Automatic language detection
* Word timestamps
* Speaker diarization
* Speaker alignment
* Context-aware campaign summaries
* Chunked summarization for extremely long sessions
* Final campaign report generated with local LLMs
* No cloud APIs required (except first-time Hugging Face model download)

---

# Requirements

Recommended:

* Python 3.11
* NVIDIA GPU (CUDA)
* 12GB+ VRAM recommended
* Ollama
* FFmpeg
* Hugging Face account (for PyAnnote)

---

# Installation

## 1. Install Python

Python 3.11 is recommended.

---

## 2. Install PyTorch (CUDA)

Follow the official installation guide:

https://pytorch.org/get-started/locally/

Verify:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

Expected:

```
True
```

---

## 3. Install project dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install Ollama

Install Ollama from:

https://ollama.com

Download the recommended models:

```bash
ollama pull qwen3:8b
ollama pull qwen3:14b
```

---

## 5. Hugging Face

Create a free account.

Accept the license for:

* pyannote/speaker-diarization-community-1

Create an Access Token and place it inside:

```python
HF_TOKEN = "your_token_here"
```

---

# Folder structure

```
audio/
transcripts/
chunk_summaries/

transcribe.py
diarization.py
alignment.py
resume.py

campaign_context.json
campaign_report.md
```

---

# Processing workflow

## 1

Place recordings inside:

```
audio/
```

Supported formats include:

* m4a
* mp3
* wav
* flac
* ogg

---

## 2

Run transcription:

```bash
python transcribe.py
```

Outputs:

```
transcripts/
```

---

## 3

Run diarization:

```bash
python diarization.py
```

Outputs:

```
diarization.json
```

---

## 4

Align transcript with speakers:

```bash
python alignment.py
```

Outputs:

```
merged_timeline.json
```

---

## 5

Configure campaign context:

```
campaign_context.json
```

Example:

```json
{
  "campaign_name": "Lost Mine of Phandelver",
  "players": [
    "Alice",
    "Bob",
    "Carlos"
  ],
  "characters": [
    {
      "player": "Alice",
      "character": "Thorin",
      "role": "Fighter"
    }
  ],
  "locations": [
    "Phandalin",
    "Wave Echo Cave"
  ],
  "npcs": [
    "Gundren Rockseeker",
    "Sildar Hallwinter"
  ],
  "factions": [
    "Lords' Alliance"
  ],
  "important_items": [
    "Map to Wave Echo Cave"
  ]
}
```

Providing campaign context helps the LLM recognize names correctly and improves summary quality.

---

## 6

Generate the campaign report:

```bash
python resume.py
```

Produces:

```
campaign_report.md
```

---

# Models

Recommended:

| Purpose         | Model     |
| --------------- | --------- |
| Chunk summaries | qwen3:8b  |
| Final report    | qwen3:14b |

---

# Current capabilities

* Automatic transcription
* Speaker diarization
* Speaker alignment
* Timeline reconstruction
* Session summaries
* Campaign reports

---

# Future ideas

* Automatic speaker naming
* Character detection
* Session memory across campaigns
* Vector database for campaign history
* RAG support
* NPC relationship graphs
* Interactive web interface

```
```
