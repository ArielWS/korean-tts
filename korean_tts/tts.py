import subprocess
import tempfile
from pathlib import Path

from openai import OpenAI

from korean_tts.config import (
    DEFAULT_MODEL,
    DEFAULT_RESPONSE_FORMAT,
    DEFAULT_VOICE,
    MAX_CHARS_PER_CHUNK,
    OUTPUT_DIR,
    TTS_INSTRUCTIONS,
)
from korean_tts.script_builder import split_script


def generate_speech_chunks(
    script: str,
    output_path: Path,
    voice: str = DEFAULT_VOICE,
    model: str = DEFAULT_MODEL,
) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = OpenAI()
    chunks = split_script(script, MAX_CHARS_PER_CHUNK)

    if not chunks:
        raise ValueError("No text chunks were generated.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        chunk_paths: list[Path] = []

        for index, chunk in enumerate(chunks, start=1):
            chunk_path = tmpdir_path / f"chunk_{index:03d}.mp3"

            print(f"Generating chunk {index}/{len(chunks)}...")

            with client.audio.speech.with_streaming_response.create(
                model=model,
                voice=voice,
                input=chunk,
                instructions=TTS_INSTRUCTIONS,
                response_format=DEFAULT_RESPONSE_FORMAT,
            ) as response:
                response.stream_to_file(chunk_path)

            chunk_paths.append(chunk_path)

        if len(chunk_paths) == 1:
            output_path.write_bytes(chunk_paths[0].read_bytes())
            return output_path

        concat_file = tmpdir_path / "concat.txt"
        concat_file.write_text(
            "\n".join(f"file '{path.as_posix()}'" for path in chunk_paths),
            encoding="utf-8",
        )

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-codec:a",
                "libmp3lame",
                "-q:a",
                "2",
                str(output_path),
            ],
            check=True,
        )

    return output_path