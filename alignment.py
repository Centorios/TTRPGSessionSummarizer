import json
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================

TRANSCRIPT_FILE = Path("transcripts/transcript.json")
DIARIZATION_FILE = Path("transcripts/diarization.json")

OUTPUT_JSON = Path("transcripts/merged_timeline.json")
OUTPUT_TXT = Path("transcripts/merged_timeline.txt")

# =====================================================

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60

    return f"{h:02d}:{m:02d}:{s:06.3f}"

# =====================================================
# LOAD
# =====================================================

print("Loading transcript...")

with open(TRANSCRIPT_FILE, "r", encoding="utf-8") as f:
    transcript = json.load(f)

print("Loading diarization...")

with open(DIARIZATION_FILE, "r", encoding="utf-8") as f:
    diarization = json.load(f)

# =====================================================
# FIND SPEAKER
# =====================================================

def find_speaker(start, end):

    best_overlap = 0
    best_speaker = "UNKNOWN"

    for segment in diarization:

        overlap = min(end, segment["end"]) - max(start, segment["start"])

        if overlap > best_overlap:

            best_overlap = overlap
            best_speaker = segment["speaker"]

    return best_speaker

# =====================================================
# ALIGN
# =====================================================

print("Assigning speakers...")

merged = []

for seg in transcript:

    speaker = find_speaker(
        seg["start"],
        seg["end"]
    )

    merged.append({

        "speaker": speaker,

        "start": round(seg["start"], 3),

        "end": round(seg["end"], 3),

        "text": seg["text"]

    })

# =====================================================
# SAVE JSON
# =====================================================

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        merged,
        f,
        indent=2,
        ensure_ascii=False
    )

# =====================================================
# SAVE TXT
# =====================================================

lines = []

for seg in merged:

    lines.append(
        f"[{format_time(seg['start'])}] "
        f"{seg['speaker']}: "
        f"{seg['text']}"
    )

with open(
    OUTPUT_TXT,
    "w",
    encoding="utf-8"
) as f:

    f.write("\n".join(lines))

print()
print("Done.")
print(f"Segments: {len(merged)}")
print(OUTPUT_JSON.resolve())