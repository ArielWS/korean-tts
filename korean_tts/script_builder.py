from korean_tts.parser import VocabItem


def build_study_script(items: list[VocabItem]) -> str:
    blocks: list[str] = []

    for index, item in enumerate(items, start=1):
        block = f"""
Item {index}.

{item.korean_word}

{item.english}

{item.korean_sentence}

{item.english_sentence}

Pause.
""".strip()

        blocks.append(block)

    return "\n\n".join(blocks)


def split_script(script: str, max_chars: int) -> list[str]:
    """
    Splits by vocabulary item blocks so the API receives manageable chunks.
    """
    blocks = [block.strip() for block in script.split("\n\nItem ") if block.strip()]

    normalized_blocks = []
    for i, block in enumerate(blocks):
        if i == 0 and block.startswith("Item "):
            normalized_blocks.append(block)
        else:
            normalized_blocks.append("Item " + block)

    chunks: list[str] = []
    current = ""

    for block in normalized_blocks:
        candidate = f"{current}\n\n{block}".strip() if current else block

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = block

    if current:
        chunks.append(current)

    return chunks