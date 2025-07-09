# app.py (Backend)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

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
    prompt = (
        f"Act as a market intelligence analyst. For {country}, provide structured insights in this format:\n"
        f"(1) Title: A catchy, 1-line market headline relevant to the selected country.\n"
        f"(2) Lead Text: 3 concise lines summarizing the market opportunity or trend.\n"
        f"(3) Latest News: 5-6 lines highlighting a key piece of recent business news for this market.\n"
        f"(4) Regulation Snapshot: 5-6 lines about key regulatory factors or legal updates exporters should know.\n"
        f"(5) Export Opportunities: 5-6 lines describing specific export or partnership opportunities in this market."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        ai_text = response['choices'][0]['message']['content']
        html_content = '<br>'.join(ai_text.splitlines())
        return {"content": html_content}

    except Exception as e:
        print("OpenAI error:", e)
        return {"content": "<p class='text-red-600'>Failed to generate insights.</p>"}
