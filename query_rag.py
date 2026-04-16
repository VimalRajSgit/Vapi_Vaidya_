import os
from dotenv import load_dotenv

from groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

load_dotenv()

# ── Config ─────────────────────────────
QDRANT_URL     = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")

COLLECTION_NAME = "medical_records"
EMBED_MODEL     = "all-MiniLM-L6-v2"
GROQ_MODEL      = "llama-3.3-70b-versatile"

# ── Clients ────────────────────────────
qdrant   = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
groq     = Groq(api_key=GROQ_API_KEY)
embedder = SentenceTransformer(EMBED_MODEL)

# ═══════════════════════════════════════
# SEARCH
# ═══════════════════════════════════════
def search_records(query, patient_id=None):
    vector = embedder.encode(query).tolist()

    filt = None
    if patient_id:
        filt = Filter(
            must=[FieldCondition(key="patient_id", match=MatchValue(value=patient_id))]
        )

    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        query_filter=filt,
        limit=5,
        with_payload=True,
    ).points

    return results

# ═══════════════════════════════════════
# ASK
# ═══════════════════════════════════════
def ask(question, patient_id=None):
    hits = search_records(question, patient_id)

    if not hits:
        return "No records found."

    context = "\n\n".join(str(h.payload) for h in hits)

    response = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{
            "role": "user",
            "content": f"""
You are a helpful medical assistant.

Answer clearly using ONLY the provided records.

Records:
{context}

Question: {question}
"""
        }],
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()

# ═══════════════════════════════════════
# CLI LOOP
# ═══════════════════════════════════════
if __name__ == "__main__":
    print("💬 Ask medical questions (type 'exit' to quit)\n")

    while True:
        q = input("❓ Your question: ")

        if q.lower() == "exit":
            break

        answer = ask(q, patient_id="mr_ramesh")
        print("\n💡 Answer:", answer, "\n")
