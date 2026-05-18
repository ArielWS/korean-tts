import argparse
from pathlib import Path

from korean_tts.config import DEFAULT_VOICE, OUTPUT_DIR
from korean_tts.parser import load_lesson_json
from korean_tts.script_builder import build_study_script
from korean_tts.tts import generate_speech_chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Korean vocabulary MP3 study audio from a lesson JSON file."
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to lesson JSON file. Example: lessons/example.json",
    )

    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output MP3 filename. Defaults to the input filename stem.",
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

    input_path = Path(args.input)
    lesson = load_lesson_json(input_path)
    study_script = build_study_script(lesson.items)

    if args.preview_script:
        print("\n--- GENERATED STUDY SCRIPT ---\n")
        if lesson.lesson_title:
            print(f"Lesson: {lesson.lesson_title}\n")
        print(study_script)
        print("\n--- END ---\n")

    output_name = args.out or f"{input_path.stem}.mp3"
    output_path = OUTPUT_DIR / output_name

    result = generate_speech_chunks(
        script=study_script,
        output_path=output_path,
        voice=args.voice,
    )

    print(f"\nDone: {result}")


if __name__ == "__main__":
    main()