# 🧠 Codebase Onboarding Assistant

An intelligent RAG (Retrieval-Augmented Generation) pipeline that parses Python codebases using Abstract Syntax Trees (AST), enriches code logic with Git history, and answers natural language architecture questions using **Gemini 3.6 Flash** and **ChromaDB**.

Built to solve a real problem: new engineers joining a team spend days manually digging through code and commit history just to answer questions like *"where is authentication handled?"* or *"why was this function changed?"* — this tool answers both in seconds, with exact file and line citations.

---

## 💡 Why AST Chunking Over Naive Chunking?

Most naive RAG implementations split source files every *N* characters or lines. This blindly slices functions mid-statement, leading to broken context and LLM hallucinations.

This project uses Python's native `ast` module to slice code strictly by structural boundaries (functions and classes), so every chunk handed to the LLM is a complete, self-contained unit of logic.

**Tested on a real file** (`crud.py` from the [full-stack-fastapi-template](https://github.com/tiangolo/full-stack-fastapi-template) repo):

| Metric | Naive Splitting (300 chars) | AST-Based Chunking |
| :--- | :--- | :--- |
| **Chunks produced** | 9 fragments | 5 complete units |
| **Integrity** | Truncates syntax mid-logic (e.g. `def authenticate(*, sessi` cut off mid-signature) | Preserves 100% complete syntax |
| **Context Quality** | Low — fragments without full function context | High — complete callable units (function/class) |
| **Citations** | Arbitrary, meaningless line ranges | Exact file paths, function names & line numbers |

---

## 🏗️ System Architecture

```text
GitHub Repo URL ──► Git Extractor (Shallow Clone, depth=30)
                         │
                         ▼
                  AST Parser (Functions & Classes)
                         │
                         ▼
             Attach Recent Git Commit History
                         │
                         ▼
        SentenceTransformer Embedding (all-MiniLM-L6-v2)
                         │
                         ▼
             ChromaDB Vector Store (batched insert)
                         │
                         ▼
User Query ──► Vector Similarity Search (Top-K Chunks)
                         │
                         ▼
          Gemini 3.6 Flash + Citation-Enforcing Prompt
                         │
                         ▼
         Synthesized Answer with Exact File & Line Citations
```

---

## ✨ What It Answers

| Question Type | Example |
| :--- | :--- |
| **Location** | "Where is user authentication handled?" |
| **Explanation** | "What does the `create_user` function do?" |
| **History** | "Why was the `authenticate` function recently changed?" |

Each answer is grounded strictly in retrieved code + git metadata — the prompt explicitly instructs the model to say "I don't know" rather than guess if context is insufficient, reducing hallucination risk.

---

## ⚡ Quickstart

**1. Clone & set up environment:**
```bash
git clone https://github.com/YOUR_USERNAME/codebase-onboarding-assistant.git
cd codebase-onboarding-assistant
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure your API key:**

Create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_gemini_api_key_here
```
Get a free key at [Google AI Studio](https://aistudio.google.com/apikey).

**3. Launch the dashboard:**
```bash
streamlit run streamlit_app.py
```

**4. Or run the FastAPI backend directly:**
```bash
uvicorn main:app --reload
```
Then visit `http://127.0.0.1:8000/docs` for the interactive API.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI
- **Code Parsing:** Python's built-in `ast` module + GitPython
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`, runs locally, $0 cost)
- **Vector Store:** ChromaDB (persistent local mode, zero config)
- **LLM:** Gemini 3.6 Flash (free tier via Google AI Studio)
- **Frontend:** Streamlit

---

## 📌 Known Limitations

- Currently supports Python files only (AST parsing is Python-specific)
- Git history depth is capped at the last 30 commits per clone for speed — older history isn't indexed
- Indexing time scales with repo size; very large repos (1000+ files) will take longer on free-tier hosting

---

## 🚀 Github

https://github.com/Abhiyazhini/codebase-onboarding-assistant

## 📹 Demo Video

https://drive.google.com/file/d/1Q-NV61TZGdB9idZfSn3XcUzFVV8aToam/view?usp=sharing

---

Built by Abhiyazhini S — actively looking for **Full-Time AI Software Engineer / AI Product Engineer** roles in Bangalore. Let's connect on [LinkedIn](https://www.linkedin.com/in/abhiyazhini-sivakumar/).
