import openai
import json
import re
from typing import Dict, List, Optional


def extract_article_links_with_openai(markdown_content: str, openai_api_key: str, model: str = "gpt-4o-mini-2024-07-18") -> List[str]:
    """
    Extract article links from DOJ markdown content using OpenAI API.
    
    Args:
        markdown_content (str): The markdown content from DOJ press room
        openai_api_key (str): OpenAI API key
        model (str): OpenAI model to use (default: gpt-4)
    
    Returns:
        List[str]: List of extracted article URLs
    """
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=openai_api_key)
    
    # Create the prompt for extracting article links
    prompt = f"""
    Analyze the following markdown content from the DOJ press room page and extract all article URLs.

    The URLs are typically in the format:
    https://www.justice.gov/psc/press-room/... 

    Return ONLY a JSON array of URLs without any additional text or explanation.

    Markdown Content:
    {markdown_content}
    """
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.0
    )
    raw = response.choices[0].message.content.strip()
    
    match = re.search(r"```json\s*(\[[\s\S]*?\])\s*```", raw)
    text = match.group(1) if match else raw

    try:
        urls = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from model: {e}")

    if not isinstance(urls, list):
        raise ValueError("Model did not return a JSON array")
    return urls