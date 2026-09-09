import re


# ---------------------------------------------------------
# VALIDATION
# ---------------------------------------------------------

def validate_brief(topic, keywords):

    errors = []

    topic = (topic or "").strip()
    keywords = (keywords or "").strip()

    if not topic:

        errors.append(
            "Please enter a content topic or brief."
        )

    elif len(topic) < 10:

        errors.append(
            "Topic/brief must contain at least 10 characters."
        )

    elif len(topic) > 10000:

        errors.append(
            "Topic/brief is too long. "
            "Please keep it under 10,000 characters."
        )

    if len(keywords) > 3000:

        errors.append(
            "Keyword list is too long. "
            "Please keep it under 3,000 characters."
        )

    return errors


# ---------------------------------------------------------
# WORD COUNT
# ---------------------------------------------------------

def word_count(text):

    if not text:
        return 0

    return len(
        re.findall(
            r"\b[\w'-]+\b",
            text
        )
    )


# ---------------------------------------------------------
# SENTENCE COUNT
# ---------------------------------------------------------

def sentence_count(text):

    if not text:
        return 0

    sentences = re.findall(
        r"[^.!?]+[.!?]+",
        text
    )

    return len(sentences)


# ---------------------------------------------------------
# HEADING COUNT
# ---------------------------------------------------------

def heading_count(text):

    if not text:
        return 0

    return len(
        re.findall(
            r"(?m)^#{1,6}\s+",
            text
        )
    )


# ---------------------------------------------------------
# CONTENT SCORE
# ---------------------------------------------------------

def content_score(text):

    if not text:
        return 0

    score = 0

    words = word_count(text)
    sentences = sentence_count(text)
    headings = heading_count(text)

    # Basic content presence
    if words >= 100:
        score += 15

    if words >= 300:
        score += 15

    # Structure
    if headings >= 2:
        score += 15

    if headings >= 4:
        score += 10

    # Readability / completeness
    if sentences >= 8:
        score += 15

    if sentences >= 15:
        score += 10

    # Paragraph/content depth
    if len(text.split("\n\n")) >= 4:
        score += 10

    return min(score, 100)
