import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import openai

app = FastAPI()

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

@app.get("/generate")
async def generate(country: str):
    prompt = f"""
You are an AI market analyst. Generate a structured market report for {country} including:

1. Overview Market: Summarize the current state of the market, economy, and key sectors.
2. Latest News: Highlight 1-2 top recent developments relevant for exporters.
3. Export Opportunities: Identify promising export opportunities and sectors.

Be concise, engaging, and informative. Each section should have 3-5 sentences.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates market insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7,
        )
        content = response.choices[0].message.content.strip()
        return JSONResponse(content={"text": content})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)