"""
medical_rag.py
Medical Transcription RAG System (FIXED VERSION)
"""

import os, json, uuid, requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from groq import Groq
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams,
    PointStruct, Filter, FieldCondition, MatchValue,
    PayloadSchemaType
)
from sentence_transformers import SentenceTransformer
import pypdf

load_dotenv()

# ── Config ─────────────────────────────────────────────
QDRANT_URL     = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
PRESCRIPTO_KEY = os.getenv("PRESCRIPTO_API_KEY")
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")

COLLECTION_NAME = "medical_records"
EMBED_MODEL     = "all-MiniLM-L6-v2"
EMBED_DIM       = 384
GROQ_MODEL      = "llama-3.3-70b-versatile"

# ── Clients ────────────────────────────────────────────
qdrant   = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
groq     = Groq(api_key=GROQ_API_KEY)
embedder = SentenceTransformer(EMBED_MODEL)

# ═══════════════════════════════════════════════════════
# 1. COLLECTION SETUP (FIXED)
# ═══════════════════════════════════════════════════════
def ensure_collection():
    existing = [c.name for c in qdrant.get_collections().collections]

    if COLLECTION_NAME not in existing:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBED_DIM, distance=Distance.COSINE),
        )
        print(f"✅ Created collection: {COLLECTION_NAME}")
    else:
        print(f"✔ Collection exists: {COLLECTION_NAME}")

    # 🔥 FIX: create index for filtering
    qdrant.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="patient_id",
        field_schema=PayloadSchemaType.KEYWORD
    )

    print("✅ Index ensured for patient_id")

# ═══════════════════════════════════════════════════════
# 2. PDF → SUMMARY → STORE
# ═══════════════════════════════════════════════════════
def read_pdf(path: str) -> str:
    reader = pypdf.PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

PROMPT = """
Return ONLY valid JSON. No explanation. No markdown.

Format:
{{
  "patient_name": "",
  "patient_age": "",
  "visit_date": "",
  "diagnoses": [],
  "medications_prescribed": [],
  "clinical_summary": ""
}}

TRANSCRIPT:
{transcript}
"""

def summarise(raw):
    resp = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": PROMPT.format(transcript=raw)}],
        temperature=0.1,
    )
    print("RAW RESPONSE:\n", resp.choices[0].message.content)
    return json.loads(resp.choices[0].message.content)

def ingest_transcript(pdf_path, patient_id=None):
    print(f"📄 {pdf_path}")
    raw = read_pdf(pdf_path)
    summary = summarise(raw)

    text = summary.get("clinical_summary", "")
    vector = embedder.encode(text).tolist()

    payload = {
        "type": "transcript",
        "patient_id": patient_id or "unknown",
        **summary
    }

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload)]
    )

# ═══════════════════════════════════════════════════════
# 3. IMAGE → OCR → STORE
# ═══════════════════════════════════════════════════════
def extract_prescription(img):
    url = "https://www.prescriptoai.com/api/v1/prescription/extract"
    headers = {"Authorization": f"Bearer {PRESCRIPTO_KEY}"}

    with open(img, "rb") as f:
        r = requests.post(url, headers=headers, files={"prescription": f})

    return r.json()

def ingest_prescription(img_path, patient_id=None):
    print(f"💊 {img_path}")
    data = extract_prescription(img_path)

    meds = data.get("medications", [])
    text = " ".join(str(m) for m in meds)

    vector = embedder.encode(text).tolist()

    payload = {
        "type": "prescription",
        "patient_id": patient_id or "unknown",
        "medications": meds
    }

    qdrant.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload)]
    )

# ═══════════════════════════════════════════════════════
# 4. SEARCH (FIXED)
# ═══════════════════════════════════════════════════════
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

# ═══════════════════════════════════════════════════════
# 5. RAG QUERY
# ═══════════════════════════════════════════════════════
def ask(q, patient_id=None):
    hits = search_records(q, patient_id)

    context = "\n".join(str(h.payload) for h in hits)

    resp = groq.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:{q}"
        }]
    )

    return resp.choices[0].message.content

# ═══════════════════════════════════════════════════════
# 6. MAIN
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    ensure_collection()

    # 📂 Load PDFs
    for pdf in Path("data").glob("*.pdf"):
        ingest_transcript(pdf, "mr_ramesh")

    # 🖼 Load images
    for img in Path("images").glob("*"):
        ingest_prescription(img, "mr_ramesh")

    # 🔍 Query
    print(ask("What medications is he taking?", "mr_ramesh"))
