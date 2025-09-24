# Business Intelligence Agent

AI-powered competitive analysis and market intelligence platform built with Streamlit and OpenAI.

## Features

- **Automated Web Scraping**: Extracts competitor website content and key business information
- **AI Analysis**: Uses GPT to generate comprehensive competitive intelligence reports
- **Dark Theme Interface**: Professional dark UI with light text for extended use
- **Market Positioning**: Identifies competitor strengths, weaknesses, and opportunities
- **Pricing Intelligence**: Automatically extracts and analyzes competitor pricing strategies
- **Strategic Recommendations**: AI-generated actionable insights for business strategy

## How It Works

1. **Configure**: Add OpenAI API key and describe your business context
2. **Input**: Enter competitor website URLs (1-5 competitors)
3. **Scrape**: Agent automatically extracts content from competitor websites
4. **Analyze**: AI generates comprehensive competitive intelligence report
5. **Insights**: Get strategic recommendations and market positioning advice

## Quick Start

### Local Development

```bash
# Clone and navigate to directory
cd streamlit-business-agent

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Setup

1. Get OpenAI API key from https://platform.openai.com/
2. Enter API key in the sidebar
3. Describe your business context
4. Add competitor URLs
5. Run analysis

## Use Cases

- **Market Research**: Comprehensive competitor landscape analysis
- **Product Positioning**: Understand competitor value propositions
- **Pricing Strategy**: Analyze competitor pricing models and positioning
- **Business Planning**: Strategic insights for market entry or expansion
- **Due Diligence**: Investment research and competitor assessment

## Analysis Includes

- **Market Positioning**: How competitors position themselves and target audiences
- **Pricing Strategy**: Pricing models, competitive pricing insights, market trends
- **Strengths & Weaknesses**: Competitor advantages and market gaps
- **Strategic Recommendations**: Actionable insights for competitive advantage
- **Key Takeaways**: Top strategic insights and immediate action items

## Technology Stack

- **Frontend**: Streamlit with custom dark theme CSS
- **AI**: OpenAI GPT-3.5-turbo for competitive analysis
- **Web Scraping**: Requests + BeautifulSoup for content extraction
- **Processing**: Python for data processing and analysis

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection for web scraping

## Security

- API keys are not stored or logged
- Web scraping follows robots.txt guidelines
- Rate limiting implemented to respect website resources

## Perfect For

- Business analysts and strategists
- Product managers researching competition
- Entrepreneurs entering new markets
- Consultants conducting market research
- Investment professionals performing due diligence

---

Built for professional competitive intelligence and market analysis.