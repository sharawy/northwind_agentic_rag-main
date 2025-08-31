from __future__ import annotations
import os, sys
import typer
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv
from agents.agent_service import AgentService
from rag.ingest import load_docs, build_vectorstore

app = typer.Typer(help="Northwind Agentic RAG: ask business questions in English, get SQL + results.")
console = Console()

def ensure_env():
    load_dotenv()
    if not os.getenv("DATABASE_PATH"):
        console.print("[red]DATABASE_PATH missing in .env[/red]")
        raise typer.Exit(code=1)

@app.command()
def ingest(
    docs_glob: str = typer.Option("rag/schema_docs/*", help="Glob for docs to embed"),
    persist_dir: str = typer.Option(".vs", help="Vector store directory"),
    backend: str = typer.Option(os.getenv("VECTOR_STORE", "chroma"), help="faiss|chroma"),
):
    """Embed schema/business docs to a vector store."""
    load_dotenv()
    docs = load_docs(docs_glob)
    kind, path = build_vectorstore(docs, persist_dir, backend=backend)
    console.print(f"Built vectorstore: [bold]{kind}[/bold] at [bold]{path}[/bold] with {len(docs)} docs.")

@app.command()
def chat():
    """Interactive chat: ask business questions in English, get SQL + results."""
    ensure_env()
    orch = AgentService(
        db_path=os.getenv("DATABASE_PATH"),
        vector_backend=os.getenv("VECTOR_STORE", "chroma"),
        vector_dir=".vs",
        retrieval_k=int(os.getenv("RETRIEVAL_TOP_K", "4")),
        result_limit=int(os.getenv("RESULT_ROW_LIMIT", "50")),
    )
    memory = []
    console.print("[bold cyan]Type your question (or 'exit' to quit):[/bold cyan]")
    while True:
        question = console.input("[green]> [/green]").strip()
        res = orch.ask(question)
        console.print(Panel.fit("[bold]Generated SQL[/bold]\n\n```sql\n" + res["sql"] + "\n```", title="SQL", border_style="cyan"))
        console.print(Panel.fit(res["table"], title=f"Results (rows={res['rows']})", border_style="green"))
        if question.lower() in {"exit", "quit"}:
            break
@app.command()
def analytics():
    """Show required analytics."""
    ensure_env()
    agent_service = AgentService(db_path=os.getenv("DATABASE_PATH"))
    agent_service.demo_required_analytics()


if __name__ == "__main__":
    app()
