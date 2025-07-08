from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read the API key directly from environment variables (Render's Environment tab)
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client correctly
client = openai.OpenAI(api_key=api_key)

@app.get("/generate")
async def generate(country: str):
    prompt = f"Give me a market update for Swiss exporters in {country}: latest news, regulations, and export opportunities."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert on international trade, writing for Swiss exporters."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500
    )

    text = response.choices[0].message.content

    return {
        "title": f"Market Update for {country}",
        "lead": f"Here’s the latest for Swiss businesses in {country}:",
        "image": f"https://source.unsplash.com/800x400/?{country}",
        "insights": [
            {"subtitle": "Market Overview", "content": text}
        ]
    }
