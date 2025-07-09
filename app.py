from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

app = FastAPI()

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your OpenAI key securely
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/api/generate")
async def generate(country: str):
    prompt = (
        f"Act as a market intelligence analyst. For {country}, provide: "
        f"(1) concise market overview, (2) latest business news, (3) export opportunities. "
        f"Each section 2-3 sentences."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        ai_text = response['choices'][0]['message']['content']

        # Optional: Add basic HTML wrapping for Page 2
        content_html = f"<p>{ai_text.replace('\n', '<br>')}</p>"

        return {"content": content_html}
    except Exception as e:
        print("OpenAI error:", e)
        return {"content": "Failed to generate insights."}
