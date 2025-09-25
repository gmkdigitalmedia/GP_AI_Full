from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
import requests
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urlparse
from typing import List, Optional
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Business Intelligence Agent API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class BusinessContextRequest(BaseModel):
    business_description: str
    num_competitors: int = 5

class CompetitorInfo(BaseModel):
    name: str
    url: str
    domain: str
    description: str
    found_via: str

class ScrapedData(BaseModel):
    url: str
    title: str
    meta_description: str
    content: str
    pricing_info: List[str]
    status: str

class AnalysisResponse(BaseModel):
    competitors: List[CompetitorInfo]
    scraped_data: List[ScrapedData]
    analysis: str
    metrics: dict

# Business Logic
async def find_competitors_with_ai(business_description: str, num_competitors: int):
    """Use AI to identify competitors"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not found in environment variables")
        openai.api_key = api_key

        prompt = f"""
Based on this business description: "{business_description}"

Identify the top {num_competitors} competitor companies in this specific industry/market. For each competitor, provide:
1. Company name
2. Website URL (must be a real, working website)
3. Brief description of what they do

Focus on direct competitors or companies in the same market segment as described.

Format your response as a JSON list like this:
[
  {{"name": "Company Name", "url": "https://company.com", "description": "What they do"}},
  {{"name": "Company Name", "url": "https://company.com", "description": "What they do"}}
]

Only return the JSON, no other text.
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a business intelligence expert who knows major companies across all industries. Provide accurate, real company information with working websites."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.3
        )

        # Parse the JSON response
        ai_response = response.choices[0].message.content.strip()

        # Clean up the response
        if '```json' in ai_response:
            ai_response = ai_response.split('```json')[1].split('```')[0]
        elif '```' in ai_response:
            ai_response = ai_response.split('```')[1]
        if ai_response.startswith('json'):
            ai_response = ai_response[4:]

        ai_response = ai_response.strip()
        competitors_data = json.loads(ai_response)

        if not isinstance(competitors_data, list):
            raise HTTPException(status_code=500, detail="AI returned invalid data format")

        # Convert to our format
        competitors = []
        for comp in competitors_data:
            if 'url' in comp and 'name' in comp:
                competitors.append(CompetitorInfo(
                    name=comp['name'],
                    url=comp['url'],
                    domain=urlparse(comp['url']).netloc,
                    description=comp.get('description', ''),
                    found_via=f"AI identified: {comp.get('description', comp['name'])}"
                ))

        return competitors[:num_competitors]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI competitor search failed: {str(e)}")

async def scrape_website_async(session: aiohttp.ClientSession, url: str):
    """Scrape website content asynchronously"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status != 200:
                return ScrapedData(
                    url=url,
                    title="Error",
                    meta_description="",
                    content=f"HTTP {response.status}",
                    pricing_info=[],
                    status="error"
                )

            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')

            # Extract key information
            title = soup.find('title')
            title = title.get_text() if title else 'No title found'

            # Extract meta description
            meta_desc = ''
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '')

            # Extract main text content
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Limit text length
            text = text[:3000] if len(text) > 3000 else text

            # Extract pricing information
            pricing_keywords = ['price', 'pricing', 'cost', 'fee', 'subscription', '$', 'free', 'premium']
            pricing_info = []
            for keyword in pricing_keywords:
                pattern = rf'.{{0,50}}{keyword}.{{0,50}}'
                matches = re.findall(pattern, text, re.IGNORECASE)
                pricing_info.extend(matches[:2])

            return ScrapedData(
                url=url,
                title=title,
                meta_description=meta_desc,
                content=text,
                pricing_info=pricing_info,
                status="success"
            )

    except Exception as e:
        return ScrapedData(
            url=url,
            title="Error",
            meta_description="",
            content=f"Error scraping website: {str(e)}",
            pricing_info=[],
            status="error"
        )

async def analyze_competitors_with_ai(competitors_data: List[ScrapedData], business_context: str):
    """Use AI to analyze competitor data"""
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # Prepare competitor information
        competitor_info = ""
        for i, comp in enumerate([c for c in competitors_data if c.status == 'success'], 1):
            competitor_info += f"""
COMPETITOR {i}: {comp.title}
URL: {comp.url}
Description: {comp.meta_description}
Content Sample: {comp.content[:1000]}
Pricing Info: {'; '.join(comp.pricing_info[:3]) if comp.pricing_info else 'Not found'}

---
"""

        prompt = f"""
As a business intelligence analyst with deep pharmaceutical industry knowledge, analyze these competitors for: "{business_context}"

COMPETITOR DATA:
{competitor_info}

Based on the original business query and competitor data, provide specific analysis answering:

**DIRECT ANSWERS TO THE BUSINESS QUESTION:**
- Which company appears to be the market leader based on website content?
- What specific heart disease medications or treatments are highlighted?
- Who has the strongest positioning in cardiovascular medicine?
- Revenue/market share indicators found on websites

**COMPETITIVE LANDSCAPE ANALYSIS:**
1. **Market Leadership & Sales Volume**
   - Evidence of market dominance from website content
   - Product portfolio strength in the specific area
   - Geographic reach and market presence

2. **Product Specialization**
   - Specific treatments/medicines mentioned for the business area
   - R&D pipeline strength
   - Clinical trial activity

3. **Strategic Positioning**
   - How each company positions itself in this specific market
   - Unique value propositions for the business area
   - Target market approach

4. **Key Performance Indicators**
   - Any revenue, market share, or sales data found
   - Patient reach numbers
   - Global presence indicators

**ACTIONABLE INSIGHTS:**
- Top performer identification with evidence
- Market gaps and opportunities
- Competitive advantages analysis

Focus on answering the specific business question while providing strategic context.
"""

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a senior business intelligence analyst specializing in competitive analysis and market research."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# API Endpoints
@app.get("/")
async def root():
    return {"message": "Business Intelligence Agent API", "status": "running"}

@app.post("/analyze-competitors")
async def analyze_business(request: BusinessContextRequest):
    """Main endpoint for business intelligence analysis"""
    try:
        # Step 1: Find competitors using AI
        competitors = await find_competitors_with_ai(
            request.business_description,
            request.num_competitors
        )

        if not competitors:
            raise HTTPException(status_code=400, detail="Could not identify competitors")

        # Step 2: Scrape competitor websites concurrently
        async with aiohttp.ClientSession() as session:
            scraping_tasks = [
                scrape_website_async(session, competitor.url)
                for competitor in competitors
            ]
            scraped_data = await asyncio.gather(*scraping_tasks)

        # Step 3: Analyze competitors using AI
        analysis = await analyze_competitors_with_ai(
            scraped_data,
            request.business_description
        )

        # Calculate metrics
        successful_scrapes = len([data for data in scraped_data if data.status == 'success'])
        total_content_length = sum(len(data.content) for data in scraped_data)
        pricing_data_found = len([data for data in scraped_data if data.pricing_info])

        metrics = {
            "competitors_analyzed": len(competitors),
            "successful_scrapes": successful_scrapes,
            "total_content_processed": total_content_length,
            "pricing_data_found": pricing_data_found,
            "analysis_length": len(analysis)
        }

        return {
            "business_description": request.business_description,
            "competitors": [
                {
                    "name": comp.name,
                    "website": comp.url,
                    "analysis": f"Company: {comp.name}\nWebsite: {comp.url}\nBusiness Focus: {data.title}\n\nKey Content: {data.content[:300]}..."
                }
                for comp, data in zip(competitors, scraped_data) if data.status == 'success'
            ],
            "analysis": analysis
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)