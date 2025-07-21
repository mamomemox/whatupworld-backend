from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from openai import OpenAIError
import httpx
import asyncio
import json
import traceback
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")
N8N_WEBHOOK_URL = "https://primary-production-77f62.up.railway.app/webhook-test/country-report"

@app.get("/")
async def root():
    return {
        "status": "API is running", 
        "webhook": N8N_WEBHOOK_URL,
        "openai_key": "***" + str(openai.api_key)[-4:] if openai.api_key else "MISSING"
    }

@app.get("/api/generate")
async def generate(country: str):
    logger.info(f"🚀 === REQUEST START: {country} ===")
    
    # Always return success for debugging
    try:
        async with httpx.AsyncClient() as client:
            logger.info(f"📤 Calling n8n: {N8N_WEBHOOK_URL}")
            logger.info(f"📤 Payload: {{'country': '{country}'}}")
            
            try:
                response = await client.post(
                    N8N_WEBHOOK_URL,
                    json={"country": country},
                    timeout=60.0,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "FastAPI-Backend/1.0"
                    }
                )
                
                logger.info(f"📊 n8n Status: {response.status_code}")
                logger.info(f"📋 n8n Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    response_text = response.text
                    logger.info(f"✅ n8n Response Length: {len(response_text)} chars")
                    logger.info(f"🔍 Response preview: {response_text[:100]}...")
                    
                    # Debug HTML content
                    debug_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="UTF-8">
                        <title>Debug Report - {country}</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                            .debug {{ background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                            .success {{ background: #d4edda; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                            .content {{ background: #fff; border: 1px solid #ddd; padding: 20px; border-radius: 5px; max-height: 500px; overflow: auto; }}
                            pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow: auto; font-size: 12px; }}
                        </style>
                    </head>
                    <body>
                        <h1>🎉 SUCCESS! Backend → n8n Connection Working</h1>
                        
                        <div class="success">
                            <h3>✅ Connection Details:</h3>
                            <strong>Country:</strong> {country}<br>
                            <strong>n8n URL:</strong> {N8N_WEBHOOK_URL}<br>
                            <strong>Status Code:</strong> {response.status_code}<br>
                            <strong>Response Length:</strong> {len(response_text)} characters<br>
                            <strong>Content-Type:</strong> {response.headers.get('content-type', 'unknown')}
                        </div>
                        
                        <div class="debug">
                            <h3>🔍 n8n Raw Response (first 1000 chars):</h3>
                            <pre>{response_text[:1000]}</pre>
                        </div>
                        
                        <div class="content">
                            <h3>📄 Actual n8n Content:</h3>
                            {response_text if response_text.startswith('<!DOCTYPE html') or response_text.startswith('<html') else f'<pre>{response_text}</pre>'}
                        </div>
                        
                        <div class="debug">
                            <h3>🛠️ Technical Info:</h3>
                            <strong>Backend Status:</strong> ✅ Working<br>
                            <strong>n8n Communication:</strong> ✅ Working<br>
                            <strong>Response Processing:</strong> ✅ Working<br>
                            <strong>Issue:</strong> None detected - everything working!
                        </div>
                    </body>
                    </html>
                    """
                    
                    logger.info("🎯 Returning debug HTML to frontend")
                    return {"html": debug_html}
                
                else:
                    error_text = response.text
                    logger.error(f"❌ n8n Error {response.status_code}: {error_text}")
                    
                    error_html = f"""
                    <div style="max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial;">
                        <h1 style="color: red;">❌ n8n Error {response.status_code}</h1>
                        <div style="background: #fee; padding: 15px; border-radius: 5px;">
                            <p><strong>URL:</strong> {N8N_WEBHOOK_URL}</p>
                            <p><strong>Country:</strong> {country}</p>
                            <p><strong>Error:</strong></p>
                            <pre>{error_text}</pre>
                        </div>
                    </div>
                    """
                    return {"html": error_html}
                
            except httpx.TimeoutException:
                logger.error("⏰ n8n Timeout")
                return {"html": "<div style='padding: 20px;'><h1>⏰ Timeout Error</h1><p>n8n took too long to respond</p></div>"}
                
            except Exception as e:
                logger.error(f"💥 HTTP Error: {e}")
                return {"html": f"<div style='padding: 20px;'><h1>💥 HTTP Error</h1><p>{str(e)}</p></div>"}
    
    except Exception as e:
        logger.error(f"🚨 Critical Error: {e}")
        logger.error(f"🚨 Traceback: {traceback.format_exc()}")
        
        return {"html": f"""
        <div style="padding: 20px; font-family: Arial;">
            <h1 style="color: red;">🚨 Critical Backend Error</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <p><strong>Country:</strong> {country}</p>
            <details>
                <summary>Technical Details</summary>
                <pre>{traceback.format_exc()}</pre>
            </details>
        </div>
        """}

@app.get("/test")
async def test():
    return {"message": "Backend is working", "webhook": N8N_WEBHOOK_URL}

@app.get("/health")
async def health():
    return {"status": "healthy"}
