# Korean Vocabulary TTS

A small local Streamlit app and CLI for turning Korean vocabulary lesson JSON into MP3 study audio using OpenAI text-to-speech.

The daily workflow is:

1. Open the local Streamlit app.
2. Paste lesson JSON into the sidebar.
3. Save the lesson into `lessons/`.
4. Preview the lesson and study script.
5. Generate one MP3 in `outputs/`.
6. Practice with the generated audio.

Default file mapping:

```text
lessons/week1-day3.json
→ outputs/week1-day3.mp3
```

## Features

- Local Streamlit app for daily use
- Paste lesson JSON directly into the app
- Saves lesson JSON into `lessons/`
- Lists existing local lesson files
- Validates lesson JSON before saving
- Shows a scrollable lesson preview table
- Shows a generated study-script preview
- Generates one MP3 per lesson file
- Defaults the MP3 filename to the lesson filename
- Supports custom output filenames under advanced settings
- Supports OpenAI voices such as `marin` and `cedar`
- Includes CLI commands for automation/debugging
- Uses a warm Korean-inspired app theme and local icon asset

## Input format

Lesson files use this JSON structure:

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

## Generated study-script order

Each item is converted into this spoken order:

```text
공장

factory

That factory is old.

그 공장은 오래됐어요.

그 공장은 오래되었습니다.
```

Items are separated by extra blank lines to encourage natural pauses without making the TTS voice read the word “pause”.

## Project structure

```text
korean-tts/
  .env.example
  .gitignore
  README.md
  SPEC.md
  app.py
  requirements.txt

  .streamlit/
    config.toml

  assets/
    korean_tts_icon.png

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

### 3. Upgrade packaging tools

This helps avoid dependency installation problems, especially with Streamlit and `pyarrow` on macOS.

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

The requirements intentionally pin `pyarrow==14.0.2` and `numpy<2` to avoid local Arrow build issues on some macOS/Python setups.

### 5. Install FFmpeg

On macOS with Homebrew:

```bash
brew install ffmpeg
```

FFmpeg is used to combine multiple temporary MP3 chunks into one final MP3 file when a lesson is too long for one API request.

### 6. Create a local `.env` file

Copy the example file:

```bash
cp .env.example .env
```

Then add your OpenAI API key:

```env
OPENAI_API_KEY=your_api_key_here
```

Do not commit `.env`.

## Run the Streamlit app

```bash
streamlit run app.py
```

The app opens in your browser.

## Daily app workflow

1. Paste a lesson filename in the sidebar, for example:

   ```text
   2026-05-18-week1-day1
   ```

2. Paste the full lesson JSON.
3. Click **Save lesson JSON**.
4. Confirm the lesson appears in the preview.
5. Choose the voice.
6. Click **Generate MP3**.
7. Use the audio player or **Download MP3** button.

The generated MP3 defaults to the same name as the lesson file:

```text
lessons/2026-05-18-week1-day1.json
outputs/2026-05-18-week1-day1.mp3
```

## Optional Mac launcher

For easier daily startup, create a local `.command` file outside Git or keep it ignored by `.gitignore`:

```bash
#!/bin/zsh
cd /Users/YOUR_USER/korean-tts
source .venv/bin/activate
streamlit run app.py
```

Make it executable:

```bash
chmod +x /path/to/Korean-TTS.command
```

Double-click it to start the app.

`.command` files are ignored by Git because they contain local machine paths.

## CLI usage

The CLI remains useful for testing and automation.

### List lesson files

```bash
python -m korean_tts.cli --list-lessons
```

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

## Public repository safety

The repository is public. Do not commit:

- `.env`
- OpenAI API keys
- `.venv/`
- real lesson files copied from paid services
- generated MP3 files
- temporary audio chunks
- local `.command` launchers

The `.gitignore` is configured to keep those out of Git.

## Notes

- This project requires an OpenAI API key.
- API usage may incur costs depending on OpenAI pricing.
- Generated MP3 files are saved locally in `outputs/`.
- Real lesson files are ignored by Git by default, except `lessons/example.json`.

## License

MIT
