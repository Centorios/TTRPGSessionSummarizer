from pathlib import Path
import json
import torch
from pyannote.audio import Pipeline

# ===========================================
# CONFIG
# ===========================================

AUDIO_FILE = Path("audio/session.wav")
OUTPUT_FILE = Path("transcripts/diarization.json")

# ===========================================
# LOAD TOKEN
# ===========================================

with open("hf_token.txt", "r") as f:
    HF_TOKEN = f.read().strip()

# ===========================================
# LOAD PIPELINE
# ===========================================

print("Loading Community-1 pipeline...")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=HF_TOKEN
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
pipeline.to(device)

print(f"Running on {device}")

# ===========================================
# DIARIZATION
# ===========================================

print("Analyzing speakers...")

output = pipeline(str(AUDIO_FILE),
    num_speakers=6
)

segments = []

for turn, _, speaker in output.itertracks(yield_label=True):

    segments.append({
        "speaker": speaker,
        "start": round(turn.start, 3),
        "end": round(turn.end, 3)
    })

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        segments,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"Saved {OUTPUT_FILE}")