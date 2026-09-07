import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.tools import web_search, scrape_url

# ---------------- Load .env ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

print("GROQ_API_KEY =", repr(os.getenv("GROQ_API_KEY")))

# ---------------- Model Setup ----------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
)

# ---------------- Search Agent ----------------
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
    )

# ---------------- Reader Agent ----------------
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
    )

# ---------------- Report Templates ----------------
TEMPLATE_INSTRUCTIONS = {
    "academic": """Write in a formal, academic tone. Use precise terminology, cite all sources properly,
and include a detailed methodology-style breakdown. Structure:
- Abstract (2-3 sentences)
- Introduction
- Key Findings (minimum 3 well-explained points, with citations)
- Discussion
- Conclusion
- Sources (list all URLs found in the research)""",

    "business": """Write in a concise, executive tone suitable for business stakeholders. Focus on
actionable insights and impact. Structure:
- Executive Summary (3-4 sentences)
- Key Insights (minimum 3 points, bullet-style, business-relevant)
- Recommendations
- Conclusion
- Sources (list all URLs found in the research)""",

    "casual": """Write in a simple, friendly, easy-to-understand tone. Avoid heavy jargon, explain
technical terms simply. Structure:
- Quick Intro (what is this about, in plain language)
- Key Points (minimum 3, explained simply with examples)
- Wrap-up
- Sources (list all URLs found in the research)""",
}

def get_writer_prompt(template: str = "academic"):
    instructions = TEMPLATE_INSTRUCTIONS.get(template, TEMPLATE_INSTRUCTIONS["academic"])

    return ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert research writer. Write clear, structured and insightful reports.",
        ),
        (
            "human",
            f"""Write a detailed research report on the topic below.

Topic: {{topic}}

Research Gathered:
{{research}}

{instructions}

Be detailed, factual and professional.
""",
        ),
    ])

def get_writer_chain(template: str = "academic"):
    return get_writer_prompt(template) | llm | StrOutputParser()

# ---------------- Critic Chain (unchanged) ----------------
critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. Be honest and specific.",
    ),
    (
        "human",
        """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...
""",
    ),
])

critic_chain = critic_prompt | llm | StrOutputParser()