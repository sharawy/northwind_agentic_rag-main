from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import pandas as pd
from tabulate import tabulate
from utils import db as dbutils

@dataclass
class SQLAnalyst:
    db_path: str
    default_limit: int = 50

    def __post_init__(self):
        self.conn = dbutils.connect(self.db_path)

    def run(self, sql: str) -> dict:
        df, final_sql = dbutils.safe_query(self.conn, sql, default_limit=self.default_limit)
        # Friendly formats
        table = tabulate(df, headers='keys', tablefmt='github', showindex=False)
        return {
            "final_sql": final_sql,
            "rows": len(df),
            "table": table,
            "data": df.to_dict(orient='records')
        }

    def schema_summary(self) -> str:
        info = dbutils.build_dbinfo(self.conn)
        parts = []
        for t in info.tables:
            schema = info.schema_map.get(t, "").replace("\n", " ")
            parts.append(f"- {t}: {schema}")
        date_hint = ""
        if info.min_order_date and info.max_order_date:
            date_hint = f"\nOrders date range: {info.min_order_date} .. {info.max_order_date}"
        return "\n".join(parts) + date_hint
