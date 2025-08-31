from __future__ import annotations
import sqlite3, re
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd

# utils/db.py
SAFE_SQL_PATTERN = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
@dataclass
class DBInfo:
    path: str
    tables: List[str]
    schema_map: Dict[str, str]
    min_order_date: Optional[str]
    max_order_date: Optional[str]

def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def list_tables(conn: sqlite3.Connection) -> List[str]:
    q = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    return [r[0] for r in conn.execute(q).fetchall()]

def get_table_schema(conn: sqlite3.Connection, table: str) -> str:
    q = "SELECT sql FROM sqlite_master WHERE type='table' AND name=?;"
    row = conn.execute(q, (table,)).fetchone()
    return row[0] if row else ""

def build_dbinfo(conn: sqlite3.Connection) -> DBInfo:
    tbls = list_tables(conn)
    schema_map = {t: get_table_schema(conn, t) for t in tbls}
    min_d = max_d = None
    try:
        q = "SELECT MIN(OrderDate) as min_d, MAX(OrderDate) as max_d FROM Orders"
        r = conn.execute(q).fetchone()
        min_d = r["min_d"]
        max_d = r["max_d"]
    except Exception:
        pass
    return DBInfo(path=str(conn), tables=tbls, schema_map=schema_map, min_order_date=min_d, max_order_date=max_d)

def preview(conn: sqlite3.Connection, table: str, limit: int = 5) -> pd.DataFrame:
    df = pd.read_sql_query(f"SELECT * FROM '{table}' LIMIT {int(limit)}", conn)
    return df

def safe_query(conn: sqlite3.Connection, sql: str, default_limit: int = 50) -> Tuple[pd.DataFrame, str]:
    sql = sql.strip().rstrip(";")
    if not SAFE_SQL_PATTERN.match(sql):
        raise ValueError("Only SELECT queries are allowed.")
    # Enforce LIMIT if absent
    if re.search(r"\bLIMIT\b", sql, flags=re.IGNORECASE) is None:
        sql += f" LIMIT {int(default_limit)}"
    df = pd.read_sql_query(sql, conn)
    return df, sql
