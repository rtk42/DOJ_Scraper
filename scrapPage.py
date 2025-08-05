import asyncio
from crawl4ai import *
from datetime import datetime, timedelta
import os
from typing import Optional

async def extract_doj_markdown(start_date: str, end_date: str, search_term: str = "") -> str:
    """
    Extract markdown from DOJ press room for a specific date range.
    
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format  
        search_term (str): Optional search term to filter results
    
    Returns:
        str: Extracted markdown content
    """
    
    # Validate date format
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Dates must be in YYYY-MM-DD format (e.g., '2025-07-31')")
    
    # Construct the URL with date parameters
    base_url = "https://www.justice.gov/psc/press-room"
    url = f"{base_url}?search_api_fulltext={search_term}&start_date={start_date}&end_date={end_date}&sort_by=field_date"
    
    print(f"Crawling DOJ press room from {start_date} to {end_date}")
    if search_term:
        print(f"Search term: '{search_term}'")
    print(f"URL: {url}\n")
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        
        if result.success:
            print("✅ Crawling successful!")
            print(f"Content length: {len(result.markdown)} characters")
            return result.markdown
        else:
            print("❌ Crawling failed!")
            print(f"Error: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")
            return ""

async def extract_doj_markdown_from_url(url: str) -> str:
    """
    Extract markdown from a specific DOJ press room URL.
    
    Args:
        url (str): The URL to extract markdown from
    
    Returns:
        str: Extracted markdown content
    """
    
    print(f"Crawling DOJ press room from URL: {url}\n")
    
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        
        if result.success:
            print("✅ Crawling successful!")
            print(f"Content length: {len(result.markdown)} characters")
            return result.markdown
        else:
            print("❌ Crawling failed!")
            print(f"Error: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")
            return ""

