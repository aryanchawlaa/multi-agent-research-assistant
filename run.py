"""
Quick CLI runner — test the full agent pipeline without needing the API or UI.
Usage:
    python run.py "your research topic here"
    python run.py  # will prompt you for a topic
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from crew.research_crew import run_research_crew
from tools.pdf_exporter import export_to_pdf


def main():
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter research topic: ").strip()
        if not topic:
            print("No topic provided. Exiting.")
            sys.exit(1)

    print(f"\n🚀 Starting research on: '{topic}'\n")

    result = run_research_crew(topic)
    review = result["literature_review"]

    print("\n" + "="*70)
    print("LITERATURE REVIEW")
    print("="*70)
    print(review)
    print("="*70)
    print(f"\nWord count: {result['word_count']}")

    # Save markdown
    os.makedirs("data/outputs", exist_ok=True)
    md_path = f"data/outputs/review_{topic[:30].replace(' ', '_')}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Literature Review: {topic}\n\n")
        f.write(review)
    print(f"✅ Markdown saved: {md_path}")

    # Save PDF
    try:
        pdf_path = export_to_pdf(topic, review)
        print(f"✅ PDF saved:      {pdf_path}")
    except Exception as e:
        print(f"⚠️  PDF export failed: {e}")

    print("\nDone! 🎉")


if __name__ == "__main__":
    main()
