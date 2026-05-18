from pathlib import Path

import streamlit as st

from korean_tts.config import DEFAULT_VOICE, OUTPUT_DIR
from korean_tts.lesson_files import create_lesson_file, list_lesson_files, resolve_output_path
from korean_tts.workflow import generate_lesson_audio, prepare_lesson_script


VOICE_OPTIONS = ["marin", "cedar"]


st.set_page_config(
    page_title="Korean Vocabulary TTS",
    page_icon="🎧",
    layout="wide",
)


st.title("Korean Vocabulary TTS")
st.caption("Generate Korean vocabulary study MP3s from local JSON lesson files.")


with st.sidebar:
    st.header("Lesson files")

    new_lesson_name = st.text_input(
        "Create new lesson file",
        placeholder="e.g. 2026-05-18-week1-day1",
    )

    overwrite = st.checkbox("Overwrite if file exists", value=False)

    if st.button("Create lesson file"):
        if not new_lesson_name.strip():
            st.error("Enter a lesson filename first.")
        else:
            try:
                created_path = create_lesson_file(
                    name=new_lesson_name,
                    overwrite=overwrite,
                )
                st.success(f"Created: {created_path.name}")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    st.divider()

    refresh = st.button("Refresh lesson list")


lesson_files = list_lesson_files()

if not lesson_files:
    st.warning("No lesson JSON files found in lessons/. Create one from the sidebar first.")
    st.stop()


lesson_labels = [path.name for path in lesson_files]

selected_label = st.selectbox(
    "Select lesson file",
    lesson_labels,
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
    output_filename = st.text_input(
        "Output filename",
        value=default_output_path.name,
        help="If you enter only a filename, the MP3 is saved in outputs/.",
    )

    resolved_output_path = resolve_output_path(
        input_path=selected_path,
        output_arg=output_filename,
    )

    st.write(f"**Output path:** `{resolved_output_path}`")

    with st.expander("Preview generated study script", expanded=False):
        st.text_area(
            "Study script",
            value=study_script,
            height=350,
            disabled=True,
            label_visibility="collapsed",
        )

    generate_clicked = st.button("Generate MP3", type="primary")

    if generate_clicked:
        try:
            with st.spinner("Generating MP3..."):
                final_path = generate_lesson_audio(
                    input_path=selected_path,
                    output_arg=output_filename,
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
    st.info("No MP3 exists yet for the selected output filename.")