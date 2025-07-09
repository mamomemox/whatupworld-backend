from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import openai

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OpenAI API key
api_key = os.getenv("OPENAI_API_KEY") or "sk-your-real-key-here"
client = openai.OpenAI(api_key=api_key)

@app.get("/api/generate")
async def generate(country: str):
    prompt = (
        f"Act as a market intelligence analyst. For {country}, provide:\n"
        f"(1) A concise market overview,\n"
        f"(2) The latest business news relevant to {country},\n"
        f"(3) Export opportunities specific to {country}.\n"
        f"Each section should be 2-3 informative sentences. Keep it professional and insightful."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
        )
        ai_text = response.choices[0].message.content.strip()
        return {"result": ai_text}
    except Exception as e:
        return {"error": str(e)}
