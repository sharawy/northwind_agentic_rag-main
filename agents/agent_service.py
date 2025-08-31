from __future__ import annotations
import os
import time
from dataclasses import dataclass
from dotenv import load_dotenv
from agents.sql_analyst import SQLAnalyst
from agents.nl2sql_agent import NL2SQLAgent
from utils import db as dbutils

load_dotenv()

@dataclass
class AgentService:
    db_path: str
    vector_backend: str = os.getenv("VECTOR_STORE", "chroma")
    vector_dir: str = "./.vs"
    retrieval_k: int = int(os.getenv("RETRIEVAL_TOP_K", "4"))
    result_limit: int = int(os.getenv("RESULT_ROW_LIMIT", "50"))

    def __post_init__(self):
        self.analyst = SQLAnalyst(self.db_path, default_limit=self.result_limit)
        self.nl2sql = NL2SQLAgent(
            vector_backend=self.vector_backend,
            vector_dir=self.vector_dir,
            retrieval_k=self.retrieval_k,
            analyst=self.analyst,
            default_limit=self.result_limit
        )

    def ask(self, question: str) -> dict:
        return self.nl2sql.answer(question)

    # Updated demo_required_analytics method
    def demo_required_analytics(self) -> dict:
        # Execute analytics queries as questions
        from rich.console import Console

        console = Console()

        # Execute analytics queries as questions
        questions = {
            "top_5_countries_by_sales": "Show top 5 countries by total sales",
            "best_selling_products_by_qty": "Show best-selling products by quantity",
            "revenue_by_category_by_quarter": "Revenue breakdown by category and quarter",
            "avg_order_value_per_customer": "Average order value per customer",
            "sales_trend_by_month": "Compare sales trends over months/years",
            "most_orders_in_2024": "Which customers ordered the most in 2024?",
            "top_categories_in_france": "What are the top 3 selling product categories in France?",
            "suppliers_in_uk": "How many suppliers are based in the UK?",
            "total_revenue_q2_2023": "What is the total revenue in Q2 2023?"
        }

        results = {}
        for key, question in questions.items():
            result = self.ask(question)
            console.rule(f"[bold cyan]{key.replace('_', ' ').title()}[/bold cyan]")
            console.print(f"[bold]Question:[/bold] {questions[key]}")
            console.print(f"[bold]Generated SQL:[/bold]\n{result['sql']}")
            console.print(f"[bold]Results:[/bold]\n{result['table']}")
            time.sleep(1)
        return results
