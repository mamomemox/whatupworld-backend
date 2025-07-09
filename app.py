from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import openai
import os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your OpenAI key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/api/generate")
async def generate(country: str):
    prompt = (
        f"Act as a market intelligence analyst. For {country}, provide the following sections:\n\n"
        f"Title:\nA short catchy headline about the market.\n\n"
        f"Lead:\nA 1-2 sentence overview of current market trends.\n\n"
        f"Latest News:\nA brief 2-3 sentence summary of the latest relevant business news.\n\n"
        f"Regulation Snapshot:\nKey compliance or regulatory updates in 2-3 sentences.\n\n"
        f"Opportunity Highlight:\nOne high-potential export opportunity described in 2-3 sentences."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional market analyst generating concise business reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )

        ai_text = response['choices'][0]['message']['content']

        # Parse the AI response into sections (very basic split based on labels)
        sections = {
            "title": "",
            "lead": "",
            "news": "",
            "regulation": "",
            "opportunity": ""
        }

        for line in ai_text.split('\n'):
            if line.lower().startswith('title:'):
                sections['title'] = line[6:].strip()
            elif line.lower().startswith('lead:'):
                sections['lead'] = line[5:].strip()
            elif line.lower().startswith('latest news:'):
                sections['news'] = line[12:].strip()
            elif line.lower().startswith('regulation snapshot:'):
                sections['regulation'] = line[20:].strip()
            elif line.lower().startswith('opportunity highlight:'):
                sections['opportunity'] = line[22:].strip()

        return sections

    except Exception as e:
        print("OpenAI error:", e)
        return {
            "title": "Error",
            "lead": "Failed to generate insights.",
            "news": "",
            "regulation": "",
            "opportunity": ""
        }
