import os
from crewai import Agent
from crewai import LLM
from tools.arxiv_tool import ArxivSearchTool
from tools.serpapi_tool import SerpApiSearchTool


def get_llm():
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
    )


def create_searcher_agent() -> Agent:
    tools = [ArxivSearchTool()]

    # Add SerpAPI web search only if key is provided
    serpapi_key = os.getenv("SERPAPI_KEY", "").strip()
    if serpapi_key:
        tools.append(SerpApiSearchTool())

    return Agent(
        role="Research Paper Searcher",
        goal=(
            "Find the most relevant, recent, and highly-cited research papers "
            "on the given topic from arXiv and the web."
        ),
        backstory=(
            "You are an expert academic researcher with 15 years of experience "
            "mining academic databases. You know exactly how to craft search "
            "queries to surface the most impactful papers. You always retrieve "
            "full abstracts, author lists, publication dates, and core claims. "
            "You never hallucinate papers — you only report what you actually find."
        ),
        tools=tools,
        llm=get_llm(),
        verbose=True,
        max_iter=5,
        allow_delegation=False,
    )
