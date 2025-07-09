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
        f"Act as a market intelligence analyst. For {country}, generate:\n"
        f"1. A catchy market-focused title (max 12 words)\n"
        f"2. A short lead text (1-2 sentences)\n"
        f"3. Latest business news (2-3 sentences)\n"
        f"4. Regulation snapshot (2-3 sentences)\n"
        f"5. Export opportunity highlight (2-3 sentences).\n"
        f"Reply in this JSON format:\n"
        f"{{'title': ..., 'lead': ..., 'news': ..., 'regulation': ..., 'opportunity': ...}}"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert market intelligence analyst creating concise reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )

        content = response['choices'][0]['message']['content']

        # Convert single quotes to double quotes if needed (very basic)
        import json
        content = content.replace("'", '"')
        data = json.loads(content)

        return data
    except Exception as e:
        print("Error:", e)
        return {
            "title": "Market Insights Unavailable",
            "lead": "We couldn't generate insights at this time.",
            "news": "",
            "regulation": "",
            "opportunity": ""
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)
