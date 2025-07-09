from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import openai

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your API key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/api/generate")
async def generate(request: Request):
    country = request.query_params.get('country', 'Germany')

    prompt = f"""
Act as a market intelligence analyst. For {country}, provide:
(1) a concise market overview (2-3 sentences),
(2) latest business news (2-3 sentences),
(3) export opportunities (2-3 sentences).
Be informative, useful, and avoid filler.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can switch to gpt-4o if you have access
            messages=[
                {"role": "system", "content": "You are a helpful market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7,
        )

        content = response['choices'][0]['message']['content']

        # Simple splitting — AI text should have 3 clear sections
        parts = content.split('\n\n')
        overview = parts[0] if len(parts) > 0 else ""
        news = parts[1] if len(parts) > 1 else ""
        opportunities = parts[2] if len(parts) > 2 else ""

        return {
            "overview": overview.strip(),
            "news": news.strip(),
            "opportunities": opportunities.strip()
        }

    except openai.error.OpenAIError as e:
        return {"error": str(e)}
