import argparse
from pathlib import Path

from korean_tts.config import DEFAULT_VOICE
from korean_tts.lesson_files import create_lesson_file, list_lesson_files
from korean_tts.workflow import generate_lesson_audio, prepare_lesson_script


def print_lesson_files() -> None:
    lesson_files = list_lesson_files()

    if not lesson_files:
        print("No lesson JSON files found in lessons/.")
        return

    print("\nAvailable lesson files:\n")

    for index, path in enumerate(lesson_files, start=1):
        print(f"{index}. {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Korean vocabulary MP3 study audio from a lesson JSON file."
    )

    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Path to lesson JSON file. Example: lessons/example.json",
    )

    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output MP3 filename or path. Defaults to the input filename stem.",
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
        help="Print the generated study script without creating audio.",
    )

    parser.add_argument(
        "--list-lessons",
        action="store_true",
        help="List available JSON lesson files in lessons/.",
    )

    parser.add_argument(
        "--create-lesson",
        type=str,
        default=None,
        help="Create a starter JSON lesson file in lessons/. Example: --create-lesson week1-day3",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow --create-lesson to overwrite an existing lesson file.",
    )

    args = parser.parse_args()

    if args.list_lessons:
        print_lesson_files()
        return

    if args.create_lesson:
        lesson_path = create_lesson_file(
            name=args.create_lesson,
            overwrite=args.overwrite,
        )
        print(f"Created lesson file: {lesson_path}")
        return

    if not args.input:
        raise SystemExit(
            "No input lesson provided. Use --input lessons/example.json, "
            "--list-lessons, or --create-lesson lesson-name."
        )

    input_path = Path(args.input)
    lesson, study_script = prepare_lesson_script(input_path)

    if args.preview_script:
        print("\n--- GENERATED STUDY SCRIPT ---\n")
        if lesson.lesson_title:
            print(f"Lesson: {lesson.lesson_title}\n")
        print(study_script)
        print("\n--- END ---\n")
        return

    result = generate_lesson_audio(
        input_path=input_path,
        output_arg=args.out,
        voice=args.voice,
    )

    print(f"\nDone: {result}")


if __name__ == "__main__":
    main()