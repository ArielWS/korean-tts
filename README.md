# Korean Vocabulary TTS CLI

A small local Python tool for turning structured Korean vocabulary lesson files into MP3 study audio using OpenAI text-to-speech.

The intended workflow is:

1. Generate or write a Korean vocabulary lesson as JSON.
2. Save it in `lessons/`.
3. Preview the study script if needed.
4. Generate one MP3 file in `outputs/`.

Example:

```text
lessons/week1-day3.json
→ outputs/week1-day3.mp3
```

## Features

- Uses local JSON lesson files
- Creates starter lesson files from the CLI
- Lists available lesson files
- Converts lesson JSON into a structured Korean/English study script
- Supports informal polite and formal polite Korean example sentences
- Generates one final MP3 per lesson file
- Names the output MP3 after the input lesson by default
- Supports custom output filenames
- Supports configurable OpenAI TTS voices
- Splits longer lessons into chunks automatically

## Input format

Lesson files live in `lessons/` and use this JSON structure:

```json
{
  "lesson_title": "Example Lesson",
  "items": [
    {
      "korean_word": "공장",
      "english": "factory",
      "korean_sentence_informal_polite": "그 공장은 오래됐어요.",
      "korean_sentence_formal_polite": "그 공장은 오래되었습니다.",
      "english_sentence": "That factory is old."
    },
    {
      "korean_word": "열",
      "english": "fever",
      "korean_sentence_informal_polite": "오늘 열이 조금 있어요.",
      "korean_sentence_formal_polite": "오늘 열이 조금 있습니다.",
      "english_sentence": "I have a slight fever today."
    }
  ]
}
```

Each item requires:

| Field | Purpose |
|---|---|
| `korean_word` | Korean vocabulary word or phrase |
| `english` | English meaning or gloss |
| `korean_sentence_informal_polite` | Korean example sentence in informal polite form, usually `-요` style |
| `korean_sentence_formal_polite` | Korean example sentence in formal polite form, usually `-습니다 / -ㅂ니다` style |
| `english_sentence` | English translation of the example sentence |

## Generated study-script format

Each item is converted into this kind of audio script:

```text
Item 1.

공장

factory

Informal polite.

그 공장은 오래됐어요.

Formal polite.

그 공장은 오래되었습니다.

That factory is old.

Pause.
```

## Project structure

```text
korean-tts/
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
    cli.py
    config.py
    lesson_files.py
    parser.py
    script_builder.py
    tts.py
    workflow.py
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ArielWS/korean-tts.git
cd korean-tts
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg

On macOS with Homebrew:

```bash
brew install ffmpeg
```

FFmpeg is used to combine multiple temporary MP3 chunks into one final MP3 file when a lesson is too long for one API request.

### 5. Create a local `.env` file

Copy the example file:

```bash
cp .env.example .env
```

Then add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

Do not commit `.env`.

## CLI usage

### List lesson files

```bash
python -m korean_tts.cli --list-lessons
```

### Create a starter lesson file

```bash
python -m korean_tts.cli --create-lesson week1-day3
```

This creates:

```text
lessons/week1-day3.json
```

Real lesson files are ignored by Git by default, except `lessons/example.json`.

### Preview the generated study script

```bash
python -m korean_tts.cli --input lessons/example.json --preview-script
```

Preview mode prints the script and exits. It does not call OpenAI and does not generate audio.

### Generate an MP3

```bash
python -m korean_tts.cli --input lessons/example.json
```

This creates:

```text
outputs/example.mp3
```

### Generate with a custom output filename

```bash
python -m korean_tts.cli --input lessons/example.json --out test-audio.mp3
```

This creates:

```text
outputs/test-audio.mp3
```

### Compare voices

The default voice is `marin`.

```bash
python -m korean_tts.cli --input lessons/example.json --voice cedar
```

## Daily workflow

```bash
cd korean-tts
source .venv/bin/activate
python -m korean_tts.cli --create-lesson 2026-05-18-week1-day1
```

Edit the new JSON file in `lessons/`, then run:

```bash
python -m korean_tts.cli --input lessons/2026-05-18-week1-day1.json --preview-script
python -m korean_tts.cli --input lessons/2026-05-18-week1-day1.json
```

The final audio file will be saved as:

```text
outputs/2026-05-18-week1-day1.mp3
```

## Public repository safety

The repository is public. Do not commit:

- `.env`
- OpenAI API keys
- `.venv/`
- real lesson files copied from paid services
- generated MP3 files
- temporary audio chunks

The `.gitignore` is configured to keep those out of Git.

## Notes

- This project requires an OpenAI API key.
- API usage may incur costs depending on OpenAI pricing.
- Generated MP3 files are saved locally in `outputs/`.
- The CLI is the core workflow; a Streamlit app may be added as a thin local UI wrapper.

## License

MIT
