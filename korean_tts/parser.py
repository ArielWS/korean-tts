import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VocabItem:
    korean_word: str
    english: str
    korean_sentence_informal_polite: str
    korean_sentence_formal_polite: str
    english_sentence: str


@dataclass
class Lesson:
    lesson_title: str | None
    items: list[VocabItem]


REQUIRED_ITEM_FIELDS = [
    "korean_word",
    "english",
    "korean_sentence_informal_polite",
    "korean_sentence_formal_polite",
    "english_sentence",
]


def load_lesson_json(path: str | Path) -> Lesson:
    lesson_path = Path(path)

    if not lesson_path.exists():
        raise FileNotFoundError(f"Lesson file not found: {lesson_path}")

    try:
        data = json.loads(lesson_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {lesson_path}: {exc}") from exc

    if "items" not in data:
        raise ValueError("Lesson JSON must contain an 'items' field.")

    if not isinstance(data["items"], list) or not data["items"]:
        raise ValueError("'items' must be a non-empty list.")

    items: list[VocabItem] = []

    for index, raw_item in enumerate(data["items"], start=1):
        if not isinstance(raw_item, dict):
            raise ValueError(f"Item {index} must be an object.")

        missing = [field for field in REQUIRED_ITEM_FIELDS if not raw_item.get(field)]
        if missing:
            raise ValueError(f"Item {index} is missing required fields: {', '.join(missing)}")

        items.append(
            VocabItem(
                korean_word=raw_item["korean_word"].strip(),
                english=raw_item["english"].strip(),
                korean_sentence_informal_polite=raw_item["korean_sentence_informal_polite"].strip(),
                korean_sentence_formal_polite=raw_item["korean_sentence_formal_polite"].strip(),
                english_sentence=raw_item["english_sentence"].strip(),
            )
        )

    return Lesson(
        lesson_title=data.get("lesson_title"),
        items=items,
    )