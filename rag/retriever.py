from __future__ import annotations
import os
from dotenv import load_dotenv
from typing import Any

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS, Chroma

load_dotenv()

def load_retriever(persist_dir: str = "./.vs", backend: str = "chroma", k: int = 4):
    if backend == "faiss":
        store = FAISS.load_local(persist_dir, GoogleGenerativeAIEmbeddings(model="text-embedding-004"), allow_dangerous_deserialization=True)
    else:
        store = Chroma(persist_directory=persist_dir, embedding_function=GoogleGenerativeAIEmbeddings(model="text-embedding-004"))
    return store.as_retriever(search_kwargs={'k': k})
