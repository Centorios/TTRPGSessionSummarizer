import json
import math
import requests
from pathlib import Path

# =====================================================
# CONFIG
# =====================================================

CHUNK_MODEL = "qwen3:8b"
FINAL_MODEL = "qwen3:14b"

OLLAMA_URL = "http://localhost:11434/api/generate"

TRANSCRIPT_FILE = Path("transcripts/merged_timeline.json")

CHUNK_DIR = Path("chunk_summaries")
CHUNK_DIR.mkdir(exist_ok=True)

FINAL_REPORT = Path("campaign_report.md")

# 500 is a good starting point
CHUNK_SIZE = 500

# =====================================================
# OLLAMA
# =====================================================

def ask_ollama(model, prompt):

    print("\n----------------------------------------")
    print(f"Model: {model}")
    print(f"Prompt chars: {len(prompt):,}")
    print("----------------------------------------")

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_ctx": 16384,
                "temperature": 0.1
            }
        },
        stream=True,
        timeout=7200
    )

    response.raise_for_status()

    output = ""

    for line in response.iter_lines():

        if not line:
            continue

        data = json.loads(line)

        if "response" in data:

            chunk = data["response"]

            print(chunk, end="", flush=True)

            output += chunk

        if data.get("done", False):
            break

    print("\n")

    return output

# ========================================
# LOAD CAMPAIGN CONTEXT
# ========================================

with open(
    "campaign_context.json",
    "r",
    encoding="utf-8"
) as f:
    campaign_context = json.load(f)

# =====================================================
# LOAD TRANSCRIPT
# =====================================================

print("Loading transcript...")

with open(
    TRANSCRIPT_FILE,
    "r",
    encoding="utf-8"
) as f:

    transcript = json.load(f)

print(
    f"Loaded {len(transcript):,} entries"
)

# =====================================================
# CHUNK PASS
# =====================================================

total_chunks = math.ceil(
    len(transcript) / CHUNK_SIZE
)

print(
    f"Creating {total_chunks} chunks "
    f"of {CHUNK_SIZE} entries"
)

chunk_reports = []

for chunk_index in range(total_chunks):

    start = chunk_index * CHUNK_SIZE
    end = start + CHUNK_SIZE

    chunk = transcript[start:end]

    transcript_text = []

    for entry in chunk:

        transcript_text.append(
            f"[{entry['start']:.2f}] "
            f"{entry['speaker']}: "
            f"{entry['text']}"
        )

    transcript_text = "\n".join(transcript_text)

    print("\n========================================")
    print(
        f"Chunk {chunk_index+1}/{total_chunks}"
    )
    print(
        f"Transcript chars: {len(transcript_text):,}"
    )
    print("========================================")

    prompt = f"""
You are processing an RPG session transcript.

Rules:

- Do not invent facts.
- Do not infer.
- Do not speculate.
- Only extract explicitly mentioned information.
- Ignore transcription mistakes when possible.
- Extract only information explicitly present.
- Be concise.
- Output markdown only.

Campaign context:
{json.dumps(campaign_context, indent=2, ensure_ascii=False)}

Return:

# Major Events

# NPCs Mentioned

# Locations Mentioned

# Quests / Objectives

# Important Items

# Character Moments

# Open Threads

Transcript:

{transcript_text}
"""

    summary = ask_ollama(
        CHUNK_MODEL,
        prompt
    )

    chunk_file = (
        CHUNK_DIR /
        f"chunk_{chunk_index+1:03d}.md"
    )

    with open(
        chunk_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(summary)

    chunk_reports.append(summary)

    print(
        f"Saved {chunk_file.name}"
    )

# =====================================================
# FINAL PASS
# =====================================================

print("\n========================================")
print("Building final report")
print("========================================")

combined = "\n\n".join(
    chunk_reports
)

final_prompt = f"""
You are an RPG campaign historian.

The following are chunk summaries
from a complete tabletop RPG session.

Merge everything into a professional
campaign recap.

Campaign context:
{json.dumps(campaign_context, indent=2, ensure_ascii=False)}

Return:

# Executive Summary

# Extended Summary (at least 2 A4 pages)

# Detailed Session Timeline

# NPC Updates

# Location Updates

# Quest Progress

# Important Items

# Character Highlights

# Open Plot Threads

# Next Session Hooks

Chunk Summaries:

{combined}
"""

final_report = ask_ollama(
    FINAL_MODEL,
    final_prompt
)

with open(
    FINAL_REPORT,
    "w",
    encoding="utf-8"
) as f:

    f.write(final_report)

print("\n========================================")
print("DONE")
print("========================================")
print(FINAL_REPORT.resolve())