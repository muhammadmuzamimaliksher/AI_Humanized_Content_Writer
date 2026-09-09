APP_NAME = "AI Humanized Content Writer"

STAGES = [
"Brief Analyzer","Search Intent Planner","Outline Architect","Draft Writer",
"Humanization Editor","SEO Optimizer","Quality Assurance","Final Editor"
]

BASE = "You are a senior professional content specialist. Be precise, useful, natural and reader-focused."

STAGE_CONFIG = {
"Brief Analyzer":{"key":"brief_analysis","system":BASE,"task":"Analyze the brief: audience needs, intent, objective, pain points, questions, angle and factual risks. Do not write the article."},
"Search Intent Planner":{"key":"intent","system":BASE,"task":"Build search-intent and SEO strategy: primary/secondary intent, semantic topics, entities, questions and keyword mapping. Do not fabricate search volume."},
"Outline Architect":{"key":"outline","system":BASE,"task":"Create an article outline with H1, H2/H3 sections, useful examples, FAQs where appropriate and conclusion. Avoid filler."},
"Draft Writer":{"key":"draft","system":"You are an expert original content writer.","task":"Write the complete first draft using the strategy and outline with natural sentence variation and useful examples."},
"Humanization Editor":{"key":"humanized","system":"You are a meticulous human-style editor.","task":"Improve rhythm, sentence variation, transitions, specificity, clarity and personality. Remove filler, repetition and awkward keyword insertion."},
"SEO Optimizer":{"key":"seo","system":"You are a senior on-page SEO editor.","task":"Optimize for user intent, semantic coverage, headings and natural keyword placement without keyword stuffing."},
"Quality Assurance":{"key":"qa","system":"You are a strict editorial QA reviewer.","task":"Audit for unsupported claims, contradictions, repetition, grammar, keyword stuffing, missing intent and readability. Return issues and corrections."},
"Final Editor":{"key":"final","system":"You are the final publication editor.","task":"Create publication-ready content by applying valid QA corrections. Return only final content."}
}
