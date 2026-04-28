import arxiv
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type


class ArxivInput(BaseModel):
    query: str = Field(description="Search query string for arXiv papers")
    max_results: int = Field(default=6, description="Number of papers to retrieve (max 10)")


class ArxivSearchTool(BaseTool):
    name: str = "ArXiv Academic Paper Search"
    description: str = (
        "Search arXiv.org for academic research papers on any topic. "
        "Returns paper titles, authors, abstracts, publication dates, and URLs. "
        "Use this to find primary research sources."
    )
    args_schema: Type[BaseModel] = ArxivInput

    def _run(self, query: str, max_results: int = 6) -> str:
        try:
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=min(max_results, 10),
                sort_by=arxiv.SortCriterion.Relevance,
            )

            papers = []
            for paper in client.results(search):
                papers.append({
                    "title": paper.title,
                    "authors": [a.name for a in paper.authors[:4]],
                    "abstract": paper.summary[:600],
                    "url": paper.entry_id,
                    "published": str(paper.published.date()),
                    "categories": paper.categories[:3],
                })

            if not papers:
                return f"No papers found for query: '{query}'"

            output = f"Found {len(papers)} papers for '{query}':\n\n"
            for i, p in enumerate(papers, 1):
                output += f"[{i}] TITLE: {p['title']}\n"
                output += f"    AUTHORS: {', '.join(p['authors'])}\n"
                output += f"    PUBLISHED: {p['published']}\n"
                output += f"    CATEGORIES: {', '.join(p['categories'])}\n"
                output += f"    URL: {p['url']}\n"
                output += f"    ABSTRACT: {p['abstract']}\n\n"

            return output

        except Exception as e:
            return f"ArXiv search failed: {str(e)}. Try a different query."
