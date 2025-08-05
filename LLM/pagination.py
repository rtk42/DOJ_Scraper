import openai
import json
import re
from typing import Dict, List, Optional

def extract_pagination_with_openai(markdown_content: str, openai_api_key: str, model: str = "gpt-4o-mini-2024-07-18") -> Dict:
    """
    Extract pagination information from DOJ markdown content using OpenAI API.
    
    Args:
        markdown_content (str): The markdown content from DOJ press room
        openai_api_key (str): OpenAI API key
        model (str): OpenAI model to use (default: gpt-4)
    
    Returns:
        Dict: Structured JSON with pagination information
    """
    
    # Initialize OpenAI client
    client = openai.OpenAI(api_key=openai_api_key)
    
    # Create the prompt for extracting pagination
    prompt = f"""
    Analyze the following markdown content from the DOJ press room page and extract pagination information.

    Look for pagination links that typically appear at the bottom of the page in this format:
    * [1](https://www.justice.gov/psc/press-room?...&page=0)
    * [2](https://www.justice.gov/psc/press-room?...&page=1)
    * [3](https://www.justice.gov/psc/press-room?...&page=2)
    * [Next](https://www.justice.gov/psc/press-room?...&page=1)
    * [Last](https://www.justice.gov/psc/press-room?...&page=2)

    Extract the following information and return ONLY a valid JSON object:

    {{
        "total_pages": <number_of_pages>,
        "current_page": <current_page_number>,
        "page_links": [
            {{
                "page_number": <page_number>,
                "url": "<full_url>",
                "is_current": <true_or_false>
            }}
        ],
        "navigation_links": {{
            "next": "<next_page_url_if_exists>",
            "last": "<last_page_url_if_exists>",
            "previous": "<previous_page_url_if_exists>",
            "first": "<first_page_url_if_exists>"
        }},
        "has_pagination": <true_or_false>
    }}

    Important instructions:
    1. If no pagination is found, set "has_pagination" to false and "total_pages" to 1
    2. Page numbers usually start from 1 in display but URLs might use 0-based indexing (page=0 for page 1)
    3. Extract the complete URLs for each page link
    4. Identify which page is currently active/selected
    5. Look for "Next", "Last", "Previous", "First" navigation links
    6. Return ONLY valid JSON, no additional text or explanation

    Markdown content to analyze:

    {markdown_content}
    """

    try:
        # Make API call to OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a data extraction specialist. Extract pagination information from web content and return only valid JSON. Do not include any explanatory text."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=1500
        )
        
        # Extract the response content
        response_text = response.choices[0].message.content.strip()
        
        # Clean up the response (remove potential markdown formatting)
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON response
        pagination_data = json.loads(response_text)
        
        return pagination_data
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response_text}")
        return {
            "error": "Failed to parse JSON response",
            "raw_response": response_text,
            "has_pagination": False,
            "total_pages": 1
        }
    
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {
            "error": str(e),
            "has_pagination": False,
            "total_pages": 1
        }

def extract_pagination_with_regex_fallback(markdown_content: str) -> Dict:
    """
    Fallback method to extract pagination using regex if OpenAI fails.
    
    Args:
        markdown_content (str): The markdown content from DOJ press room
    
    Returns:
        Dict: Basic pagination information
    """
    
    # Pattern to match pagination links
    page_pattern = r'\* \[(\d+)\]\((https://www\.justice\.gov/psc/press-room[^)]+page=(\d+))\)'
    nav_pattern = r'\* \[ (Next|Last|Previous|First) \]\((https://www\.justice\.gov/psc/press-room[^)]+)\)'
    
    # Find all page number links
    page_matches = re.findall(page_pattern, markdown_content)
    nav_matches = re.findall(nav_pattern, markdown_content)
    
    page_links = []
    navigation_links = {}
    
    # Process page number links
    for display_num, url, page_param in page_matches:
        page_links.append({
            "page_number": int(display_num),
            "url": url,
            "is_current": False  # Would need more logic to determine current page
        })
    
    # Process navigation links
    for nav_type, url in nav_matches:
        navigation_links[nav_type.lower()] = url
    
    total_pages = len(page_links) if page_links else 1
    has_pagination = len(page_links) > 1
    
    return {
        "total_pages": total_pages,
        "current_page": 1,  # Default, would need more logic to determine
        "page_links": page_links,
        "navigation_links": navigation_links,
        "has_pagination": has_pagination,
        "extraction_method": "regex_fallback"
    }

def process_doj_pagination(markdown_content: str, openai_api_key: Optional[str] = None, 
                          use_fallback: bool = True) -> Dict:
    """
    Main function to extract pagination information with OpenAI and fallback options.
    
    Args:
        markdown_content (str): The markdown content from DOJ press room
        openai_api_key (str, optional): OpenAI API key
        use_fallback (bool): Whether to use regex fallback if OpenAI fails
    
    Returns:
        Dict: Pagination information
    """
    
    if openai_api_key:
        print("Extracting pagination using OpenAI...")
        result = extract_pagination_with_openai(markdown_content, openai_api_key)
        
        # Check if OpenAI extraction was successful
        if "error" not in result:
            result["extraction_method"] = "openai"
            return result
        else:
            print("OpenAI extraction failed, using fallback method...")
    
    if use_fallback:
        print("Using regex fallback method...")
        return extract_pagination_with_regex_fallback(markdown_content)
    else:
        return {
            "error": "No valid extraction method available",
            "has_pagination": False,
            "total_pages": 1
        }
