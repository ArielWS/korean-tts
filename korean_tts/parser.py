from dataclasses import dataclass


@dataclass
class VocabItem:
    korean_word: str
    english: str
    korean_sentence: str
    english_sentence: str


def _clean_cell(value: str) -> str:
    return value.strip().replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ")


def parse_markdown_table(text: str) -> list[VocabItem]:
    """
    Parses a copied ChatGPT markdown table like:

    | Korean word | English | Korean sentence | English sentence |
    |---|---|---|---|
    | 공장 | factory | 그 공장은 오래됐어요. | That factory is old. |
    """

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    table_lines = [line for line in lines if line.startswith("|") and line.endswith("|")]

    if not table_lines:
        raise ValueError("No markdown table found. Copy the table including the | column separators.")

    rows: list[list[str]] = []

    for line in table_lines:
        cells = [_clean_cell(cell) for cell in line.strip("|").split("|")]

        # Skip separator row: |---|---|---|
        if all(set(cell.replace(":", "").replace("-", "").strip()) == set() for cell in cells):
            continue

        rows.append(cells)

    if len(rows) < 2:
        raise ValueError("The table needs a header row and at least one vocabulary row.")

    header = [h.lower() for h in rows[0]]
    data_rows = rows[1:]

    items: list[VocabItem] = []

    for i, row in enumerate(data_rows, start=1):
        if len(row) < 4:
            raise ValueError(f"Row {i} has fewer than 4 columns: {row}")

        item = VocabItem(
            korean_word=row[0],
            english=row[1],
            korean_sentence=row[2],
            english_sentence=row[3],
        )

        if not item.korean_word or not item.english or not item.korean_sentence or not item.english_sentence:
            raise ValueError(f"Row {i} contains an empty required field: {row}")

        items.append(item)

    return items