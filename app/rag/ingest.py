from pathlib import Path
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from app.config import settings

KB_DIR = Path("data/kb")


def get_vectorstore():
    embeddings = OllamaEmbeddings(
        model=settings.EMBED_MODEL, base_url=settings.OLLAMA_BASE_URL
    )
    return Chroma(
        collection_name="it_kb",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_DIR,
    )


def load_chunks():
    """One chunk per '##' section. Title is added to every chunk for context."""
    docs, ids = [], []
    for f in sorted(KB_DIR.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        title = lines[0].lstrip("# ").strip()

        category, priority = "other", "low"
        for line in lines[:4]:
            if line.startswith("Category:"):
                parts = line.split("|")
                category = parts[0].replace("Category:", "").strip()
                if len(parts) > 1:
                    priority = parts[1].replace("Default priority:", "").strip()

        sections = text.split("\n## ")
        for i, sec in enumerate(sections[1:], start=1):
            heading, _, body = sec.partition("\n")
            content = f"{title} - {heading.strip()}\n{body.strip()}"
            docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": f.name,
                        "title": title,
                        "section": heading.strip(),
                        "category": category,
                        "priority": priority,
                    },
                )
            )
            ids.append(f"{f.stem}-{i}")
    return docs, ids


def ingest():
    docs, ids = load_chunks()
    vs = get_vectorstore()
    vs.reset_collection()  # fresh start, no duplicates on re-run
    vs.add_documents(docs, ids=ids)
    print(f"Ingested {len(docs)} chunks from {len(set(d.metadata['source'] for d in docs))} files")


if __name__ == "__main__":
    ingest()