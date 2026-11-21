from app.rag.retriever import HybridRetriever, grade_documents, rewrite_query

retriever = HybridRetriever()

for q in [
    "VPN not connecting",
    "I forgot my password",
    "my laptop is very slow",
    "internet is not working",
]:
    docs = retriever.search(q)
    print("\n=== Query:", q)
    for d in docs:
        print(" -", d.metadata["source"], "|", d.metadata["section"])

    ok = grade_documents(q, docs)
    print("Relevant?", ok)
    if not ok:
        new_q = rewrite_query(q)
        print("Rewritten query:", new_q)