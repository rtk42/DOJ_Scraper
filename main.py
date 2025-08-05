
from scrapPage import extract_doj_markdown, extract_doj_markdown_from_url
from LLM.pagination import process_doj_pagination
from LLM.extractLinks import extract_article_links_with_openai
from LLM.extractArticleText import extract_press_release_body
from utils import get_date_range_from_args


import logging
import os
import dotenv
import json
import asyncio
import time

dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY is not set in the environment variables.")
    exit(1)




# Get start and end dates
DATE_FROM, DATE_TO = get_date_range_from_args()

BASE_URL = (
    f"https://www.justice.gov/psc/press-room?search_api_fulltext=&start_date={DATE_FROM}&end_date={DATE_TO}&sort_by=field_date"
)

print(f"Fetching press releases from {DATE_FROM} to {DATE_TO}...")
print("Base URL:", BASE_URL)

# output = asyncio.run(linkScraper(FIRECRAWL_API_KEY, BASE_URL, DATE_FROM, DATE_TO))
markdown = asyncio.run(extract_doj_markdown(DATE_FROM, DATE_TO))
print("Markdown content fetched successfully.")
# print("Markdown length:", len(markdown))

# print("#### Markdown Content ####")
# print(markdown)

pagination_info = process_doj_pagination(markdown, openai_api_key=OPENAI_API_KEY, use_fallback=False)
print("Pagination Information:")
print(json.dumps(pagination_info, indent=2))

article_store = {}

for page_links in pagination_info.get("page_links", []):
    print(f"Page {page_links['page_number']}: {page_links['url']}")
    getpage_markdown = asyncio.run(extract_doj_markdown_from_url(page_links['url']))

    article_links = extract_article_links_with_openai(getpage_markdown, openai_api_key=os.getenv("OPENAI_API_KEY"))

    article_store[page_links['page_number']] = article_links


for page_number, links in article_store.items():
    print(f"Page {page_number} has {len(links)} article links.")

print("Extracted article links:")

article_text_store = {}

for page_number, links in article_store.items():
    print(f"Page {page_number}:")
    article_text_store[page_number] = {}
    for link in links:
        print(f"Fetching markdown content for link: {link}")
        article_text = ""
        
        # 1) Fetch markdown
        getpage_markdown = asyncio.run(extract_doj_markdown_from_url(link))
        if not getpage_markdown:
            print(f"  ✗ Failed to fetch markdown for {link}")
            article_text = "Markdown fetch failed"
        else:
            # 2) Try to extract body
            try:
                article_text = extract_press_release_body(
                    getpage_markdown,
                    api_key=os.getenv("OPENAI_API_KEY")
                ) or ""
                print(f"  ✓ Extracted text for {link}")
            except Exception as e:
                print(f"  ✗ Extraction failed for {link}: {e}")
                article_text = "Extraction failed"
        
        # 3) Record it (empty if anything went wrong)
        article_text_store[page_number][link] = article_text
        
        time.sleep(3)





# store all
output_file = "extracted_article_text.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(article_text_store, f, ensure_ascii=False, indent=2)

print(f"Article text extracted and saved to {output_file}")

    