# Northwind Agentic RAG — NL→SQL Multi‑Agent (LangChain)

Two‑agent system for translating natural‑language business questions into **SQLite SQL** and returning results, grounded with **Agentic RAG** (FAISS/Chroma).

## Features
- **Agent 2 (NL→SQL Generator)**: Uses LangChain + OpenAI/Gemini and a vector store (FAISS/Chroma) containing schema and business notes to reduce hallucinations.
- **Agent 1 (SQL Analyst)**: Executes SQL against your Northwind SQLite DB and returns pretty tables.
- **Schema‑aware prompts** with validation pass to catch common SQL mistakes.
- **Conversation‑ready** design; easy to add memory (ConversationBufferMemory) if you deploy to a server/bot.
- **Canonical analytics SQL** templates included.

> ⚠️ Your dataset dates are in **2016** (per the sample you shared). If a user asks for 2023/2024, the system auto‑adjusts to the nearest valid year and annotates the SQL with a comment.

## Quickstart

1) **Create & fill `.env`** (use the provided example):

```bash
cp .env.example .env
# Edit: OPENAI_API_KEY or GOOGLE_API_KEY, and DATABASE_PATH=./data/1751978414.sqlite3
```

2) **Install**:

```bash
pip install -r requirements.txt
```

3) **Embed schema/docs** into a vector store (Chroma by default):

```bash
python app.py ingest
# Or FAISS:
# VECTOR_STORE=faiss python app.py ingest --backend faiss
```

4) **Ask a question**:

```bash
python app.py chat "Which customers ordered the most in 2016?"
```

5) **Show canonical analytics SQL**:

```bash
python app.py analytics
```

## Project Layout
```
northwind_agentic_rag/
  app.py
  requirements.txt
  .env.example
  rag/
    ingest.py
    retriever.py
    schema_docs/
      schema.md
      business_notes.md
  agents/
    sql_analyst.py
    nl2sql_agent.py
    orchestrator.py
  prompts/
    nl2sql_prompt.txt
    sql_validator_prompt.txt
  utils/
    db.py
    logging_conf.py
    eval.py
  tests/
    test_queries.yaml
  data/
    1751978414.sqlite3   # <- place your DB file here
```

## How it Works

1) **RAG build**: We embed `rag/schema_docs/*` (schema + business notes) into FAISS/Chroma via `OpenAIEmbeddings`.  
2) **NL→SQL**: The user question + top‑k retrieved snippets + live DB schema summary are passed to Agent 2’s prompt. The LLM returns a single `SELECT` query in a code block.  
3) **Validation**: A reviewer prompt enforces SQLite syntax, quoting (`"Order Details"`), and LIMIT behavior.  
4) **Execution**: Agent 1 executes the query (read‑only) on SQLite and renders a markdown table.  

You can add **memory** (e.g., `ConversationBufferMemory`) by wrapping `Orchestrator.ask()` inside a chat loop and storing prior messages for the prompt. The code is structured so that step is straightforward.

## Required Analytics — Canonical SQL

Open with `python app.py analytics`; included queries cover:
- Top 5 countries by total sales (revenue)
- Best‑selling products by quantity
- Revenue breakdown by category and quarter
- Average order value per customer
- Sales trends by month/year

## Sample Queries
- “Which customers ordered the most in 2016?”
- “What are the top 3 selling product categories in France by **revenue**?”
- “How many suppliers are based in the UK?”
- “What is the total revenue in Q2 2016?”
- “Show top 5 countries by total sales revenue.”
- “Best‑selling products by quantity.”
- “Revenue by category and quarter.”
- “Average order value per customer.”
- “Compare sales trends by month over the data period.”
- “Top 10 customers by revenue in Germany.”

## Notes on Accuracy & Speed
- **No DDL/DML** is allowed; only `SELECT` statements execute.
- Unknown years (e.g., 2024) are adjusted to the dataset’s actual year range (e.g., 2016) with an inline SQL comment.
- Retrieval `k` and default `LIMIT` are configurable via `.env`. Keep `k≤4` and `LIMIT≤50` to meet the 3–5s target.

## Tests
Edit `tests/test_queries.yaml` and run:
```bash
python -m utils.eval
```

## Why Agentic RAG?
- The vector store **grounds** the model on table names and relationships, which is the primary cause of NL→SQL hallucinations.
- The validation pass catches common quoting and LIMIT issues.
- The modular design separates concerns, making it easy to swap LLMs or vector backends.
