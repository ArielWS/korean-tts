from pathlib import Path
import json
import tempfile

import streamlit as st

from korean_tts.config import DEFAULT_VOICE, LESSONS_DIR
from korean_tts.lesson_files import list_lesson_files, normalise_lesson_filename, resolve_output_path
from korean_tts.parser import load_lesson_json
from korean_tts.workflow import generate_lesson_audio, prepare_lesson_script


VOICE_OPTIONS = ["marin", "cedar"]
ICON_PATH = Path("assets/korean_tts_icon.png")


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
        load_lesson_json(tmp_path)

    return data


def save_pasted_lesson_json(
    lesson_name: str,
    raw_json: str,
    overwrite: bool,
) -> Path:
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
    page_icon=str(ICON_PATH) if ICON_PATH.exists() else "🎧",
    layout="wide",
)


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1180px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        background: #F4E8D8;
        border-right: 1px solid rgba(47, 93, 80, 0.15);
    }

    h1, h2, h3 {
        letter-spacing: -0.03em;
    }

    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(47, 93, 80, 0.18);
        border-radius: 14px;
        box-shadow: 0 8px 24px rgba(47, 93, 80, 0.05);
        margin-bottom: 1rem;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    .korean-tts-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }

    .korean-tts-header img {
        width: 76px;
        height: 76px;
        object-fit: contain;
        border-radius: 20px;
        background: #FFF9EF;
        border: 1px solid rgba(47, 93, 80, 0.15);
    }

    .korean-tts-kicker {
        color: #2F5D50;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .korean-tts-muted {
        color: #6F685F;
        font-size: 0.95rem;
    }

    .stButton > button[kind="primary"] {
        border-radius: 10px;
        font-weight: 700;
    }

    code {
        white-space: pre-wrap !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if ICON_PATH.exists():
    st.markdown('<div class="korean-tts-header">', unsafe_allow_html=True)
    col_icon, col_title = st.columns([0.09, 0.91], vertical_alignment="center")
    with col_icon:
        st.image(str(ICON_PATH), width=72)
    with col_title:
        st.markdown('<div class="korean-tts-kicker">Daily Korean audio builder</div>', unsafe_allow_html=True)
        st.title("Korean Vocabulary TTS")
        st.markdown(
            '<div class="korean-tts-muted">Paste lesson JSON, save it locally, then generate one clean MP3 for practice.</div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.title("Korean Vocabulary TTS")
    st.caption("Paste lesson JSON, save it locally, then generate one clean MP3 for practice.")


with st.sidebar:
    st.header("Add lesson")

    lesson_name = st.text_input(
        "Lesson filename",
        placeholder="e.g. 2026-05-18-week1-day1",
    )

    pasted_json = st.text_area(
        "Paste lesson JSON",
        value=json.dumps(EXAMPLE_JSON, ensure_ascii=False, indent=2),
        height=390,
    )

    overwrite = st.checkbox("Overwrite if file exists", value=False)

    if st.button("Save lesson JSON", type="primary", use_container_width=True):
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

    if st.button("Refresh lesson list", use_container_width=True):
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


with st.expander("📁 1. Select lesson file", expanded=True):
    selected_label = st.selectbox(
        "Lesson file",
        lesson_labels,
        index=default_index,
        label_visibility="collapsed",
    )

selected_path = lesson_files[lesson_labels.index(selected_label)]


try:
    lesson, study_script = prepare_lesson_script(selected_path)
except Exception as exc:
    st.error(f"Could not load lesson file: {exc}")
    st.stop()


with st.expander("🧾 2. Lesson preview", expanded=True):
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
        height=320,
    )


with st.expander("🎙️ 3. Audio settings", expanded=True):
    voice = st.selectbox(
        "Voice",
        VOICE_OPTIONS,
        index=VOICE_OPTIONS.index(DEFAULT_VOICE) if DEFAULT_VOICE in VOICE_OPTIONS else 0,
    )

    default_output_path = resolve_output_path(selected_path)

    st.write("**Output filename**")
    st.code(default_output_path.name)

    st.write("**Output path**")
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



with st.expander("🎧 4. Generate audio", expanded=True):
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