from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from openai import OpenAIError
import httpx
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")
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
                    timeout=60.0
                )
                
                if n8n_response.status_code == 200:
                    n8n_data = n8n_response.text
                    
                    # Check if it's HTML
                    if n8n_data.strip().startswith('<!DOCTYPE html') or n8n_data.strip().startswith('<html'):
                        return {"html": n8n_data}
                    
                    # Try to parse as JSON
                    try:
                        json_data = json.loads(n8n_data)
                        if "html" in json_data:
                            return {"html": json_data["html"]}
                        else:
                            # Format with Tailwind
                            formatted_html = f"""
                            <div class="max-w-4xl mx-auto p-6">
                                <div class="bg-white rounded-lg shadow-lg p-8">
                                    <h1 class="text-[#181111] text-2xl font-bold mb-6 text-center">
                                        📊 Market Insights: {country}
                                    </h1>
                                    <div class="text-[#181111] text-base leading-relaxed">
                                        <div class="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
                                            <h3 class="font-bold text-lg mb-3">Data from n8n:</h3>
                                            <pre class="bg-white p-4 rounded border text-sm overflow-auto">{json.dumps(json_data, indent=2, ensure_ascii=False)}</pre>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """
                            return {"html": formatted_html}
                            
                    except json.JSONDecodeError:
                        # Format with Tailwind
                        formatted_html = f"""
                        <div class="max-w-4xl mx-auto p-6">
                            <div class="bg-white rounded-lg shadow-lg p-8">
                                <h1 class="text-[#181111] text-2xl font-bold mb-6 text-center">
                                    📊 Market Data: {country}
                                </h1>
                                <div class="text-[#181111] text-base leading-relaxed">
                                    <div class="bg-yellow-50 p-6 rounded-lg border-l-4 border-yellow-500">
                                        <h3 class="font-bold text-lg mb-3">Raw Response from n8n:</h3>
                                        <pre class="bg-white p-4 rounded border text-sm overflow-auto">{n8n_data[:2000]}...</pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """
                        return {"html": formatted_html}
                
            except httpx.TimeoutException:
                pass
            except Exception as e:
                print(f"n8n error: {e}")
        
        # OpenAI Fallback with Tailwind Design
        prompt = f"Create a comprehensive market report for {country}. Include economic indicators, trade data, and business opportunities."

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_text = response.choices[0].message.content
        
        # Format with proper Tailwind styling
        formatted_content = ai_text.replace('\n\n', '</p><p class="mb-4">')
        formatted_content = formatted_content.replace('**', '<strong>').replace('**', '</strong>')
        formatted_content = formatted_content.replace('## ', '<h2 class="text-xl font-bold mt-6 mb-3 text-[#181111]">')
        formatted_content = formatted_content.replace('\n', '</h2><p class="mb-4 text-[#181111] leading-relaxed">')
        
        final_html = f"""
        <div class="max-w-4xl mx-auto p-6">
            <div class="bg-white rounded-lg shadow-lg p-8">
                <h1 class="text-[#181111] text-2xl font-bold mb-6 text-center">
                    📊 Market Insights: {country}
                </h1>
                <div class="text-[#181111] text-base leading-relaxed">
                    <div class="bg-orange-50 p-4 rounded-lg mb-6 border-l-4 border-orange-500">
                        <p class="text-sm">⚠️ <strong>Fallback Mode:</strong> Generated by OpenAI (n8n not available)</p>
                    </div>
                    <div class="prose max-w-none">
                        <p class="mb-4">{formatted_content}</p>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return {"html": final_html}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "n8n_url": N8N_WEBHOOK_URL}
