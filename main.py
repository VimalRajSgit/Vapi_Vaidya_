from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import time
import os
from dotenv import load_dotenv

# 🔥 import your RAG function
from query_rag import ask

load_dotenv()

app = FastAPI()

# ── Models ─────────────────────────────
class Message(BaseModel):
    role: str
    content: str

class VAPIRequest(BaseModel):
    messages: list[Message]

# ──────────────────────────────────────
# CHAT ENDPOINT (RAG ENABLED)
# ──────────────────────────────────────
@app.post("/chat/completions")
async def chat(req: VAPIRequest):

    # 🧠 Get latest user message
    user_message = req.messages[-1].content

    # 🔥 Call your RAG system instead of direct LLM
    answer = ask(user_message, patient_id="mr_ramesh")

    # ── Streaming response ─────────────
    def generate():
        words = answer.split()

        for word in words:
            chunk = {
                "id": "chatcmpl-rag",
                "object": "chat.completion.chunk",
                "choices": [{
                    "index": 0,
                    "delta": {
                        "role": "assistant",
                        "content": word + " "
                    },
                    "finish_reason": None
                }]
            }

            yield f"data: {json.dumps(chunk)}\n\n"
            time.sleep(0.03)  # smooth streaming feel

        # final done signal
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ──────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────
@app.get("/")
def health():
    return {"status": "ok"}
