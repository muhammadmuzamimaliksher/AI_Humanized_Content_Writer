import streamlit as st

from config import APP_NAME, STAGES, STAGE_CONFIG, AVAILABLE_MODELS
from ai_engine import run_stage
from utils import validate_brief, word_count, content_score


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title=APP_NAME,
    page_icon="✍️",
    layout="wide"
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "project" not in st.session_state:
    st.session_state.project = {
        cfg["key"]: ""
        for cfg in STAGE_CONFIG.values()
    }

if "status" not in st.session_state:
    st.session_state.status = {
        stage: "Not Started"
        for stage in STAGES
    }


# ---------------------------------------------------------
# API KEY
# ---------------------------------------------------------

if "GROQ_API_KEY" not in st.secrets:

    st.error(
        "GROQ_API_KEY is missing from Streamlit Secrets."
    )

    st.info(
        'Add this to Streamlit Secrets:\n\n'
        'GROQ_API_KEY = "gsk_your_api_key_here"'
    )

    st.stop()


GROQ_API_KEY = st.secrets["GROQ_API_KEY"]


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("✍️ AI Humanized Content Writer")

st.caption(
    "8-stage AI workflow: "
    "Analyze → Intent → Outline → Draft → "
    "Humanize → SEO → QA → Final"
)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:
    st.header("Settings")

    model = st.selectbox(
        "AI Model",
        AVAILABLE_MODELS,
        index=0
    )

    tone = st.selectbox(
        "Tone",
        [
            "Professional",
            "Conversational",
            "Friendly",
            "Persuasive",
            "Educational"
        ]
    )

    language = st.selectbox(
        "Language",
        [
            "English",
            "Urdu",
            "Roman Urdu",
            "Arabic",
            "Persian"
        ]
    )

    audience = st.text_input(
        "Target Audience",
        "General readers"
    )

    length = st.selectbox(
        "Target Length",
        [
            "Short (300–500)",
            "Medium (700–1,000)",
            "Long (1,500–2,000)"
        ]
    )

    st.divider()

    st.success("Groq API: Connected")


# ---------------------------------------------------------
# CONTENT BRIEF
# ---------------------------------------------------------

st.subheader("1. Content Brief")

topic = st.text_area(
    "Topic / Content Brief",
    height=130,
    placeholder=(
        "Example: Write a detailed article about "
        "Local SEO strategies for small businesses."
    )
)

keywords = st.text_input(
    "Primary & Secondary Keywords",
    placeholder=(
        "local SEO, Google Maps ranking, "
        "Google Business Profile"
    )
)

extra = st.text_area(
    "Additional Instructions",
    height=100,
    placeholder=(
        "Add any special instructions, "
        "structure requirements or points to cover."
    )
)


# ---------------------------------------------------------
# CONTEXT
# ---------------------------------------------------------

def get_context():

    return {
        "topic": topic,
        "keywords": keywords,
        "tone": tone,
        "language": language,
        "audience": audience,
        "length": length,
        "extra": extra
    }


# ---------------------------------------------------------
# RUN FULL PIPELINE
# ---------------------------------------------------------

if st.button(
    "🚀 Run Full Pipeline",
    type="primary",
    use_container_width=True
):

    errors = validate_brief(
        topic,
        keywords
    )

    if errors:

        for error in errors:
            st.error(error)

    else:

        progress = st.progress(0)
        status_box = st.empty()

        previous = ""

        for i, stage in enumerate(STAGES):

            status_box.info(
                f"Running Stage {i + 1}/{len(STAGES)}: {stage}"
            )

            result = run_stage(
                stage=stage,
                ctx=get_context(),
                previous=previous,
                api_key=GROQ_API_KEY,
                model=model
            )

            if not result["ok"]:

                st.session_state.status[stage] = "Error"

                st.error(result["error"])

                st.warning(
                    "Previous completed stages have been preserved. "
                    "Fix the problem and use the Retry button."
                )

                break

            st.session_state.status[stage] = "Completed"

            st.session_state.project[
                result["key"]
            ] = result["content"]

            previous = result["content"]

            progress.progress(
                (i + 1) / len(STAGES)
            )

        else:

            status_box.success(
                "All 8 stages completed successfully."
            )


# ---------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------

st.subheader("2. AI Pipeline")

for i, stage in enumerate(STAGES, 1):

    status = st.session_state.status[stage]

    if status == "Completed":
        icon = "✅"

    elif status == "Error":
        icon = "❌"

    else:
        icon = "⏳"

    key = STAGE_CONFIG[stage]["key"]

    with st.expander(
        f"{icon} Stage {i} — {stage} [{status}]",
        expanded=(stage == "Final Editor")
    ):

        current_value = st.session_state.project[key]

        edited_value = st.text_area(
            "Stage Output",
            value=current_value,
            height=280,
            key=f"output_{key}"
        )

        st.session_state.project[key] = edited_value

        if st.button(
            f"↻ Retry {stage}",
            key=f"retry_{i}"
        ):

            result = run_stage(
                stage=stage,
                ctx=get_context(),
                previous=edited_value,
                api_key=GROQ_API_KEY,
                model=model
            )

            if result["ok"]:

                st.session_state.project[key] = (
                    result["content"]
                )

                st.session_state.status[stage] = "Completed"

                st.success(
                    f"{stage} regenerated successfully."
                )

                st.rerun()

            else:

                st.error(
                    result["error"]
                )


# ---------------------------------------------------------
# FINAL REPORT
# ---------------------------------------------------------

final_text = st.session_state.project.get(
    "final",
    ""
)


if final_text:

    st.subheader("3. Final Report")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Word Count",
        word_count(final_text)
    )

    col2.metric(
        "Content Score",
        f"{content_score(final_text)}/100"
    )

    completed = sum(
        1
        for status in st.session_state.status.values()
        if status == "Completed"
    )

    col3.metric(
        "Stages Completed",
        f"{completed}/{len(STAGES)}"
    )

    st.download_button(
        "⬇️ Download TXT",
        data=final_text,
        file_name="final_content.txt",
        mime="text/plain",
        use_container_width=True
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.caption(
    "Responsible-use: improves natural, reader-first writing. "
    "No AI-detector bypass guarantee."
)
