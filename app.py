from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from openai import OpenAIError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
async def root():
    return {"status": "API is running"}

@app.get("/api/generate")
async def generate(country: str):
    prompt = (
        f"Act as a market intelligence analyst. For {country}, provide structured insights in this format:\n\n"
        f"(1) Title: ...\n(2) Lead Text: ...\n(3) Latest News: ...\n(4) Regulation Snapshot: ...\n(5) Export Opportunities: ..."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        ai_text = response.choices[0].message.content
        return {"content": ai_text.replace('\n', '<br>')}
    except OpenAIError as e:
        return {"content": "Failed to generate insights: " + str(e)}
