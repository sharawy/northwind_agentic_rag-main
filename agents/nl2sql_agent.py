from __future__ import annotations
import os, re, textwrap
from dataclasses import dataclass
from typing import Tuple
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from rag.retriever import load_retriever
from agents.sql_analyst import SQLAnalyst

load_dotenv()

def make_llm(model: str = None):
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "gemini":
        mdl = model or "gemini-2.5-flash"
        return ChatGoogleGenerativeAI(model=mdl, temperature=0.2)
    else:
        mdl = model or "gpt-4o-mini"
        return ChatOpenAI(model=mdl, temperature=0.2)

SQL_BLOCK_RE = re.compile(r"```sql\s*(.*?)\s*```", re.IGNORECASE | re.DOTALL)

@dataclass
class NL2SQLAgent:
    vector_backend: str
    vector_dir: str
    retrieval_k: int
    analyst: SQLAnalyst
    default_limit: int = 50

    def __post_init__(self):
        self.retriever = load_retriever(self.vector_dir, self.vector_backend, self.retrieval_k)
        self.llm = make_llm()
        self.validator_llm = make_llm()

        prompt_text = open("prompts/nl2sql_prompt.txt", "r", encoding="utf-8").read()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_text),
            ("human", "Question: {question}\n\nRetrieved context:\n{context}\n\nSchema Summary:\n{schema}\n\nProduce SQL now."),
        ])
        val_prompt_text = open("prompts/sql_validator_prompt.txt", "r", encoding="utf-8").read()
        self.validator_prompt = ChatPromptTemplate.from_messages([
            ("system", val_prompt_text),
            ("human", "SQL to validate:\n```sql\n{sql}\n```\n\nSchema Summary:\n{schema}"),
        ])
        self.parser = StrOutputParser()

    def _extract_sql(self, text: str) -> str:
        m = SQL_BLOCK_RE.search(text)
        return m.group(1).strip() if m else text.strip()

    def generate_sql(self, question: str) -> Tuple[str, str]:
        # Retrieve relevant docs
        docs = self.retriever.get_relevant_documents(question)
        context = "\n---\n".join([d.page_content[:1200] for d in docs])
        schema = self.analyst.schema_summary()

        chain = self.prompt | self.llm | self.parser
        raw = chain.invoke({"question": question, "context": context, "schema": schema})
        sql = self._extract_sql(raw)

        # Validate / correct SQL
        v_chain = self.validator_prompt | self.validator_llm | self.parser
        v_raw = v_chain.invoke({"sql": sql, "schema": schema})
        v_sql = self._extract_sql(v_raw)
        return v_sql, context

    def answer(self, question: str) -> dict:
        sql, context = self.generate_sql(question)
        result = self.analyst.run(sql)
        result.update({
            "sql": sql,
            "context": context
        })
        return result
