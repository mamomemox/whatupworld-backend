# app.py (Backend)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

@app.get("/api/generate")
async def generate(country: str):
    prompt = (
        f"Act as a market intelligence analyst. For {country}, provide:\n"
        "1. Title and lead text about the market\n"
        "2. Latest business news\n"
        "3. Regulation snapshot\n"
        "4. Export opportunity highlight. Keep each section concise."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    # Split content intelligently here if needed
    return {
        "title": f"Market Insights for {country}",
        "lead": content.split('\n')[0],
        "latest_news": content.split('\n')[1],
        "regulation": content.split('\n')[2],
        "opportunity": content.split('\n')[3],
    }
