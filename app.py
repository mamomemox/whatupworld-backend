from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import openai

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/api/generate")
async def generate(country: str):
    prompt = f"""
Act as a market intelligence analyst. For {country}, provide:
1. Concise market overview (2-3 sentences).
2. Latest business news (2-3 sentences).
3. Export opportunities (2-3 sentences).
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or use "gpt-4" if available
            messages=[
                {"role": "system", "content": "You are an expert market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        ai_text = response.choices[0].message.content.strip()
        return {"result": ai_text}

    except Exception as e:
        return {"error": str(e)}
