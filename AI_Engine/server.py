from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama
import json
import os
import re
from datetime import datetime

app = FastAPI()

# ALLOW FRONTEND CONNECTION

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# INPUT MODEL

class ArticleInput(BaseModel):
    article: str

# EXTRACT SECTIONS

def extract_section(text, start, end=None):

    if end:

        pattern = rf"\*\*{start}:?\*\*\s*(.*?)\s*(?=\*\*{end}:?\*\*|$)"

    else:

        pattern = rf"\*\*{start}:?\*\*\s*(.*)"

    match = re.search(
        pattern,
        text,
        re.DOTALL | re.IGNORECASE
    )

    if match:
        return match.group(1).strip()

    return ""

# GET ALL ARTICLES

@app.get("/articles")
def get_articles():

    file_path = "data/articles.json"

    if os.path.exists(file_path):

        with open(file_path, "r", encoding="utf-8") as file:
            articles = json.load(file)

    else:

        articles = []

    return {
        "articles": articles
    }

# GENERATE ARTICLE

@app.post("/generate")
def generate_article(data: ArticleInput):

    prompt = f"""

You are an elite CAT VARC reading content creator.

Your task is to transform the RAW ARTICLE into a highly realistic CAT-style reading passage for Articles Daily+.

IMPORTANT OBJECTIVE:

This is NOT a mock test platform.

The goal is to:
- build reading habit
- improve comprehension
- train paragraph flow understanding
- improve tone recognition
- develop CAT-level reading stamina

WRITING STYLE RULES:

1. Preserve the core ideas of the raw article.
2. Use authentic CAT RC writing style.
3. Make the writing analytical and intellectually dense.
4. Avoid robotic AI phrasing.
5. Use nuanced transitions.
6. Passage length: 500–700 words.
7. Writing should feel editorial and sophisticated.
8. Prioritize readability and conceptual depth.
9. Avoid generic motivational language.
10. Maintain CAT-level abstraction and inference density.

OUTPUT FORMAT STRICTLY:

**TITLE:**
<generated title>

**CATEGORY:**
<ONE category only>

**DIFFICULTY:**
<Easy/Moderate/Difficult>

**READ TIME:**
<example: 6 mins>

**PASSAGE:**
<full passage>

**SUMMARY:**
<2-3 line concise summary>

**CENTRAL IDEA:**
<main conceptual argument>

**AUTHOR TONE:**
<comma separated tone words>

**PARAGRAPH INSIGHTS:**

Paragraph 1:
<main function of paragraph>

Paragraph 2:
<main function of paragraph>

Paragraph 3:
<main function of paragraph>

Paragraph 4:
<main function of paragraph>

Paragraph 5:
<main function of paragraph>

Keep paragraph insights:
- concise
- analytical
- CAT-oriented
- focused on argument flow

RAW ARTICLE:
{data.article}

END OF ARTICLE.
"""

    response = ollama.chat(
        model="gemma3:1b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    result = response["message"]["content"]

    # EXTRACT CONTENT

    title = extract_section(
        result,
        "TITLE",
        "CATEGORY"
    )

    category = extract_section(
        result,
        "CATEGORY",
        "DIFFICULTY"
    )

    difficulty = extract_section(
        result,
        "DIFFICULTY",
        "READ TIME"
    )

    read_time = extract_section(
        result,
        "READ TIME",
        "PASSAGE"
    ).split("\n")[0]

    passage_match = re.search(
        r"\*\*PASSAGE:\*\*(.*?)\*\*SUMMARY:",
        result,
        re.DOTALL | re.IGNORECASE
    )

    passage = (
        passage_match.group(1).strip()
        if passage_match
        else ""
    )

    summary = extract_section(
        result,
        "SUMMARY",
        "CENTRAL IDEA"
    )

    central_idea = extract_section(
        result,
        "CENTRAL IDEA",
        "AUTHOR TONE"
    )

    author_tone = extract_section(
        result,
        "AUTHOR TONE",
        "PARAGRAPH INSIGHTS"
    )

    paragraph_insights = extract_section(
        result,
        "PARAGRAPH INSIGHTS",
        None
    )

    # ARTICLE OBJECT

    article_data = {
        "id": datetime.now().timestamp(),
        "created_at": str(datetime.now()),
        "raw_article": data.article,
        "title": title,
        "category": category,
        "difficulty": difficulty,
        "read_time": read_time,
        "passage": passage,
        "summary": summary,
        "central_idea": central_idea,
        "author_tone": author_tone,
        "paragraph_insights": paragraph_insights,
        "generated_output": result
    }

    # FILE PATH

    file_path = "data/articles.json"

    # LOAD EXISTING ARTICLES

    if os.path.exists(file_path):

        with open(file_path, "r", encoding="utf-8") as file:
            articles = json.load(file)

    else:

        articles = []

    # INSERT NEW ARTICLE

    articles.insert(0, article_data)

    # SAVE FILE

    with open(file_path, "w", encoding="utf-8") as file:

        json.dump(
            articles,
            file,
            indent=4,
            ensure_ascii=False
        )

    return {
        "output": result
    }