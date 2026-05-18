from pathlib import Path
import json
import tempfile

import streamlit as st

from korean_tts.config import DEFAULT_VOICE, LESSONS_DIR
from korean_tts.lesson_files import list_lesson_files, normalise_lesson_filename, resolve_output_path
from korean_tts.parser import load_lesson_json
from korean_tts.workflow import generate_lesson_audio, prepare_lesson_script


VOICE_OPTIONS = ["marin", "cedar"]


EXAMPLE_JSON = {
    "lesson_title": "Example Lesson",
    "items": [
        {
            "korean_word": "공장",
            "english": "factory",
            "korean_sentence_informal_polite": "그 공장은 오래됐어요.",
            "korean_sentence_formal_polite": "그 공장은 오래되었습니다.",
            "english_sentence": "That factory is old."
        }
    ]
}


def validate_lesson_json_text(raw_json: str) -> dict:
    """
    Validates pasted lesson JSON before writing it into lessons/.
    """

    if not raw_json.strip():
        raise ValueError("Paste lesson JSON before saving.")

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "lesson.json"
        tmp_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # Reuse the existing parser validation.
        load_lesson_json(tmp_path)

    return data


def save_pasted_lesson_json(
    lesson_name: str,
    raw_json: str,
    overwrite: bool,
) -> Path:
    """
    Saves pasted lesson JSON into lessons/ after validating it.
    """

    if not lesson_name.strip():
        raise ValueError("Enter a lesson filename.")

    lesson_data = validate_lesson_json_text(raw_json)

    LESSONS_DIR.mkdir(parents=True, exist_ok=True)

    filename = normalise_lesson_filename(lesson_name)
    lesson_path = LESSONS_DIR / filename

    if lesson_path.exists() and not overwrite:
        raise FileExistsError(
            f"Lesson file already exists: {lesson_path.name}. "
            "Enable overwrite or choose another name."
        )

    lesson_path.write_text(
        json.dumps(lesson_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return lesson_path


st.set_page_config(
    page_title="Korean Vocabulary TTS",
    page_icon="🎧",
    layout="wide",
)


st.title("Korean Vocabulary TTS")
st.caption("Paste a lesson JSON file, save it locally, then generate an MP3.")


with st.sidebar:
    st.header("Add lesson")

    lesson_name = st.text_input(
        "Lesson filename",
        placeholder="e.g. 2026-05-18-week1-day1",
    )

    pasted_json = st.text_area(
        "Paste lesson JSON",
        value=json.dumps(EXAMPLE_JSON, ensure_ascii=False, indent=2),
        height=360,
    )

    overwrite = st.checkbox("Overwrite if file exists", value=False)

    if st.button("Save lesson JSON", type="primary"):
        try:
            saved_path = save_pasted_lesson_json(
                lesson_name=lesson_name,
                raw_json=pasted_json,
                overwrite=overwrite,
            )

            st.session_state["selected_lesson_name"] = saved_path.name
            st.success(f"Saved: {saved_path.name}")
            st.rerun()

        except Exception as exc:
            st.error(str(exc))

    st.divider()

    if st.button("Refresh lesson list"):
        st.rerun()


lesson_files = list_lesson_files()

if not lesson_files:
    st.warning("No lesson JSON files found in lessons/. Paste and save a lesson in the sidebar.")
    st.stop()


lesson_labels = [path.name for path in lesson_files]

default_index = 0
if "selected_lesson_name" in st.session_state:
    if st.session_state["selected_lesson_name"] in lesson_labels:
        default_index = lesson_labels.index(st.session_state["selected_lesson_name"])

selected_label = st.selectbox(
    "Select lesson file",
    lesson_labels,
    index=default_index,
)

selected_path = lesson_files[lesson_labels.index(selected_label)]


left_col, right_col = st.columns([1, 1])


with left_col:
    st.subheader("Lesson preview")

    try:
        lesson, study_script = prepare_lesson_script(selected_path)

        st.write(f"**File:** `{selected_path}`")

        if lesson.lesson_title:
            st.write(f"**Lesson title:** {lesson.lesson_title}")

        st.write(f"**Items:** {len(lesson.items)}")

        st.dataframe(
            [
                {
                    "Korean word": item.korean_word,
                    "English": item.english,
                    "Informal polite": item.korean_sentence_informal_polite,
                    "Formal polite": item.korean_sentence_formal_polite,
                    "English sentence": item.english_sentence,
                }
                for item in lesson.items
            ],
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:
        st.error(f"Could not load lesson file: {exc}")
        st.stop()


with right_col:
    st.subheader("Audio settings")

    voice = st.selectbox(
        "Voice",
        VOICE_OPTIONS,
        index=VOICE_OPTIONS.index(DEFAULT_VOICE) if DEFAULT_VOICE in VOICE_OPTIONS else 0,
    )

    default_output_path = resolve_output_path(selected_path)

    st.write("**Output filename:**")
    st.code(default_output_path.name)

    st.write("**Output path:**")
    st.code(str(default_output_path))

    with st.expander("Advanced: custom output filename", expanded=False):
        custom_output_filename = st.text_input(
            "Custom output filename",
            value="",
            placeholder=default_output_path.name,
            help="Leave blank to use the lesson filename.",
        )

    output_arg = custom_output_filename.strip() or None
    resolved_output_path = resolve_output_path(
        input_path=selected_path,
        output_arg=output_arg,
    )

    with st.expander("Preview generated study script", expanded=False):
        st.text_area(
            "Study script",
            value=study_script,
            height=350,
            disabled=True,
            label_visibility="collapsed",
        )

    if st.button("Generate MP3", type="primary"):
        try:
            with st.spinner("Generating MP3..."):
                final_path = generate_lesson_audio(
                    input_path=selected_path,
                    output_arg=output_arg,
                    voice=voice,
                )

            st.success(f"Generated: {final_path}")

        except Exception as exc:
            st.error(f"Failed to generate MP3: {exc}")


st.divider()

st.subheader("Generated audio")

existing_output_path = Path(resolved_output_path)

if existing_output_path.exists():
    st.audio(str(existing_output_path))

    with existing_output_path.open("rb") as audio_file:
        st.download_button(
            label="Download MP3",
            data=audio_file,
            file_name=existing_output_path.name,
            mime="audio/mpeg",
        )
else:
    st.info("No MP3 exists yet for the selected lesson/output filename.")