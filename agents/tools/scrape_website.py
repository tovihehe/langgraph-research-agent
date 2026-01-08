import aiohttp
import chardet
import asyncio  
from interfaces.llm_interface import LLMInterface
from utils.prompt_manager import PromptManager
from langgraph.prebuilt import InjectedState
from typing_extensions import Annotated
from agents.research_agent.state import State
from pydantic import BaseModel, Field
from typing import Any, cast
from bs4 import BeautifulSoup


class WebInfo(BaseModel):
    """
    Extracted information from a URL.
    """
    url: str = Field(
        description="The URL from which the information was extracted."
    )
    notes: str = Field(
        description="The extracted information from the URL relevant to the researched topic."
    )


async def extract_text(url):
    """Extract text from a URL, handling timeouts, encoding issues, and content type filtering."""
    print(f"Extracting text from {url}")

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),  # Ignore SSL verification
        timeout=aiohttp.ClientTimeout(total=30)  # 30s timeout
    ) as session:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
            }
            async with session.get(url, headers=headers) as response:
                content_type = response.headers.get('Content-Type', '').lower()

                # Only process HTML responses
                if 'text/html' not in content_type:
                    print(f"Skipping non-HTML content from {url} (Content-Type: {content_type})")
                    return "Skipped non-HTML content"

                raw_content = await response.read()
                detected_encoding = chardet.detect(raw_content)['encoding'] or 'utf-8'

                return raw_content.decode(detected_encoding, errors='ignore')

        except asyncio.TimeoutError:
            print(f"Timeout while fetching {url}")
            return "Failed to fetch content"

        except aiohttp.ClientError as e:
            print(f"Network error while fetching {url}: {e}")
            return "Failed to fetch content"

        except asyncio.CancelledError:
            print(f"Request to {url} was cancelled.")
            return "Request cancelled"
        
        except Exception as e:
            print(f"Error while fetching {url}: {e}")
            return "Failed to fetch content"


async def extract_notes(
    url: str,
    state: Annotated[State, InjectedState],
    config: dict,
) -> str:
    """Scrape and summarize content from a website."""
    print(f"Extracting notes from {url}")

    # Extract text from the URL
    content = await extract_text(url)
    if content in ["Failed to fetch content", "Skipped non-HTML content", "Request cancelled"]:
        return content  # Skip processing if the fetch failed or was non-HTML
    
    # Parse the HTML content
    soup = BeautifulSoup(content, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()  # Remove script and style tags
    
    # Get the text content
    text_content = soup.get_text()
    text_content = " ".join(text_content.split())  # Normalize whitespace

    # Limit the content to 20k characters
    content = text_content[:20000]

    # Get the extract_info prompt 
    extract_info_prompt = PromptManager(config).get_prompt("extract_info")
    prompt = extract_info_prompt.format(
        topic=state.topic,
        url=url,
        content=content,  # Limit content to 20k characters
    )

    llm = LLMInterface(config).get_llm()
    bound_model = llm.with_structured_output(WebInfo)
    response = cast(WebInfo, await bound_model.ainvoke(prompt))
    notes_extracted = response.model_dump()
    return str(notes_extracted)
