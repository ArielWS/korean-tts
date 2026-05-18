from pathlib import Path

from korean_tts.config import DEFAULT_VOICE
from korean_tts.lesson_files import resolve_output_path
from korean_tts.parser import Lesson, load_lesson_json
from korean_tts.script_builder import build_study_script
from korean_tts.tts import generate_speech_chunks


def prepare_lesson_script(input_path: str | Path) -> tuple[Lesson, str]:
    """
    Loads a lesson JSON file and builds the TTS-ready study script.
    """

    lesson = load_lesson_json(input_path)
    study_script = build_study_script(lesson.items)

    return lesson, study_script


def generate_lesson_audio(
    input_path: str | Path,
    output_arg: str | None = None,
    voice: str = DEFAULT_VOICE,
) -> Path:
    """
    Generates one MP3 file from one lesson JSON file.
    """

    input_path = Path(input_path)
    _lesson, study_script = prepare_lesson_script(input_path)

    output_path = resolve_output_path(
        input_path=input_path,
        output_arg=output_arg,
    )

    return generate_speech_chunks(
        script=study_script,
        output_path=output_path,
        voice=voice,
    )