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
                print(f"🔄 Calling n8n for country: {country}")
                n8n_response = await client.post(
                    N8N_WEBHOOK_URL,
                    json={"country": country},
                    timeout=60.0
                )
                
                print(f"📊 n8n Response Status: {n8n_response.status_code}")
                
                if n8n_response.status_code == 200:
                    n8n_data = n8n_response.text
                    print(f"✅ n8n Response Length: {len(n8n_data)} characters")
                    
                    # Check if it's HTML
                    if n8n_data.strip().startswith('<!DOCTYPE html') or n8n_data.strip().startswith('<html'):
                        print("🎯 Detected HTML response from n8n")
                        return {"html": n8n_data}
                    
                    # Try to parse as JSON
                    try:
                        json_data = json.loads(n8n_data)
                        
                        if "html" in json_data:
                            print("🎯 Found HTML in JSON response")
                            return {"html": json_data["html"]}
                        else:
                            # Format structured JSON response
                            formatted_html = f"""
                            <div class="report-container max-w-4xl mx-auto p-6">
                                <div class="bg-white rounded-lg shadow-lg p-8">
                                    <h1 class="text-[#181111] text-2xl font-bold mb-6 text-center">
                                        📊 Market Insights: {country}
                                    </h1>
                                    <div class="text-[#181111] text-base leading-relaxed">
                                        <pre class="whitespace-pre-wrap bg-gray-50 p-4 rounded border">{json.dumps(json_data, indent=2, ensure_ascii=False)}</pre>
                                    </div>
                                </div>
                            </div>
                            """
                            return {"html": formatted_html}
                            
                    except json.JSONDecodeError:
                        # Format plain text response
                        formatted_html = f"""
                        <div class="report-container max-w-4xl mx-auto p-6">
                            <div class="bg-white rounded-lg shadow-lg p-8">
                                <h1 class="text-[#181111] text-2xl font-bold mb-6 text-center">
                                    📊 Market Data: {country}
                                </h1>
                                <div class="text-[#181111] text-base leading-relaxed">
                                    <div class="bg-blue-50 p-6 rounded-lg border-l-4 border-blue-500">
                                        <h3 class="font-bold text-lg mb-3">Raw Data from n8n:</h3>
                                        <pre class="whitespace-pre-wrap bg-white p-4 rounded border text-sm">{n8n_data}</pre>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """
                        return {"html": formatted_html}
                else:
                    print(f"❌ n8n returned status {n8n_response.status_code}")
                
            except httpx.TimeoutException:
                print(f"⏰ n8n webhook timeout for country: {country}")
            except Exception as e:
                print(f"💥 n8n webhook error: {str(e)}")
        
        # Fallback to OpenAI
        print(f"🤖 Using OpenAI fallback for country: {country}")
        
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
        
        # Better HTML formatting
        formatted_content = ai_text.replace('\n\n', '</p><p>')
        formatted_content = formatted_content.replace('**', '<strong>').replace('**', '</strong>')
        formatted_content = formatted_content.replace('## ', '<h2 class="text-xl font-bold mt-6 mb-3 text-[#181111]">')
        formatted_content = formatted_content.replace('\n', '</h2><p class="mb-4 text-[#181111] leading-relaxed">')
        
        final_html = f"""
        <div class="report-container max-w-4xl mx-auto p-6">
            <div class="bg-white rounded-lg shadow-lg p-8">
                <h1 class="text-[#181111] text-2xl font-bold mb-6 text-center">
                    📊 Market Insights: {country}
                </h1>
                <div class="text-[#181111] text-base leading-relaxed">
                    <div class="bg-orange-50 p-4 rounded-lg mb-6 border-l-4 border-orange-500">
                        <p class="text-sm">⚠️ <strong>Fallback Mode:</strong> Generated by OpenAI (n8n not available)</p>
                    </div>
                    <p class="mb-4">{formatted_content}</p>
                </div>
            </div>
        </div>
        """
        
        return {"html": final_html}
        
    except OpenAIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "n8n_url": N8N_WEBHOOK_URL}
