# Multi-Agent Research Assistant
### 100% FREE — No paid API keys required

3 specialized AI agents that autonomously search arXiv, cross-verify claims, detect contradictions, and produce literature reviews.

**Free Stack:** Groq (free LLM) · arXiv (free papers) · Qdrant (free local vector DB) · FastAPI · Streamlit

---

## Get Your Free API Keys

### 1. Groq API Key (REQUIRED — replaces OpenAI, completely free)
1. Go to **https://console.groq.com**
2. Sign up with Google or email — no credit card needed
3. Click **API Keys** → **Create API Key**
4. Copy the key → paste into `.env` as `GROQ_API_KEY=...`
- Free tier: 30 requests/minute, 6000 tokens/min — more than enough

### 2. SerpAPI Key (OPTIONAL — for web search)
1. Go to **https://serpapi.com**
2. Sign up — no credit card needed
3. You get **100 free searches/month**
4. Copy key → paste into `.env` as `SERPAPI_KEY=...`
- **If you skip this, arXiv search alone works perfectly fine**

### 3. Everything else is free
- **arXiv** — no key, no signup, completely open
- **Qdrant** — runs locally on your machine via Docker
- **sentence-transformers** — runs locally, no API

---

## Setup (Step by Step)

### Step 1 — Open the folder in VS Code
Unzip the download. You get a folder called `multi-agent-research`.
Open VS Code → File → Open Folder → select `multi-agent-research`

### Step 2 — Create virtual environment
Open the VS Code terminal (Ctrl + `) and run:
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```
This takes 3–5 minutes the first time.

### Step 4 — Add your free Groq key to .env
Open the `.env` file in VS Code and replace:
```
GROQ_API_KEY=your_groq_api_key_here
```
with your actual key from console.groq.com

### Step 5 — Start Qdrant (needs Docker Desktop)
If you don't have Docker: download from **https://docker.com/products/docker-desktop**

Then run in terminal:
```bash
docker run -p 6333:6333 qdrant/qdrant
```
Leave this terminal open.

### Step 6 — Run the project

**Easiest way (CLI, no UI):**
```bash
python run.py "transformer attention mechanisms"
```

**Full UI:**
```bash
# Terminal 1 (keep Qdrant running from Step 5)

# Terminal 2:
uvicorn api.main:app --reload --port 8000

# Terminal 3:
streamlit run frontend/app.py
```
Open browser → **http://localhost:8501**

---

## Project Structure
```
multi-agent-research/
├── .env                     ← Your free API keys go here
├── requirements.txt
├── run.py                   ← Quick test runner (no UI needed)
├── agents/
│   ├── searcher.py          ← Agent 1: Searches arXiv
│   ├── critic.py            ← Agent 2: Finds contradictions
│   └── writer.py            ← Agent 3: Writes review
├── tools/
│   ├── arxiv_tool.py        ← Free arXiv search (no key needed)
│   ├── serpapi_tool.py      ← Optional web search
│   ├── vector_store.py      ← Qdrant local memory
│   └── pdf_exporter.py      ← PDF generation
├── crew/
│   └── research_crew.py     ← Orchestrates all 3 agents
├── api/
│   └── main.py              ← FastAPI backend
└── frontend/
    └── app.py               ← Streamlit UI
```

---

## Troubleshooting

**"GROQ_API_KEY not found"**
→ Open `.env` and make sure you pasted your key correctly. No spaces around `=`.

**"Cannot connect to API server"**
→ Run `uvicorn api.main:app --reload --port 8000` in a separate terminal first.

**"Qdrant connection refused"**
→ Run `docker run -p 6333:6333 qdrant/qdrant` in a terminal and leave it open.

**"Module not found"**
→ Make sure your venv is activated: `venv\Scripts\activate` (Windows)

**Agents are slow**
→ Normal. 3 agents doing real research takes 3–8 minutes. You can see live logs in the terminal running the API.

---

## Resume Line
> "Built a multi-agent academic research pipeline using CrewAI and Groq LLaMA-3 where specialized agents autonomously search arXiv, detect contradictions between papers, and generate structured literature reviews — reducing manual research time from 4 hours to under 6 minutes."



<video src="https://github.com/user-attachments/assets/" controls width="700"></video>
