from typing import Any, Optional, cast
from langchain_community.tools.tavily_search import TavilySearchResults


async def search(
    query: str, config: dict
) -> Optional[list[dict[str, Any]]]:
    """Query a search engine.

    This function queries the web to fetch comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events. Provide as much context in the query as needed to ensure high recall.
    """
    print(f"Searching for {query}")


    # Wrap the Tavily search tool
    wrapped = TavilySearchResults(
        search_depth="basic", #advanced
        topic="news", #general
        include_images=False,
        include_image_description=False,
        include_answer=False,
        include_raw_content=False,
        # time_range="year",
        max_results=config.max_search_results
        # include_domains=["wikipedia.org"]
        )
    
    # Perform the search
    result = await wrapped.ainvoke({"query": query})

    # Remove URLs that are PDFs from the search results
    for item in result:
        if item["url"].lower().endswith('.pdf') or '/pdf/' in item["url"].lower():
            result.remove(item)
        else:
            continue

    return cast(list[dict[str, Any]], result)

