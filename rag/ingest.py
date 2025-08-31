from __future__ import annotations
import os, glob
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS, Chroma

load_dotenv()

def load_docs(path_glob: str) -> List[Document]:
    docs = []
    for p in glob.glob(path_glob):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.read()
        docs.append(Document(page_content=txt, metadata={'source': os.path.basename(p)}))
    return docs

def build_vectorstore(docs: List[Document], persist_dir: str = "./.vs", backend: str = "chroma"):

    embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004") # relies on OPENAI_API_KEY
    os.makedirs(persist_dir, exist_ok=True)

    if backend == "faiss":
        store = FAISS.from_documents(docs, embeddings)
        store.save_local(persist_dir)
        return ("faiss", persist_dir)
    else:
        store = Chroma.from_documents(docs, embeddings, persist_directory=persist_dir)
        return ("chroma", persist_dir)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--docs_glob', default='rag/schema_docs/*')
    ap.add_argument('--persist_dir', default='./.vs')
    ap.add_argument('--backend', default=os.getenv('VECTOR_STORE', 'chroma'))
    args = ap.parse_args()

    docs = load_docs(args.docs_glob)
    kind, path = build_vectorstore(docs, args.persist_dir, backend=args.backend)
    print(f"Built vectorstore: {kind} at {path} with {len(docs)} docs")
