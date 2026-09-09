import streamlit as st
from config import APP_NAME, STAGES, STAGE_CONFIG
from ai_engine import run_stage
from utils import validate_brief, word_count, content_score

st.set_page_config(page_title=APP_NAME, page_icon="✍️", layout="wide")

if "project" not in st.session_state:
    st.session_state.project = {v["key"]: "" for v in STAGE_CONFIG.values()}
if "status" not in st.session_state:
    st.session_state.status = {s: "Not Started" for s in STAGES}

st.title("✍️ AI Humanized Content Writer")
st.caption("8-stage pipeline: Analyze → Intent → Outline → Draft → Humanize → SEO → QA → Final")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    model = st.text_input("AI Model", value="gpt-4o-mini")
    tone = st.selectbox("Tone", ["Professional","Conversational","Friendly","Persuasive","Educational"])
    language = st.selectbox("Language", ["English","Urdu","Roman Urdu","Arabic","Persian"])
    audience = st.text_input("Target Audience", "General readers")
    length = st.selectbox("Target Length", ["Short (300–500)","Medium (700–1,000)","Long (1,500–2,000)"])

st.subheader("1. Content Brief")
topic = st.text_area("Topic / Brief", height=120)
keywords = st.text_input("Primary & Secondary Keywords")
extra = st.text_area("Additional Instructions", height=100)

def context():
    return {"topic":topic,"keywords":keywords,"tone":tone,"language":language,
            "audience":audience,"length":length,"extra":extra}

if st.button("🚀 Run Full Pipeline", type="primary"):
    errors = validate_brief(topic, keywords)
    if errors:
        for e in errors: st.error(e)
    else:
        progress = st.progress(0)
        previous = ""
        for i, stage in enumerate(STAGES):
            st.info(f"Running Stage {i+1}/8: {stage}")
            result = run_stage(stage, context(), previous, api_key, model)
            if not result["ok"]:
                st.session_state.status[stage] = "Error"
                st.error(result["error"])
                st.warning("Completed stages are preserved. Fix the problem and use Retry.")
                break
            st.session_state.status[stage] = "Completed"
            st.session_state.project[result["key"]] = result["content"]
            previous = result["content"]
            progress.progress((i+1)/len(STAGES))
        else:
            st.success("All 8 stages completed successfully.")

st.subheader("2. Pipeline")
for i, stage in enumerate(STAGES, 1):
    status = st.session_state.status[stage]
    icon = "✅" if status=="Completed" else "❌" if status=="Error" else "⏳"
    key = STAGE_CONFIG[stage]["key"]
    with st.expander(f"{icon} Stage {i} — {stage} [{status}]", expanded=stage=="Final Editor"):
        value = st.text_area("Output", st.session_state.project[key], height=260, key=f"edit_{key}")
        st.session_state.project[key] = value
        if st.button(f"↻ Retry {stage}", key=f"retry_{i}"):
            result = run_stage(stage, context(), value, api_key, model)
            if result["ok"]:
                st.session_state.project[key] = result["content"]
                st.session_state.status[stage] = "Completed"
                st.success("Stage regenerated.")
                st.rerun()
            else:
                st.error(result["error"])

final_text = st.session_state.project["final"]
if final_text:
    st.subheader("3. Final Report")
    a,b = st.columns(2)
    a.metric("Word Count", word_count(final_text))
    b.metric("Content Score", f"{content_score(final_text)}/100")
    st.download_button("⬇️ Download TXT", final_text, "final_content.txt", "text/plain")

st.divider()
st.caption("Responsible-use: improves natural, reader-first writing; no AI-detector bypass guarantee.")
