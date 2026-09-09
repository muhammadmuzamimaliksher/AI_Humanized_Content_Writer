import os
import time
import uuid

from groq import Groq
from config import STAGE_CONFIG


def _client(api_key):
    """
    Create and return a Groq client.

    Priority:
    1. API key supplied by Streamlit
    2. GROQ_API_KEY environment variable
    """

    key = (api_key or os.getenv("GROQ_API_KEY", "")).strip()

    if not key:
        raise RuntimeError(
            "Groq API key is missing. "
            "Add GROQ_API_KEY to Streamlit Secrets."
        )

    if not key.startswith("gsk_"):
        raise RuntimeError(
            "Invalid Groq API key. "
            "A Groq API key normally starts with 'gsk_'."
        )

    return Groq(api_key=key)


def _call(client, model, system, prompt, retries=3):
    """
    Call Groq with automatic retry and exponential backoff.
    """

    last_error = None

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
                raise RuntimeError(
                    "Groq returned no response choices."
                )

            text = response.choices[0].message.content

            if not text:
                raise RuntimeError(
                    "Groq returned an empty response."
                )

            text = text.strip()

            if not text:
                raise RuntimeError(
                    "Groq returned an empty response."
                )

            return text

        except Exception as error:

            last_error = error

            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    raise RuntimeError(str(last_error))


def run_stage(stage, ctx, previous, api_key, model):

    if stage not in STAGE_CONFIG:
        return {
            "ok": False,
            "error": f"Unknown pipeline stage: {stage}",
            "key": ""
        }

    cfg = STAGE_CONFIG[stage]

    prompt = f"""
CONTENT BRIEF

Topic:
{ctx.get('topic', '')}

Keywords:
{ctx.get('keywords', '')}

Tone:
{ctx.get('tone', '')}

Language:
{ctx.get('language', '')}

Target Audience:
{ctx.get('audience', '')}

Target Length:
{ctx.get('length', '')}

Additional Instructions:
{ctx.get('extra', '')}


PREVIOUS STAGE OUTPUT

{previous or 'No previous stage output.'}


CURRENT TASK

{cfg['task']}


CONTENT RULES

- Be useful, original and reader-focused.
- Follow the requested language and tone.
- Do not invent facts, statistics, sources or quotations.
- If information is uncertain, avoid presenting it as fact.
- Avoid unnecessary repetition and filler.
- Use natural sentence variation.
- Use keywords naturally rather than stuffing them.
- Do not promise AI-detector bypass or guaranteed human detection results.
- Do not imitate a living writer.
"""

    try:

        client = _client(api_key)

        text = _call(
            client=client,
            model=model,
            system=cfg["system"],
            prompt=prompt
        )

        return {
            "ok": True,
            "content": text,
            "key": cfg["key"]
        }

    except Exception as error:

        error_id = uuid.uuid4().hex[:8].upper()

        return {
            "ok": False,
            "error": (
                f"Error ID "
                f"{stage[:8].upper()}-{error_id}: "
                f"{error}"
            ),
            "key": cfg["key"]
        }
