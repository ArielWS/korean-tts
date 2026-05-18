# Korean Vocabulary TTS CLI

A small Python CLI tool for turning Korean vocabulary study tables into MP3 audio using OpenAI text-to-speech.

The intended workflow is simple:

1. Generate a Korean vocabulary table in ChatGPT.
2. Copy the table.
3. Run the CLI.
4. Get an MP3 study file.

## Features

- Reads a copied Markdown table from the clipboard
- Converts Korean vocabulary rows into a structured study script
- Sends the script to OpenAI text-to-speech
- Outputs an MP3 file
- Supports multiple OpenAI voices
- Splits longer lessons into chunks automatically

## Input format

Copy a Markdown table in this format:

```markdown
| Korean word | English | Korean sentence | English sentence |
|---|---|---|---|
| 공장 | factory | 그 공장은 오래됐어요. | That factory is old. |
| 열 | fever | 오늘 열이 조금 있어요. | I have a slight fever today. |
| 극장 | theater | 우리는 극장에 갔어요. | We went to the theater. |
```

The CLI reads this directly from the clipboard.

## Project structure

```text
korean-tts/
  .env.example
  .gitignore
  README.md
  requirements.txt
  korean_tts/
    __init__.py
    config.py
    parser.py
    script_builder.py
    tts.py
    cli.py
  outputs/
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
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

FFmpeg is used to combine multiple MP3 chunks into one final MP3 file.

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

## Usage

Copy a valid vocabulary table, then run:

```bash
python -m korean_tts.cli --from-clipboard --out day_01.mp3
```

The output will be saved to:

```text
outputs/day_01.mp3
```

## Preview the generated study script

To inspect the text before audio generation:

```bash
python -m korean_tts.cli --from-clipboard --out test.mp3 --preview-script
```

## Compare voices

The default voice is `marin`.

You can test another voice:

```bash
python -m korean_tts.cli --from-clipboard --out day_01_cedar.mp3 --voice cedar
```

## Example daily workflow

```bash
cd korean-tts
source .venv/bin/activate
python -m korean_tts.cli --from-clipboard --out korean_vocab_2026-05-18.mp3
```

## Notes

- This project requires an OpenAI API key.
- API usage may incur costs depending on OpenAI pricing.
- `.env`, virtual environments, and generated audio files should not be committed.
- Generated MP3 files are saved locally in `outputs/`.

## License

MIT