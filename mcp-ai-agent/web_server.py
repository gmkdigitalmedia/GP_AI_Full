"""
Web Search MCP Server
Provides web search and scraping capabilities
"""

import requests
from bs4 import BeautifulSoup
import wikipedia
from mcp_base import MCPServer

class WebServer(MCPServer):
    def __init__(self):
        super().__init__("web", "Web search and content retrieval server")

    def _register_tools(self):
        """Register web tools"""

        # Wikipedia search tool
        self.add_tool(
            "wikipedia_search",
            "Search Wikipedia for information",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for Wikipedia"},
                    "sentences": {"type": "integer", "description": "Number of sentences to return (default: 3)"}
                },
                "required": ["query"]
            },
            self._wikipedia_search
        )

        # Wikipedia summary tool
        self.add_tool(
            "wikipedia_summary",
            "Get detailed Wikipedia summary",
            {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Wikipedia article title"},
                    "sentences": {"type": "integer", "description": "Number of sentences (default: 5)"}
                },
                "required": ["title"]
            },
            self._wikipedia_summary
        )

        # URL content fetch tool
        self.add_tool(
            "fetch_url",
            "Fetch and extract text content from a URL",
            {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch content from"},
                    "max_length": {"type": "integer", "description": "Max characters to return (default: 2000)"}
                },
                "required": ["url"]
            },
            self._fetch_url
        )

        # News headlines tool (using a simple RSS-like approach)
        self.add_tool(
            "get_news_headlines",
            "Get current news headlines from Wikipedia current events",
            {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of headlines to return (default: 5)"}
                },
                "required": []
            },
            self._get_news_headlines
        )

    def _wikipedia_search(self, query: str, sentences: int = 3) -> str:
        """Search Wikipedia and return summary"""
        try:
            # Search for pages
            search_results = wikipedia.search(query, results=5)

            if not search_results:
                return f"No Wikipedia results found for '{query}'"

            results = []
            for title in search_results[:3]:  # Top 3 results
                try:
                    summary = wikipedia.summary(title, sentences=sentences)
                    results.append(f"**{title}**\n{summary}")
                except wikipedia.exceptions.DisambiguationError as e:
                    # Try the first option from disambiguation
                    try:
                        summary = wikipedia.summary(e.options[0], sentences=sentences)
                        results.append(f"**{e.options[0]}**\n{summary}")
                    except:
                        continue
                except:
                    continue

            if not results:
                return f"Could not retrieve summaries for '{query}'"

            return f"Wikipedia search results for '{query}':\n\n" + "\n\n".join(results)

        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"

    def _wikipedia_summary(self, title: str, sentences: int = 5) -> str:
        """Get detailed Wikipedia summary for a specific title"""
        try:
            summary = wikipedia.summary(title, sentences=sentences)
            page = wikipedia.page(title)

            return f"**{page.title}**\n\n{summary}\n\nURL: {page.url}"

        except wikipedia.exceptions.DisambiguationError as e:
            options = e.options[:5]
            return f"Multiple pages found for '{title}'. Options: {', '.join(options)}"
        except wikipedia.exceptions.PageError:
            return f"No Wikipedia page found for '{title}'"
        except Exception as e:
            return f"Error getting Wikipedia summary: {str(e)}"

    def _fetch_url(self, url: str, max_length: int = 2000) -> str:
        """Fetch content from a URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Limit length
            if len(text) > max_length:
                text = text[:max_length] + "..."

            return f"Content from {url}:\n\n{text}"

        except requests.exceptions.RequestException as e:
            return f"Error fetching URL: {str(e)}"
        except Exception as e:
            return f"Error processing URL content: {str(e)}"

    def _get_news_headlines(self, limit: int = 5) -> str:
        """Get current events from Wikipedia"""
        try:
            # Get current events page
            page = wikipedia.page("Portal:Current events")
            content = page.content

            # Extract first few paragraphs as "headlines"
            lines = content.split('\n')
            headlines = []

            for line in lines:
                line = line.strip()
                if line and not line.startswith('=') and len(line) > 20:
                    headlines.append(line)
                    if len(headlines) >= limit:
                        break

            if not headlines:
                return "Could not retrieve current news headlines"

            return "Current events from Wikipedia:\n\n" + "\n\n".join(f"• {headline}" for headline in headlines)

        except Exception as e:
            return f"Error getting news headlines: {str(e)}"