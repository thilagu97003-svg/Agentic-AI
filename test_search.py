from app.rag.retriever import HybridRetriever

retriever = HybridRetriever()

for q in [
    "VPN not connecting",
    "I forgot my password",
    "my laptop is very slow",
    "internet is not working",
    "printer shows offline",
]:
    print("\n=== Query:", q)
    for d in retriever.search(q):
        print(" -", d.metadata["source"], "|", d.metadata["section"])