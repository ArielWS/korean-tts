from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = PROJECT_ROOT / "lessons"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

DEFAULT_MODEL = "gpt-4o-mini-tts"
DEFAULT_VOICE = "marin"
DEFAULT_RESPONSE_FORMAT = "mp3"

# Conservative chunk size. The model limit is token-based, but this avoids
# sending very large 50-word lesson scripts in one request.
MAX_CHARS_PER_CHUNK = 2500

TTS_INSTRUCTIONS = """
You are generating Korean vocabulary study audio.

Read Korean in clear, standard Seoul Korean pronunciation.
Use a neutral adult voice.
Do not act, dramatize, emote, or exaggerate intonation.
Read Korean slightly slower than normal conversation, but still naturally.
Read English clearly and neutrally.
Preserve the text exactly. Do not translate, explain, skip, or add anything.
Use brief pauses between lines and a slightly longer pause between vocabulary items.
"""