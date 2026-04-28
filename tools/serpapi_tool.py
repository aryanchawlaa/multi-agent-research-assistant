import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type


class SerpApiInput(BaseModel):
    query: str = Field(description="Web search query string")


class SerpApiSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = (
        "Search the web for academic papers, blogs, and recent research. "
        "Use this to supplement arXiv results with newer findings or news."
    )
    args_schema: Type[BaseModel] = SerpApiInput

    def _run(self, query: str) -> str:
        serpapi_key = os.getenv("SERPAPI_KEY", "").strip()
        if not serpapi_key:
            return "Web search skipped — no SERPAPI_KEY set. Using arXiv results only."

        try:
            from serpapi import GoogleSearch
            search = GoogleSearch({
                "q": query + " research paper",
                "api_key": serpapi_key,
                "num": 5,
            })
            results = search.get_dict().get("organic_results", [])
            if not results:
                return "No web results found."

            output = f"Web results for '{query}':\n\n"
            for i, r in enumerate(results[:5], 1):
                output += f"[{i}] {r.get('title', 'No title')}\n"
                output += f"    URL: {r.get('link', '')}\n"
                output += f"    Snippet: {r.get('snippet', '')}\n\n"
            return output

        except Exception as e:
            return f"Web search failed: {str(e)}"
