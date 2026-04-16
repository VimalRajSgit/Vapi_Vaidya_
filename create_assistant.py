import requests
import os
from dotenv import load_dotenv

load_dotenv()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")

YOUR_BACKEND_URL = "https://28a2-2409-40f2-216f-8b11-32d-6f15-1abc-740f.ngrok-free.app"

response = requests.post(
    "https://api.vapi.ai/assistant",
    headers={
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "name": "Vaidya Test",
        "model": {
            "provider": "custom-llm",
            "url": YOUR_BACKEND_URL,
            "model": "vaidya-test"
        },
        "voice": {
            "provider": "azure",
            "voiceId": "kn-IN-GaganNeural"
        },
        "transcriber": {
            "provider": "azure",
            "language": "kn-IN"
        }
        ,
        "firstMessage": "Namaste, I am Vaidya. How can I help you today?"
    }
)

print("Status:", response.status_code)
print("Response:", response.json())
