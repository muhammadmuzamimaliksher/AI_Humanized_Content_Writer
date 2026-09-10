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
def run_paragraph_rewrite(
    paragraph,
    style,
    preserve_meaning,
    improve_readability,
    remove_repetition,
    additional_instructions,
    api_key,
    model
):
    """
    Rewrite/humanize a single paragraph.
    """

    
    preserve_keywords = st.text_input(
    "Keywords / Terms to Preserve",
    placeholder="Example: Google Maps SEO, local SEO, Google Business Profile"
    )
    
    system_prompt = f"""
You are an expert human editor and rewriting specialist.

Your job is to improve the provided paragraph so it reads naturally,
clearly, and professionally.

The goal is reader-first writing, not AI-detector evasion.

Do not:
- Invent facts
- Add unsupported statistics
- Add fake citations
- Change factual meaning
- Add information that was not provided
- Imitate a living writer
- Promise AI-detector bypass
Keywords / terms to preserve:

{preserve_keywords or "None"}

Do not remove or unnecessarily replace these terms.
Use them naturally.
Return ONLY the rewritten paragraph.
Do not explain your changes.
"""

    user_prompt = f"""
ORIGINAL PARAGRAPH:

{paragraph}


REWRITE STYLE:

{style}


REQUIREMENTS:

Preserve original meaning:
{preserve_meaning}

Improve readability:
{improve_readability}

Remove repetition and filler:
{remove_repetition}

Additional instructions:
{additional_instructions or "None"}


REWRITE THE PARAGRAPH NOW.

Important:
Keep the rewrite focused on the original topic.
Do not add unrelated information.
Return only the final rewritten paragraph.
"""
rewrite_level = st.select_slider(
    "Rewrite Intensity",
    options=[
        "Light",
        "Balanced",
        "Deep"
    ],
    value="Balanced"
)
    try:

        client = create_client(api_key)

        content = call_groq(
            client=client,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            retries=3
        )

        return {
            "ok": True,
            "content": content
        }

    except Exception as error:

        error_id = uuid.uuid4().hex[:8].upper()

        return {
            "ok": False,
            "error": (
                f"PARAGRAPH-REWRITE-{error_id}: "
                f"{str(error)}"
            )
        }
