from faster_whisper import WhisperModel
from pathlib import Path
import json
import time
# =====================================================
# CONFIG
# =====================================================

MODEL_NAME = "large-v3"      # or distil-large-v3
DEVICE = "cuda"
COMPUTE_TYPE = "float16"

AUDIO_DIR = Path("audio")
OUTPUT_DIR = Path("transcripts")

OUTPUT_DIR.mkdir(exist_ok=True)

# =====================================================
# HELPERS
# =====================================================

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60

    return f"{h:02d}:{m:02d}:{s:06.3f}"

# =====================================================
# LOAD MODEL
# =====================================================

print("Loading model...")

model = WhisperModel(
    MODEL_NAME,
    device=DEVICE,
    compute_type=COMPUTE_TYPE
)

print("Model loaded.")

# =====================================================
# GLOBAL TIMELINE
# =====================================================

all_segments = []

# =====================================================
# PROCESS FILES
# =====================================================

audio_extensions = {
    ".mp3",
    ".wav",
    ".m4a",
    ".ogg",
    ".flac"
}

audio_files = [
    f for f in AUDIO_DIR.iterdir()
    if f.suffix.lower() in audio_extensions
]

for audio_file in sorted(audio_files):

    speaker = audio_file.stem

    print(f"\nTranscribing {audio_file.name}")

    segments, info = model.transcribe(
        str(audio_file),
        #language="en",  left blank to auto-detect
        task="transcribe",
        temperature=0.1, # lower temperature for more accurate and less creative output
        beam_size=5,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False
    )

    speaker_json = {
        "speaker": speaker,
        "language": info.language,
        "segments": []
    }

    speaker_txt = []

    total_duration = info.duration

    start_processing = time.time()

    segment_count = 0
    last_update = 0

    print(
        f"\n==================================================\n"
        f"File: {audio_file.name}\n"
        f"Speaker: {speaker}\n"
        f"Duration: {total_duration/60:.1f} min\n"
        f"=================================================="
    )

    for segment in segments:

        segment_count += 1

        text = segment.text.strip()

        # ==========================================
        # LIVE PROGRESS
        # ==========================================

        now = time.time()

        if now - last_update > 1:

            elapsed = now - start_processing

            progress = max(segment.end / total_duration, 0.0001)

            percent = progress * 100

            speed = segment.end / elapsed

            eta = (
                (total_duration - segment.end) / speed
                if speed > 0
                else 0
            )

            print(
                f"\r"
                f"{percent:6.2f}% | "
                f"{segment.end/60:7.1f}/{total_duration/60:.1f} min | "
                f"Speed {speed:5.2f}x | "
                f"ETA {eta/60:6.1f} min | "
                f"Segments {segment_count}",
                end="",
                flush=True
            )

            last_update = now

        # ==========================================
        # BUILD JSON
        # ==========================================

        segment_data = {
            "speaker": speaker,
            "start_seconds": round(segment.start, 3),
            "end_seconds": round(segment.end, 3),
            "text": text,
            "words": []
        }

        if segment.words:

            for word in segment.words:

                segment_data["words"].append({
                    "word": word.word,
                    "start": round(word.start, 3),
                    "end": round(word.end, 3)
                })

        speaker_json["segments"].append(segment_data)

        speaker_txt.append(
            f"[{format_time(segment.start)} -> "
            f"{format_time(segment.end)}] "
            f"{text}"
        )

        all_segments.append({
            "speaker": speaker,
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": text
        })

    elapsed_total = time.time() - start_processing

    realtime_factor = (
        total_duration / elapsed_total
        if elapsed_total > 0
        else 0
    )

    print(
        f"\nFinished {audio_file.name} | "
        f"{elapsed_total/60:.1f} min processing | "
        f"{realtime_factor:.2f}x realtime"
    )

    # ==========================================
    # SAVE INDIVIDUAL FILES
    # ==========================================

    with open(
        OUTPUT_DIR / f"{speaker}.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            speaker_json,
            f,
            ensure_ascii=False,
            indent=2
        )

    with open(
        OUTPUT_DIR / f"{speaker}.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write("\n".join(speaker_txt))

# =====================================================
# MERGE TIMELINE
# =====================================================

print("\nBuilding merged timeline...")

all_segments.sort(key=lambda x: x["start"])

with open(
    OUTPUT_DIR / "merged_timeline.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        all_segments,
        f,
        ensure_ascii=False,
        indent=2
    )

# =====================================================
# HUMAN READABLE TIMELINE
# =====================================================

timeline_lines = []

for seg in all_segments:

    timeline_lines.append(
        f"[{format_time(seg['start'])}] "
        f"{seg['speaker']}: "
        f"{seg['text']}"
    )

with open(
    OUTPUT_DIR / "merged_timeline.txt",
    "w",
    encoding="utf-8"
) as f:

    f.write("\n".join(timeline_lines))

print("\nDone.")
print(f"Processed {len(audio_files)} files.")