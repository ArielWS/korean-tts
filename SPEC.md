# Korean Vocabulary TTS CLI — Project Specification

## 1. Purpose

This project is a small local tool for converting Korean vocabulary lessons into MP3 study audio.

The user should be able to maintain daily lesson files locally, generate pronunciation-focused audio from those files, and keep the resulting MP3s named and organized in a way that matches the source lesson.

The project is intentionally small. The goal is not to build a full language-learning platform. The goal is a reliable daily workflow for turning structured vocabulary content into clear Korean/English study audio.

## 2. Primary User Workflow

The intended workflow is:

1. The user collects a daily Korean vocabulary list from a learning source.
2. The user asks ChatGPT to expand the list into structured JSON containing:
   - Korean vocabulary word
   - English meaning
   - Korean example sentence
   - English translation of the sentence
3. The user saves that JSON as a lesson file in `lessons/`.
4. The user runs the CLI or opens the local Streamlit app.
5. The tool generates one MP3 file in `outputs/`.
6. The MP3 filename matches the lesson filename.

Example:

```text
lessons/2026-05-18-week1-day1.json
→ outputs/2026-05-18-week1-day1.mp3
```

## 3. Non-Goals

This project should not become any of the following:

- A full SaaS application
- A hosted web service
- A database-backed language platform
- A spaced-repetition system
- A vocabulary-management CMS
- A translation engine
- A flashcard app
- A complex package with unnecessary abstractions

The tool should stay local, simple, auditable, and easy to run from VS Code, the Mac terminal, or a local Streamlit app.

## 4. Core Requirements

### 4.1 Lesson Input

Lesson input should use JSON files stored in `lessons/`.

Real lesson files should not be committed to the public repository by default, because they may contain content copied from paid learning services.

The repository should include only a safe example file:

```text
lessons/example.json
```

### 4.2 JSON Schema

The preferred lesson format is:

```json
{
  "lesson_title": "Week 1 Day 1",
  "items": [
    {
      "korean_word": "공장",
      "english": "factory",
      "korean_sentence": "그 공장은 오래됐어요.",
      "english_sentence": "That factory is old."
    }
  ]
}
```

Required top-level fields:

| Field | Type | Required | Notes |
|---|---:|---:|---|
| `lesson_title` | string | No | Human-readable label only |
| `items` | array | Yes | List of vocabulary items |

Required item fields:

| Field | Type | Required | Notes |
|---|---:|---:|---|
| `korean_word` | string | Yes | Korean vocabulary word or phrase |
| `english` | string | Yes | English meaning or gloss |
| `korean_sentence` | string | Yes | Korean example sentence |
| `english_sentence` | string | Yes | English translation of the example sentence |

### 4.3 Output

The application should generate one final MP3 file per input lesson file.

The final MP3 should be saved in `outputs/`.

The output filename should default to the input filename stem:

```text
lessons/week1-day1.json
→ outputs/week1-day1.mp3
```

The application may internally create temporary MP3 chunks when the lesson is too long for one API call. These temporary chunks should not remain in the project after successful generation.

### 4.4 Audio Format

Each vocabulary item should be read in a consistent study cadence:

```text
Item 1.

공장

factory

그 공장은 오래됐어요.

That factory is old.

Pause.
```

The cadence may be adjusted later, but the first version should prioritize clarity and repeatability over theatrical performance.

### 4.5 Pronunciation and Voice Requirements

The TTS instructions should request:

- Clear standard Seoul Korean pronunciation
- Neutral adult voice
- Slightly slower than normal conversational Korean
- No acting
- No exaggerated emotion
- No dramatic intonation
- Clear English pronunciation for English lines
- No additions, omissions, translations, or explanations

The default OpenAI TTS settings should be:

| Setting | Default |
|---|---|
| Model | `gpt-4o-mini-tts` |
| Voice | `marin` |
| Alternate voice | `cedar` |
| Format | `mp3` |

The voice should be configurable from both CLI and Streamlit.

## 5. Architecture

### 5.1 Recommended Project Structure

```text
korean-tts/
  .env
  .env.example
  .gitignore
  README.md
  SPEC.md
  requirements.txt

  lessons/
    example.json

  outputs/

  korean_tts/
    __init__.py
    config.py
    parser.py
    script_builder.py
    tts.py
    cli.py

  app.py
```

### 5.2 Module Responsibilities

#### `korean_tts/config.py`

Responsible for:

- Loading environment variables
- Project paths
- Default model
- Default voice
- Default response format
- TTS instructions
- Chunk-size constants

Should not contain business logic.

#### `korean_tts/parser.py`

Responsible for:

- Loading JSON lesson files
- Validating required fields
- Converting raw JSON into typed internal objects

Should return a list of vocabulary items and optional lesson metadata.

#### `korean_tts/script_builder.py`

Responsible for:

- Turning vocabulary items into the final study script text
- Keeping audio cadence consistent
- Splitting long scripts into safe chunks for the TTS API

Should not call OpenAI directly.

#### `korean_tts/tts.py`

Responsible for:

- Calling OpenAI text-to-speech
- Writing temporary MP3 chunks
- Combining chunks into one final MP3 where needed
- Returning the final output path

Should not parse lesson files.

#### `korean_tts/cli.py`

Responsible for:

- Command-line arguments
- Calling parser, script builder, and TTS modules
- Printing useful success/error messages

The CLI should remain the canonical automation path.

#### `app.py`

Optional Streamlit wrapper.

Responsible for:

- Listing available lesson files from `lessons/`
- Showing a preview of parsed lesson items
- Allowing voice selection
- Triggering MP3 generation
- Showing final output path
- Optionally offering audio playback/download

Streamlit should not duplicate core logic. It should call the same functions used by the CLI.

## 6. CLI Design

Primary command:

```bash
python -m korean_tts.cli --input lessons/week1-day1.json
```

Expected output:

```text
outputs/week1-day1.mp3
```

Optional flags:

```bash
python -m korean_tts.cli --input lessons/week1-day1.json --voice cedar
python -m korean_tts.cli --input lessons/week1-day1.json --out custom-name.mp3
python -m korean_tts.cli --input lessons/week1-day1.json --preview-script
```

### CLI Arguments

| Argument | Required | Default | Purpose |
|---|---:|---|---|
| `--input` | Yes | None | Path to lesson JSON file |
| `--out` | No | Input filename stem + `.mp3` | Custom output filename |
| `--voice` | No | `marin` | OpenAI TTS voice |
| `--preview-script` | No | false | Print generated script before TTS |

## 7. Streamlit Design

Streamlit is optional but desirable because it provides a simple app-like interface without building a full web app.

### Streamlit MVP

The first Streamlit version should provide:

- Page title
- Dropdown of JSON files from `lessons/`
- Parsed lesson preview
- Voice selector
- Output filename preview
- Generate MP3 button
- Final output path
- Audio playback if the file exists

### Streamlit Non-Goals

The Streamlit app should not initially include:

- User accounts
- File uploads
- Editing full JSON inside the app
- Cloud deployment
- Database storage
- Complex settings screens

## 8. Git and Public Repo Rules

Because the repository is public, the following should not be committed:

- `.env`
- OpenAI API keys
- `.venv/`
- Real lesson JSON files from paid learning services
- Generated MP3 files
- Temporary audio chunks
- Local logs

Recommended `.gitignore` rules:

```gitignore
# Secrets
.env
.env.*
!.env.example

# Python
__pycache__/
*.py[cod]
.venv/
venv/
env/

# Real lesson content
lessons/*.json
!lessons/example.json

# Generated audio
outputs/
*.mp3
*.wav
*.m4a

# OS / editor
.DS_Store
.vscode/
.idea/

# Logs
*.log
```

## 9. Error Handling Requirements

The application should provide clear errors for:

- Missing `.env` or missing `OPENAI_API_KEY`
- Missing input file
- Invalid JSON
- Missing `items` field
- Empty `items` list
- Missing required item fields
- OpenAI API failure
- FFmpeg not installed when chunk stitching is required

Errors should be written in plain language.

## 10. Implementation Principles

The project should follow these principles:

1. Keep the CLI as the stable core.
2. Keep Streamlit as a thin wrapper.
3. Avoid overengineering.
4. Prefer readable code over clever abstractions.
5. Make outputs deterministic and easy to trace back to inputs.
6. Never commit secrets or paid lesson content.
7. Keep the study cadence predictable.
8. Make voice/model settings configurable but not complicated.

## 11. Initial Milestones

### Milestone 1 — JSON CLI

- Add `lessons/example.json`
- Replace markdown table parser with JSON lesson parser
- Add `--input` CLI argument
- Auto-name MP3 from input filename
- Generate one MP3 from one JSON lesson

### Milestone 2 — Safer Public Repo

- Update `.gitignore`
- Ensure real lesson files are ignored
- Ensure generated MP3s are ignored
- Update README usage instructions

### Milestone 3 — Streamlit MVP

- Add `app.py`
- List lesson files
- Preview lesson content
- Select voice
- Generate MP3
- Play or download generated MP3

### Milestone 4 — Quality Improvements

Potential later improvements:

- Add configurable pauses
- Add Korean-only mode
- Add review mode with repeated Korean sentence
- Add per-item numbering toggle
- Add validation command
- Add support for alternate JSON field names
- Add a simple template prompt for generating lesson JSON from raw vocabulary words

## 12. Current Preferred Direction

The current preferred direction is:

```text
Local JSON lesson files
→ CLI core
→ one MP3 per lesson file
→ optional Streamlit wrapper
```

This should remain the guiding architecture unless deliberately changed.
