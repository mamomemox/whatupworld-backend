from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from openai import OpenAIError
import httpx
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

# n8n Webhook URL
N8N_WEBHOOK_URL = "https://primary-production-77f62.up.railway.app/webhook/country-report"

@app.get("/")
async def root():
    return {"status": "API is running"}

@app.get("/api/generate")
async def generate(country: str):
    try:
        # Call n8n workflow
        async with httpx.AsyncClient() as client:
            try:
                n8n_response = await client.post(
                    N8N_WEBHOOK_URL,
                    json={"country": country},
                    timeout=30.0
                )
                
                if n8n_response.status_code == 200:
                    n8n_data = n8n_response.text
                    
                    if n8n_data.strip().startswith('<!DOCTYPE html') or n8n_data.strip().startswith('<html'):
                        return {"html": n8n_data}
                    else:
                        try:
                            import json
                            json_data = json.loads(n8n_data)
                            if "html" in json_data:
                                return {"html": json_data["html"]}
                            else:
                                return {"content": n8n_data}
                        except:
                            return {"content": n8n_data}
                
            except httpx.TimeoutException:
                print(f"n8n webhook timeout for country: {country}")
            except Exception as e:
                print(f"n8n webhook error: {e}")
        
        # Fallback to OpenAI
        prompt = (
            f"Act as a market intelligence analyst. Create a comprehensive report for {country} with the following structure:\n\n"
            f"🌍 **Market Report: {country}**\n\n"
            f"## 📊 Executive Summary\n"
            f"[2-3 key insights about the market]\n\n"
            f"## 💰 Key Economic Indicators\n"
            f"[GDP, inflation, unemployment, etc.]\n\n"
            f"## 🏭 Industry Analysis\n"
            f"[Main sectors and growth opportunities]\n\n"
            f"## 📈 Market Trends\n"
            f"[Current trends and future outlook]\n\n"
            f"## 🌐 Trade & Export Opportunities\n"
            f"[Key trading partners and export potential]\n\n"
            f"## 🔮 Recommendations\n"
            f"[Strategic recommendations for businesses]\n\n"
            f"Please provide specific data, statistics, and actionable insights."
        )

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert market analyst with deep knowledge of global markets, trade, and economic trends."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        ai_text = response.choices[0].message.content
        
        formatted_content = ai_text.replace('\n\n', '</p><p>')
        formatted_content = formatted_content.replace('**', '<strong>').replace('**', '</strong>')
        formatted_content = formatted_content.replace('## ', '<h2>').replace('\n', '</h2><p>')
        formatted_content = f"<p>{formatted_content}</p>"
        
        return {"content": formatted_content}
        
    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "n8n_url": N8N_WEBHOOK_URL}
