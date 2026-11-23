import re
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from app.config import settings
from app.llm import get_chat_model
from app.rag.ingest import get_vectorstore


def tokenize(text: str):
    return re.findall(r"\w+", text.lower())


class HybridRetriever:
    """Vector search + BM25 keyword search, merged with Reciprocal Rank Fusion."""

    def __init__(self):
        self.vs = get_vectorstore()
        data = self.vs.get()
        self.docs = [
            Document(page_content=c, metadata=m)
            for c, m in zip(data["documents"], data["metadatas"])
        ]
        self.bm25 = BM25Okapi([tokenize(d.page_content) for d in self.docs])

    def search(self, query: str, k: int = 3):
        vector_hits = self.vs.similarity_search(query, k=6)

        scores = self.bm25.get_scores(tokenize(query))
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:6]
        bm25_hits = [self.docs[i] for i in top_idx if scores[i] > 0]

        fused = {}
        for results in (vector_hits, bm25_hits):
            for rank, d in enumerate(results):
                entry = fused.setdefault(d.page_content, [d, 0.0])
                entry[1] += 1 / (60 + rank)

        ranked = sorted(fused.values(), key=lambda x: x[1], reverse=True)
        return [d for d, _ in ranked[:k]]


llm = get_chat_model()


def grade_documents(query: str, docs) -> bool:
    """Agentic RAG step: are the retrieved chunks actually useful?"""
    if not docs:
        return False
    context = "\n\n".join(d.page_content for d in docs)
    prompt = (
        "You are a grader for an IT helpdesk search system.\n"
        f"User issue: {query}\n\n"
        f"Retrieved documents:\n{context}\n\n"
        "Answer 'yes' if the documents are about the same kind of problem as the user issue, "
        "even if they do not cover every detail. Answer 'no' only if they are about "
        "a completely different topic. Answer with one word: yes or no."
    )
    answer = llm.invoke(prompt).content.strip().lower()
    return answer.startswith("yes")


def rewrite_query(query: str) -> str:
    """Agentic RAG step: rewrite a weak query into better search keywords."""
    prompt = (
        "Rewrite this IT support issue as a short search query with technical keywords. "
        "Return only the query, nothing else.\n"
        f"Issue: {query}"
    )
    return llm.invoke(prompt).content.strip()