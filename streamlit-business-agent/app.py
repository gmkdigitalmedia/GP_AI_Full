import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urlparse, urljoin, quote_plus
import json

# Page configuration
st.set_page_config(
    page_title="Business Intelligence Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark theme CSS
st.markdown("""
<style>
    /* Main app dark theme */
    .stApp {
        background-color: #0e1117 !important;
        color: #fafafa !important;
    }

    /* Sidebar dark theme */
    .css-1d391kg, .css-1lcbmhc, .css-17eq0hr {
        background-color: #1a1a1a !important;
        color: #fafafa !important;
    }

    /* Sidebar content */
    .css-1d391kg * {
        color: #fafafa !important;
    }

    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #262626 !important;
        color: #fafafa !important;
        border: 1px solid #444 !important;
    }

    /* Text areas */
    .stTextArea > div > div > textarea {
        background-color: #262626 !important;
        color: #fafafa !important;
        border: 1px solid #444 !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #262626 !important;
        color: #fafafa !important;
        border: 1px solid #444 !important;
    }

    /* Radio buttons */
    .stRadio > div {
        background-color: transparent !important;
    }

    .stRadio label {
        color: #fafafa !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #00d4ff !important;
        color: #000 !important;
        border: none !important;
    }

    /* Sliders */
    .stSlider > div > div > div {
        color: #fafafa !important;
    }

    /* Headers */
    .main-header {
        font-size: 2.5rem;
        color: #00d4ff !important;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .sub-header {
        font-size: 1.2rem;
        color: #a0a0a0 !important;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Custom components */
    .agent-status {
        background: linear-gradient(90deg, #1e3a8a, #3b82f6) !important;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #00d4ff;
        color: #fafafa !important;
    }

    .analysis-card {
        background-color: #1a1a1a !important;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 1px solid #333;
        color: #fafafa !important;
    }

    .competitor-card {
        background-color: #262626 !important;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #00d4ff;
        color: #fafafa !important;
    }

    .metric-box {
        background-color: #1a1a1a !important;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #333;
        color: #fafafa !important;
    }

    /* Success/Error messages */
    .success-message {
        background-color: #1a4d3a !important;
        color: #4ade80 !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #22c55e;
    }

    .error-message {
        background-color: #4d1a1a !important;
        color: #f87171 !important;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ef4444;
    }

    /* Force all text to be light */
    div[data-testid="stSidebar"] * {
        color: #fafafa !important;
    }

    /* Placeholder text */
    ::placeholder {
        color: #888 !important;
    }

    /* Progress bars */
    .stProgress > div > div {
        background-color: #00d4ff !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
def find_competitors_with_ai(business_description, num_competitors=5, api_key=None):
    """Use AI to identify competitors based on business description"""
    try:
        if not api_key:
            return []

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

        # Clean up the response if it has extra text
        if '```json' in ai_response:
            ai_response = ai_response.split('```json')[1].split('```')[0]
        elif '```' in ai_response:
            ai_response = ai_response.split('```')[1]
        if ai_response.startswith('json'):
            ai_response = ai_response[4:]

        ai_response = ai_response.strip()

        # Parse JSON
        competitors_data = json.loads(ai_response)

        # Validate the data structure
        if not isinstance(competitors_data, list):
            st.error("AI returned invalid data format")
            return []

        # Convert to our format
        competitors = []
        for comp in competitors_data:
            if 'url' in comp and 'name' in comp:
                competitors.append({
                    'url': comp['url'],
                    'domain': urlparse(comp['url']).netloc,
                    'found_via': f"AI identified: {comp.get('description', comp['name'])}"
                })

        return competitors[:num_competitors]

    except Exception as e:
        st.warning(f"AI competitor search failed: {str(e)}")
        return []


def find_competitors(business_description, num_competitors=5, api_key=None):
    """Find competitors using AI intelligence"""
    try:
        st.info("Agent using AI to identify competitors...")

        # AI-powered competitor discovery
        competitors = find_competitors_with_ai(business_description, num_competitors, api_key)

        if competitors:
            st.success(f"AI identified {len(competitors)} competitors")
            return competitors
        else:
            st.error("AI could not identify competitors. Please refine your business description or check your API key.")
            return []

    except Exception as e:
        st.error(f"Error finding competitors: {str(e)}")
        return []

def scrape_website(url):
    """Scrape website content and extract key business information"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract key information
        title = soup.find('title').get_text() if soup.find('title') else 'No title found'

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
            pricing_info.extend(matches[:2])  # Limit to 2 matches per keyword

        return {
            'url': url,
            'title': title,
            'meta_description': meta_desc,
            'content': text,
            'pricing_info': pricing_info,
            'status': 'success'
        }

    except Exception as e:
        return {
            'url': url,
            'title': 'Error',
            'meta_description': '',
            'content': f'Error scraping website: {str(e)}',
            'pricing_info': [],
            'status': 'error'
        }

def analyze_competitors(competitor_data, business_context, api_key):
    """Use GPT to analyze competitor information and generate insights"""
    try:
        openai.api_key = api_key

        # Prepare competitor information for analysis
        competitor_info = ""
        for i, comp in enumerate(competitor_data, 1):
            competitor_info += f"""
COMPETITOR {i}: {comp['title']}
URL: {comp['url']}
Description: {comp['meta_description']}
Content Sample: {comp['content'][:1000]}
Pricing Info: {'; '.join(comp['pricing_info'][:3]) if comp['pricing_info'] else 'Not found'}

---
"""

        prompt = f"""
As a business intelligence analyst, analyze these competitors for the business context: "{business_context}"

COMPETITOR DATA:
{competitor_info}

Provide a comprehensive analysis including:

1. MARKET POSITIONING
- How each competitor positions themselves
- Unique value propositions identified
- Target audience for each competitor

2. PRICING STRATEGY
- Pricing models observed
- Competitive pricing insights
- Market pricing trends

3. STRENGTHS & WEAKNESSES
- Key strengths of each competitor
- Potential weaknesses or gaps
- Market opportunities

4. STRATEGIC RECOMMENDATIONS
- Competitive advantages to leverage
- Market gaps to exploit
- Positioning recommendations

5. KEY TAKEAWAYS
- Top 3 insights for business strategy
- Immediate action items
- Long-term strategic considerations

Format the response in clear sections with bullet points where appropriate.
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
        return f"Error generating analysis: {str(e)}"

# Main App
st.markdown('<h1 class="main-header">Business Intelligence Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-Powered Competitive Analysis and Market Intelligence</p>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("Configuration")

    # OpenAI API Key
    api_key = st.text_input("OpenAI API Key", type="password",
                           help="Enter your OpenAI API key for AI analysis")

    st.markdown("---")

    st.title("Analysis Settings")

    # Business Context
    business_context = st.text_area("Your Business Context",
                                   placeholder="Describe your business, industry, target market, or specific focus area for competitive analysis...",
                                   height=100)

    # Number of competitors
    num_competitors = st.slider("Number of Competitors to Analyze", 1, 5, 3)

    st.markdown("---")

    st.title("Platform Features")
    st.markdown('<p style="color: #00ff88;">- Automated web scraping</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #00ff88;">- AI-powered analysis</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #00ff88;">- Competitive intelligence</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #00ff88;">- Strategic recommendations</p>', unsafe_allow_html=True)
    st.markdown('<p style="color: #00ff88;">- Market positioning insights</p>', unsafe_allow_html=True)

# Main Interface
if api_key and business_context:
    st.markdown("""
    <div class="analysis-card">
        <h3>Autonomous Business Intelligence Agent</h3>
        <p>1. Agent searches Google to find your competitors automatically</p>
        <p>2. Agent scrapes and analyzes competitor websites</p>
        <p>3. AI generates comprehensive competitive intelligence report</p>
    </div>
    """, unsafe_allow_html=True)

    # Mode Selection
    analysis_mode = st.radio("Analysis Mode:",
                            ["Automatic Competitor Discovery", "Manual URL Input"],
                            help="Choose whether the agent should find competitors automatically or use your provided URLs")

    competitor_urls = []

    if analysis_mode == "Manual URL Input":
        # Manual URL Input (original functionality)
        st.subheader("Manual Competitor URLs")
        for i in range(num_competitors):
            url = st.text_input(f"Competitor {i+1} URL",
                               placeholder="https://competitor-website.com",
                               key=f"comp_{i}")
            if url:
                competitor_urls.append(url)

    # Analysis Button
    if st.button("Run Competitive Analysis", type="primary"):
        # Step 0: Find competitors automatically if needed
        if analysis_mode == "Automatic Competitor Discovery":
            progress_bar = st.progress(0)
            status_container = st.container()

            status_container.markdown('<div class="agent-status"><h4>Agent Status: Searching for competitors...</h4></div>', unsafe_allow_html=True)

            competitors_found = find_competitors(business_context, num_competitors, api_key)
            competitor_urls = [comp['url'] for comp in competitors_found]

            if competitors_found:
                st.subheader("Competitors Found by Agent")
                cols = st.columns(min(len(competitors_found), 3))

                for i, comp in enumerate(competitors_found):
                    with cols[i % 3]:
                        st.markdown(f"""
                        <div class="competitor-card">
                            <h4>{comp['domain']}</h4>
                            <p><strong>Found via:</strong> {comp['found_via']}</p>
                            <p><strong>URL:</strong> {comp['url'][:50]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("Agent could not find competitors automatically. Try manual mode or refine your business description.")
                st.stop()

        if competitor_urls:
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_container = st.container()

            with status_container:
                st.markdown('<div class="agent-status"><h4>Agent Status: Initializing Analysis</h4></div>', unsafe_allow_html=True)

            # Step 1: Scrape competitor websites
            competitor_data = []
            total_steps = len(competitor_urls) + 1  # Scraping + Analysis

            for i, url in enumerate(competitor_urls):
                progress_bar.progress((i) / total_steps)
                status_container.markdown(f'<div class="agent-status"><h4>Agent Status: Scraping {url}</h4></div>', unsafe_allow_html=True)

                data = scrape_website(url)
                competitor_data.append(data)
                time.sleep(1)  # Rate limiting

            # Step 2: Display scraped data
            st.subheader("Scraped Competitor Data")
            cols = st.columns(min(len(competitor_data), 3))

            for i, data in enumerate(competitor_data):
                with cols[i % 3]:
                    if data['status'] == 'success':
                        st.markdown(f"""
                        <div class="competitor-card">
                            <h4>{data['title']}</h4>
                            <p><strong>URL:</strong> {data['url']}</p>
                            <p><strong>Description:</strong> {data['meta_description'][:100]}...</p>
                            <p><strong>Content Preview:</strong> {data['content'][:150]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="error-message">
                            <h4>Error: {data['title']}</h4>
                            <p>{data['content']}</p>
                        </div>
                        """, unsafe_allow_html=True)

            # Step 3: Generate AI Analysis
            progress_bar.progress((total_steps - 1) / total_steps)
            status_container.markdown('<div class="agent-status"><h4>Agent Status: Generating AI Analysis Report</h4></div>', unsafe_allow_html=True)

            # Only analyze successfully scraped competitors
            successful_data = [data for data in competitor_data if data['status'] == 'success']

            if successful_data:
                analysis = analyze_competitors(successful_data, business_context, api_key)

                progress_bar.progress(1.0)
                status_container.markdown('<div class="success-message"><h4>Analysis Complete</h4></div>', unsafe_allow_html=True)

                # Display Analysis Report
                st.markdown("---")
                st.subheader("AI-Generated Competitive Intelligence Report")

                st.markdown(f"""
                <div class="analysis-card">
                    <h3>Competitive Analysis Report</h3>
                    <p><strong>Business Context:</strong> {business_context}</p>
                    <p><strong>Competitors Analyzed:</strong> {len(successful_data)}</p>
                    <p><strong>Analysis Date:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                """, unsafe_allow_html=True)

                # Format and display the analysis
                st.markdown("""
                <div class="analysis-card">
                </div>
                """, unsafe_allow_html=True)

                # Display the analysis using regular markdown
                st.markdown(analysis)

                # Metrics Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-box">
                        <h3>{len(successful_data)}</h3>
                        <p>Competitors Analyzed</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    total_content = sum(len(data['content']) for data in successful_data)
                    st.markdown(f"""
                    <div class="metric-box">
                        <h3>{total_content:,}</h3>
                        <p>Characters Processed</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    pricing_found = sum(1 for data in successful_data if data['pricing_info'])
                    st.markdown(f"""
                    <div class="metric-box">
                        <h3>{pricing_found}</h3>
                        <p>Pricing Data Found</p>
                    </div>
                    """, unsafe_allow_html=True)

            else:
                st.error("No competitor websites could be successfully analyzed. Please check the URLs and try again.")

        else:
            st.warning("Please enter at least one competitor URL to analyze.")

else:
    # Welcome Screen
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="analysis-card">
            <h3>Welcome to Business Intelligence Agent</h3>
            <p>Transform competitor research with AI-powered analysis</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### How it works:")
        st.markdown("1. **Configure:** Add your OpenAI API key and describe your business context")
        st.markdown("2. **Input:** Enter competitor website URLs for analysis")
        st.markdown("3. **Analyze:** Agent scrapes websites and generates intelligence reports")
        st.markdown("4. **Insights:** Get strategic recommendations and competitive positioning")

        st.markdown("#### Perfect for:")
        st.markdown("- Market research and competitive analysis")
        st.markdown("- Product positioning and pricing strategy")
        st.markdown("- Business strategy and planning")
        st.markdown("- Investment due diligence")

        if not api_key:
            st.error("**Setup Required:** Add your OpenAI API key in the sidebar to get started")
            st.info("Get your key at: https://platform.openai.com/")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    Business Intelligence Agent | Built with Streamlit & OpenAI | Automated Competitive Analysis
</div>
""", unsafe_allow_html=True)