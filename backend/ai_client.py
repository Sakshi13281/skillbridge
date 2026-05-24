import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

async def ask_ai(prompt: str) -> str:
    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not found in .env file")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }

    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2048
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(GROQ_URL, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def ask_ai_json(prompt: str) -> dict:
    json_prompt = prompt + "\n\nCRITICAL RULES:\n1. Return ONLY a raw JSON object\n2. No markdown, no code blocks, no backticks\n3. No text before or after the JSON\n4. Must start with { and end with }\n5. Use double quotes for all strings\n6. No trailing commas"

    raw = await ask_ai(json_prompt)
    raw = raw.strip()

    # Remove markdown code fences
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                raw = part
                break

    # Find JSON boundaries — strips any extra text before/after
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Ask Groq to fix its own broken JSON
        fix_prompt = f"Fix this broken JSON. Return only the corrected JSON object, nothing else:\n{raw}"
        fixed = await ask_ai(fix_prompt)
        fixed = fixed.strip()
        start = fixed.find("{")
        end = fixed.rfind("}") + 1
        if start != -1 and end > start:
            fixed = fixed[start:end]
        return json.loads(fixed)