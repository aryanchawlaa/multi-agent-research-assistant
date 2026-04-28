import os
from crewai import Agent
from crewai import LLM


def get_llm():
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.4,
    )


def create_writer_agent() -> Agent:
    return Agent(
        role="Academic Literature Review Writer",
        goal=(
            "Synthesize all research findings into a coherent, well-structured "
            "literature review with proper citations, highlighted contradictions, "
            "and clearly identified research gaps."
        ),
        backstory=(
            "You are a world-class academic writer who has authored literature "
            "reviews published in Nature, Science, and top AI conferences. "
            "You write with precision and clarity. Every single claim you make "
            "is backed by a cited paper. You highlight contradictions between "
            "papers honestly and always end with concrete research gaps and "
            "future directions. You format your output in clean Markdown."
        ),
        llm=get_llm(),
        verbose=True,
        max_iter=5,
        allow_delegation=False,
    )
