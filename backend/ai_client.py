import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

async def ask_gemini(prompt: str) -> str:
    """
    Sends a prompt to Groq AI and gets a response back.
    We kept the function name ask_gemini so nothing else needs to change.
    """
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not found in .env file")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 2048
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(GROQ_URL, headers=headers, json=body)
        
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def ask_ai_json(prompt: str) -> dict:
    """
    Same as ask_gemini but returns parsed JSON.
    """
    json_prompt = prompt + "\n\nIMPORTANT: Reply with valid JSON only. No extra text, no markdown, no code blocks. Just the raw JSON object."

    raw = await ask_gemini(json_prompt)

    # Clean up in case model adds markdown code fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)