# TTRPGSessionSummarizer
Local AI pipepile for TTRPG transcript and summarization


This project provides a fully local pipeline for:

* Multi-speaker RPG session transcription
* Speaker timeline generation
* Campaign report generation
* Long-term campaign memory extraction

The entire workflow runs locally using:

* Faster-Whisper
* NVIDIA CUDA
* cuDNN
* Ollama
* Qwen3

No cloud APIs are required.

---

# Hardware Requirements

Recommended:

* NVIDIA RTX 3080 (10GB+) or better
* 32GB+ RAM (64GB recommended)
* Windows 10/11
* Python 3.8+

Minimum tested:

* RTX 3080 10GB
* 16GB RAM

---

# Installing CUDA

Install CUDA 12.8:

https://developer.nvidia.com/cuda-12-8-0-download-archive

Default installation path:

```text
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8
```

Verify installation:

```powershell
nvidia-smi
nvcc --version
```

---

# Installing cuDNN

Download cuDNN 9 for CUDA 12.x:

https://developer.nvidia.com/cudnn

Install to:

```text
C:\Program Files\NVIDIA\CUDNN\
```

Example path:

```text
C:\Program Files\NVIDIA\CUDNN\v9.x\bin\12.8\x64
```

---

# Configure Environment Variables

Add both directories to PATH:

```text
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin

C:\Program Files\NVIDIA\CUDNN\v9.x\bin\12.8\x64
```

Permanent PowerShell script:

```powershell
$cuda = "C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin"
$cudnn = "C:\Program Files\NVIDIA\CUDNN\v9.x\bin\12.8\x64"

$current = [Environment]::GetEnvironmentVariable(
    "Path",
    "User"
)

if ($current -notlike "*$cuda*") {
    $current += ";$cuda"
}

if ($current -notlike "*$cudnn*") {
    $current += ";$cudnn"
}

[Environment]::SetEnvironmentVariable(
    "Path",
    $current,
    "User"
)

Write-Host "PATH updated."
```

Open a new PowerShell after running it.

---

# Python Setup

Create virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install faster-whisper
pip install requests
```

Verify CUDA access:

```powershell
python -c "import torch; print(torch.cuda.is_available())"
```

---

# Whisper Model

Recommended:

```python
MODEL_NAME = "large-v3"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
```

Transcription settings:

```python
segments, info = model.transcribe(
    str(audio_file),
    task="transcribe",
    temperature=0.1,
    beam_size=5,
    word_timestamps=True,
    vad_filter=True,
    condition_on_previous_text=False
)
```

Notes:

* `temperature=0.1` improves consistency.
* `condition_on_previous_text=False` avoids repetition loops.
* `large-v3` produced the best results during testing.

---

# Audio Structure

Input:

```text
audio/
├── player1.mp3
├── player2.mp3
├── player3.mp3
├── dm.mp3
```

Output:

```text
transcripts/
├── player1.json
├── player1.txt
├── player2.json
├── merged_timeline.json
└── merged_timeline.txt
```

---

# Installing Ollama

Download:

https://ollama.com

Verify:

```powershell
ollama --version
```

---

# Download Qwen

Fast summarization:

```powershell
ollama pull qwen3:8b
```

High quality final report:

```powershell
ollama pull qwen3:14b
```

---

# Recommended Workflow

Step 1:

```text
Audio Files
↓
Whisper
↓
merged_timeline.json
```

Step 2:

```text
merged_timeline.json
↓
Qwen3:8B
↓
Chunk Reports
```

Step 3:

```text
Chunk Reports
↓
Qwen3:14B
↓
Final Campaign Report
```

---

# Campaign Context

Example:

```python
campaign_context = {
    "campaign_name": "Fear & Hunger Argentina",
    "players": [
        "Alejo",
        "Juan"
    ],
    "characters": [
        "Inspector Salvatierra",
        "Father Ignacio"
    ],
    "locations": [
        "Línea A",
        "Plaza Miserere"
    ],
    "npcs": [
        "El Guardavía"
    ],
    "factions": [
        "Culto de Alll-Mer"
    ],
    "important_items": [
        "Llave de Bronce"
    ]
}
```

This context is injected into every LLM prompt to improve recognition of fantasy names, NPCs, locations, and factions.

---

# Future Improvements

Planned features:

* Campaign memory database
* Automatic NPC extraction
* Automatic location extraction
* Quest tracking
* Relationship tracking
* Storyboard generation
* AI-assisted session recap videos

---

# Troubleshooting

## cublas64_12.dll missing

Usually caused by:

* CUDA not installed
* CUDA PATH missing

Verify:

```powershell
where cublas64_12.dll
```

---

## GPU not being used

Check:

```powershell
nvidia-smi
```

During transcription:

```text
GPU Utilization > 50%
```

should be visible.

---

## Ollama extremely slow

Check loaded model:

```powershell
ollama ps
```

Recommended:

```text
Chunk processing -> qwen3:8b
Final merge -> qwen3:14b
```

Using qwen3:14b for every chunk significantly increases processing time.

---
