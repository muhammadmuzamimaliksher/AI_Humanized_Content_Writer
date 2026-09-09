import os
import time
import uuid

from groq import Groq
from config import STAGE_CONFIG


def _client(api_key):
    """
    Create a Groq API client.
    Priority:
    1. API key passed from Streamlit
    2. GROQ_API_KEY environment variable
    """

    key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()

    if not key:
        raise RuntimeError(
            "Groq API key is missing. "
            "Configure GROQ_API_KEY in Streamlit Secrets."
        )

    if not key.startswith("gsk_"):
        raise RuntimeError(
            "Invalid Groq API key format. "
            "Your Groq key should normally start with 'gsk_'."
        )

    return Groq(api_key=key)


def _call(client, model, system, prompt, retries=3):
    """
    Send a request to Groq with automatic retries.
    """

    last = None

    for attempt in range(retries):
        try:

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )

            if not response.choices:
                raise RuntimeError("Groq returned no choices.")

            text = response.choices[0].message.content

            if not text:
                raise RuntimeError("Groq returned an empty response.")

            text = text.strip()

            if not text:
                raise RuntimeError("Groq returned an empty response.")

            return text

        except Exception as e:
            last = e

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    raise RuntimeError(str(last))


def run_stage(stage, ctx, previous, api_key, model):

    if stage not in STAGE_CONFIG:
        raise RuntimeError(f"Unknown stage: {stage}")

    cfg = STAGE_CONFIG[stage]

    prompt = f"""
Topic: {ctx['topic']}

Keywords:
{ctx['keywords']}

Tone:
{ctx['tone']}

Language:
{ctx['language']}

Audience:
{ctx['audience']}

Length:
{ctx['length']}

Extra instructions:
{ctx['extra']}

Previous stage:
{previous or 'None'}

Task:
{cfg['task']}

Rules:
- Be useful and original.
- Do not invent facts.
- Do not promise AI-detector evasion.
- Do not imitate a living writer.
- Write naturally and clearly.
"""

    try:

        client = _client(api_key)

        text = _call(
            client,
            model,
            cfg["system"],
            prompt
        )

        return {
            "ok": True,
            "content": text,
            "key": cfg["key"]
        }

    except Exception as e:

        eid = uuid.uuid4().hex[:8].upper()

        return {
            "ok": False,
            "error": (
                f"Error ID "
                f"{stage[:8].upper()}-{eid}: {e}"
            ),
            "key": cfg["key"]
        }
