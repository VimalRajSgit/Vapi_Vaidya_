from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
import os
import json
import time
from dotenv import load_dotenv


load_dotenv()
app = FastAPI()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))



class Message(BaseModel):
    role: str
    content: str

class VAPIRequest(BaseModel):
    messages: list[Message]

@app.post("/chat/completions")
async def chat(req: VAPIRequest):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are Vaidya, an AI health assistant. Answer in simple Kannada."},
            *[{"role": m.role, "content": m.content} for m in req.messages]
        ],
        stream=True  # enable streaming
    )

    def generate():
        for chunk in response:
            delta = chunk.choices[0].delta
            if delta.content:
                data = {
                    "id": "chatcmpl-test",
                    "object": "chat.completion.chunk",
                    "choices": [{
                        "index": 0,
                        "delta": {"role": "assistant", "content": delta.content},
                        "finish_reason": None
                    }]
                }
                yield f"data: {json.dumps(data)}\n\n"
        # send final done chunk
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/")
def health():
    return {"status": "ok"}
