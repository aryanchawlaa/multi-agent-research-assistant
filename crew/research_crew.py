import os
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Task, Process

from agents.searcher import create_searcher_agent
from agents.critic import create_critic_agent
from agents.writer import create_writer_agent

load_dotenv()


def build_tasks(topic: str, searcher, critic, writer):
    search_task = Task(
        description=(
            f"Search for the 6 most relevant and recent academic papers on: '{topic}'.\n\n"
            "For EACH paper you find, extract and return:\n"
            "1. Full paper title\n"
            "2. Author names (up to 4)\n"
            "3. Publication year\n"
            "4. Core claims and contributions (3-5 bullet points)\n"
            "5. Methodology used\n"
            "6. Key results and metrics reported\n"
            "7. Stated limitations\n"
            "8. ArXiv URL\n\n"
            "Use the ArXiv search tool first, then supplement with web search. "
            "Only include real papers you have actually found. Do not fabricate."
        ),
        agent=searcher,
        expected_output=(
            "A structured list of 5-6 real papers with title, authors, year, "
            "core claims, methodology, results, limitations, and URL for each."
        ),
    )

    critic_task = Task(
        description=(
            f"You have been given a list of research papers on '{topic}'. "
            "Perform a rigorous critical analysis:\n\n"
            "1. CONTRADICTIONS: Identify any claims where two papers directly contradict "
            "each other. Cite both paper titles and quote the conflicting claims.\n"
            "2. WEAK EVIDENCE: Flag any papers that make strong claims without sufficient "
            "experimental evidence or with very small sample sizes.\n"
            "3. CREDIBILITY SCORES: Assign each paper a credibility score from 1-10 based on "
            "methodology quality, reproducibility, dataset size, and novelty.\n"
            "4. CONSENSUS: Identify the 2-3 findings that multiple papers agree on.\n"
            "5. METHODOLOGY COMPARISON: Compare the experimental approaches across papers.\n\n"
            "Be specific. Always cite paper titles. This analysis will be used directly in the review."
        ),
        agent=critic,
        expected_output=(
            "A detailed critical analysis with: contradictions (with paper citations), "
            "credibility scores for each paper, consensus findings, weak evidence flags, "
            "and methodology comparison."
        ),
        context=[search_task],
    )

    write_task = Task(
        description=(
            f"Write a complete academic literature review on '{topic}' using the "
            "Searcher's paper list and the Critic's analysis.\n\n"
            "REQUIRED SECTIONS (use these exact Markdown headers):\n\n"
            "## 1. Introduction\n"
            "Brief overview of the topic and why it matters. Scope of this review.\n\n"
            "## 2. Key Themes and Findings\n"
            "Synthesize the main contributions across papers. Group by theme. "
            "Cite every claim with the paper title in brackets e.g. [Smith et al., 2023].\n\n"
            "## 3. Contradictions and Debates\n"
            "Use the Critic's contradiction analysis. Present both sides fairly.\n\n"
            "## 4. Methodology Comparison\n"
            "Compare approaches, datasets used, and evaluation metrics across papers.\n\n"
            "## 5. Credibility Assessment\n"
            "Include the credibility scores from the Critic with brief justifications.\n\n"
            "## 6. Research Gaps and Future Directions\n"
            "Based on the gaps you see, list 4-6 concrete future research directions.\n\n"
            "## 7. References\n"
            "List all papers in APA format with their ArXiv URLs.\n\n"
            "Write in formal academic tone. Use Markdown formatting throughout."
        ),
        agent=writer,
        expected_output=(
            "A complete, well-structured literature review in Markdown format with all 7 sections, "
            "proper citations, contradiction highlights, credibility scores, and a references list."
        ),
        context=[search_task, critic_task],
    )

    return search_task, critic_task, write_task


def run_research_crew(topic: str) -> dict:
    """Run the full 3-agent research pipeline and return structured results."""

    print(f"\n{'='*60}")
    print(f"  Starting Research Crew for: {topic}")
    print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}\n")

    searcher = create_searcher_agent()
    critic = create_critic_agent()
    writer = create_writer_agent()

    search_task, critic_task, write_task = build_tasks(topic, searcher, critic, writer)

    crew = Crew(
        agents=[searcher, critic, writer],
        tasks=[search_task, critic_task, write_task],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    review_text = str(result)

    return {
        "topic": topic,
        "literature_review": review_text,
        "agents_used": ["Searcher", "Critic", "Writer"],
        "timestamp": datetime.now().isoformat(),
        "word_count": len(review_text.split()),
    }
