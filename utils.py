import re

def validate_brief(topic, keywords):
    errors=[]
    if not topic or len(topic.strip()) < 10:
        errors.append("Topic/brief must contain at least 10 characters.")
    if len(topic or "") > 10000:
        errors.append("Topic/brief is too long.")
    if len(keywords or "") > 3000:
        errors.append("Keyword list is too long.")
    return errors

def word_count(text):
    return len(re.findall(r"\b[\w'-]+\b", text or ""))

def content_score(text):
    if not text: return 0
    score=50
    if word_count(text)>=300: score+=15
    if len(re.findall(r"\n#{1,6}\s",text))>=2: score+=10
    if len(re.split(r"[.!?]",text))>=8: score+=10
    if len(text.split())>50: score+=10
    return min(score,100)
