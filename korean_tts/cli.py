import argparse
from datetime import date
from pathlib import Path

import pyperclip

from korean_tts.config import DEFAULT_VOICE, OUTPUT_DIR
from korean_tts.parser import parse_markdown_table
from korean_tts.script_builder import build_study_script
from korean_tts.tts import generate_speech_chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Korean vocabulary MP3 study audio from a copied markdown table."
    )

    parser.add_argument(
        "--from-clipboard",
        action="store_true",
        help="Read the copied ChatGPT markdown table from the Mac clipboard.",
    )

    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output MP3 filename. Example: day_01.mp3",
    )

    parser.add_argument(
        "--voice",
        type=str,
        default=DEFAULT_VOICE,
        help="OpenAI TTS voice. Recommended: marin or cedar.",
    )

    parser.add_argument(
        "--preview-script",
        action="store_true",
        help="Print the generated study script before creating audio.",
    )

    args = parser.parse_args()

    if not args.from_clipboard:
        raise SystemExit("Use --from-clipboard for now.")

    raw_text = pyperclip.paste()

    if not raw_text.strip():
        raise SystemExit("Clipboard is empty. Copy the ChatGPT vocabulary table first.")

    items = parse_markdown_table(raw_text)
    study_script = build_study_script(items)

    if args.preview_script:
        print("\n--- GENERATED STUDY SCRIPT ---\n")
        print(study_script)
        print("\n--- END ---\n")

    output_name = args.out or f"korean_vocab_{date.today().isoformat()}.mp3"
    output_path = OUTPUT_DIR / output_name

    result = generate_speech_chunks(
        script=study_script,
        output_path=output_path,
        voice=args.voice,
    )

    print(f"\nDone: {result}")


if __name__ == "__main__":
    main()