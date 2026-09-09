import os, time, uuid
from openai import OpenAI
from config import STAGE_CONFIG

def _client(api_key):
    key = (api_key or os.getenv("OPENAI_API_KEY","")).strip()
    if not key:
        raise RuntimeError("API key is missing. Configure OPENAI_API_KEY in Streamlit Secrets or enter it.")
    return OpenAI(api_key=key)

def _call(client, model, system, prompt, retries=3):
    last = None
    for attempt in range(retries):
        try:
            r = client.responses.create(model=model, instructions=system, input=prompt)
            text = r.output_text.strip()
            if not text: raise RuntimeError("AI returned an empty response.")
            return text
        except Exception as e:
            last = e
            if attempt < retries-1: time.sleep(2**attempt)
    raise RuntimeError(str(last))

def run_stage(stage, ctx, previous, api_key, model):
    cfg = STAGE_CONFIG[stage]
    prompt = f"""Topic: {ctx['topic']}
Keywords: {ctx['keywords']}
Tone: {ctx['tone']}
Language: {ctx['language']}
Audience: {ctx['audience']}
Length: {ctx['length']}
Extra instructions: {ctx['extra']}

Previous stage:
{previous or 'None'}

Task:
{cfg['task']}

Rules: be useful and original; do not invent facts; do not promise AI-detector evasion; do not imitate a living writer."""
    try:
        text = _call(_client(api_key), model, cfg["system"], prompt)
        return {"ok":True,"content":text,"key":cfg["key"]}
    except Exception as e:
        eid = uuid.uuid4().hex[:8].upper()
        return {"ok":False,"error":f"Error ID {stage[:8].upper()}-{eid}: {e}","key":cfg["key"]}
