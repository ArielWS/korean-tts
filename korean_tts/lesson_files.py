import json
import re
from pathlib import Path

from korean_tts.config import LESSONS_DIR, OUTPUT_DIR


LESSON_TEMPLATE = {
    "lesson_title": "New Lesson",
    "items": [
        {
            "english": "factory",
            "korean_word": "공장",
            "english_sentence": "That factory is old.",
            "korean_sentence_informal_polite": "그 공장은 오래됐어요.",
            "korean_sentence_formal_polite": "그 공장은 오래되었습니다."
        }
    ]
}


def normalise_lesson_filename(name: str) -> str:
    """
    Converts a user-provided lesson name into a safe JSON filename.

    Example:
    'Week 1 Day 3' -> 'week-1-day-3.json'
    """

    cleaned = name.strip().lower()
    cleaned = re.sub(r"[^a-z0-9가-힣_-]+", "-", cleaned)
    cleaned = cleaned.strip("-")

    if not cleaned:
        raise ValueError("Lesson filename cannot be empty.")

    if not cleaned.endswith(".json"):
        cleaned = f"{cleaned}.json"

    return cleaned


def list_lesson_files(lessons_dir: Path = LESSONS_DIR) -> list[Path]:
    """
    Returns all JSON lesson files in the lessons directory.
    """

    if not lessons_dir.exists():
        return []

    return sorted(lessons_dir.glob("*.json"))


def create_lesson_file(
    name: str,
    lessons_dir: Path = LESSONS_DIR,
    overwrite: bool = False,
) -> Path:
    """
    Creates a starter lesson JSON file in the lessons directory.
    """

    lessons_dir.mkdir(parents=True, exist_ok=True)

    filename = normalise_lesson_filename(name)
    lesson_path = lessons_dir / filename

    if lesson_path.exists() and not overwrite:
        raise FileExistsError(
            f"Lesson file already exists: {lesson_path}. "
            "Use a different name or enable overwrite."
        )

    lesson_path.write_text(
        json.dumps(LESSON_TEMPLATE, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return lesson_path


def resolve_output_path(
    input_path: Path,
    output_arg: str | None = None,
    output_dir: Path = OUTPUT_DIR,
) -> Path:
    """
    Resolves the final MP3 output path.

    If no output is provided:
    lessons/week1-day1.json -> outputs/week1-day1.mp3

    If output is just a filename:
    custom.mp3 -> outputs/custom.mp3

    If output is a path:
    custom_outputs/custom.mp3 -> custom_outputs/custom.mp3
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    if output_arg is None:
        return output_dir / f"{input_path.stem}.mp3"

    output_path = Path(output_arg)

    if output_path.suffix.lower() != ".mp3":
        output_path = output_path.with_suffix(".mp3")

    if output_path.parent == Path("."):
        output_path = output_dir / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    return output_path