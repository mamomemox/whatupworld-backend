from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import os

# Initialize FastAPI app
app = FastAPI()

# CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Request model for POST
class GenerateRequest(BaseModel):
    country: str

# Route for AI generation
@app.post("/api/generate")
async def generate_content(data: GenerateRequest):
    country = data.country

    prompt = f"""
Act as a market intelligence analyst. For {country}, provide:
1. A concise market overview (2-3 sentences).
2. The latest business news (2-3 sentences).
3. Export opportunities (2-3 sentences).

Respond in plain text with clear separation between sections using ### as delimiter. No lists.
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4o" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant generating market insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7,
        )

        ai_text = response['choices'][0]['message']['content']
        # Split into sections based on delimiter
        sections = ai_text.split("###")
        result = {
            "title": f"{country} Market Insights",
            "lead": sections[0].strip() if len(sections) > 0 else "",
            "latest_news": sections[1].strip() if len(sections) > 1 else "",
            "regulation": sections[2].strip() if len(sections) > 2 else "",
            "opportunity": sections[3].strip() if len(sections) > 3 else "",
        }

        return result

    except openai.error.OpenAIError as e:
        return {"error": str(e)}
