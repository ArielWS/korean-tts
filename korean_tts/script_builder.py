from korean_tts.parser import VocabItem


def build_study_script(items: list[VocabItem]) -> str:
    blocks: list[str] = []

    for item in items:
        block = f"""
{item.korean_word}

{item.english}

{item.english_sentence}

{item.korean_sentence_informal_polite}

{item.korean_sentence_formal_polite}
""".strip()

        blocks.append(block)

    return "\n\n\n".join(blocks)


def split_script(script: str, max_chars: int) -> list[str]:
    """
    Splits the study script by vocabulary item blocks so the API receives
    manageable chunks.
    """

    blocks = [block.strip() for block in script.split("\n\n\n") if block.strip()]

    chunks: list[str] = []
    current = ""

    for block in blocks:
        candidate = f"{current}\n\n\n{block}".strip() if current else block

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current)

            if len(block) > max_chars:
                raise ValueError(
                    "A single vocabulary item is too long for one TTS chunk. "
                    "Shorten the example sentence."
                )

            current = block

    if current:
        chunks.append(current)

    return chunks