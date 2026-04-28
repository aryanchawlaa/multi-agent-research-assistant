import os
from crewai import Agent
from crewai import LLM


def get_llm():
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )


def create_critic_agent() -> Agent:
    return Agent(
        role="Research Critic and Fact Verifier",
        goal=(
            "Critically analyze research papers, cross-verify claims across "
            "multiple sources, detect contradictions, and assign credibility scores."
        ),
        backstory=(
            "You are a senior research scientist and peer reviewer for NeurIPS, "
            "ICML, and ACL with 20 years of experience. You have an exceptionally "
            "sharp eye for spotting when two papers contradict each other, when "
            "claims are overstated, when sample sizes are too small, or when "
            "results may not generalize. You always cite specific paper titles "
            "when flagging issues and assign a credibility score from 1 to 10 "
            "based on methodology, reproducibility, and citation count."
        ),
        llm=get_llm(),
        verbose=True,
        max_iter=5,
        allow_delegation=False,
    )
