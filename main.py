import os, json, asyncio, logging
import dotenv
from utils import get_date_range_from_args
from scrapPage import extract_doj_markdown, extract_doj_markdown_from_url
from LLM.pagination import process_doj_pagination
from LLM.extractLinks import extract_article_links_with_openai
from LLM.extractArticleText import extract_press_release_body

# ─── Setup ──────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY is not set in the environment variables.")
    raise SystemExit(1)

DATE_FROM, DATE_TO = get_date_range_from_args()
BASE_URL = (
    f"https://www.justice.gov/psc/press-room?search_api_fulltext=&start_date={DATE_FROM}"
    f"&end_date={DATE_TO}&sort_by=field_date"
)

# ─── Helpers ───────────────────────────────────────────────────────────────────
def normalize_pages(pages_obj):
    """
    Normalize whatever process_doj_pagination returns into List[str] URLs.
    Handles:
      - {"pages": [...]}
      - {"page_links": [...]}
      - {"0": "url", "1": "url", ...}
      - list[str] or list[dict]
    """
    if not pages_obj:
        return []

    # Case 1: dict wrapper
    if isinstance(pages_obj, dict):
        # Common wrappers
        for key in ("pages", "page_links", "links"):
            if key in pages_obj and isinstance(pages_obj[key], (list, tuple, set)):
                pages_obj = list(pages_obj[key])
                break
        else:
            # Not a known wrapper. Use values.
            vals = list(pages_obj.values())
            # If the single value is itself a list/tuple/set, unwrap it
            if len(vals) == 1 and isinstance(vals[0], (list, tuple, set)):
                pages_obj = list(vals[0])
            else:
                pages_obj = vals  # e.g., {"0":"url","1":"url"} -> ["url","url"]

    # Now expect a list/tuple/set of either str or dict
    if isinstance(pages_obj, (set, tuple)):
        pages_obj = list(pages_obj)

    if not isinstance(pages_obj, list):
        return []

    if not pages_obj:
        return []

    # If list of dicts → extract url-like fields
    if isinstance(pages_obj[0], dict):
        urls = []
        for d in pages_obj:
            if not isinstance(d, dict):
                continue
            url = d.get("url") or d.get("href") or d.get("link")
            if url:
                urls.append(url)
        return urls

    # If list of strings → already URLs
    if isinstance(pages_obj[0], str):
        return pages_obj

    return []

async def fetch_article_text(url, sem):
    async with sem:
        md = await extract_doj_markdown_from_url(url)
        if not md:
            return url, "Markdown fetch failed"
        try:
            text = extract_press_release_body(md, OPENAI_API_KEY)
            return url, text or "Extraction produced empty text"
        except Exception as e:
            logging.error(f"Article body extraction failed for {url}: {e}")
            return url, "Extraction failed"

# ─── Main ──────────────────────────────────────────────────────────────────────
async def main():
    print(f"Fetching press releases from {DATE_FROM} to {DATE_TO}...")
    print("Base URL:", BASE_URL)

    first_markdown = await extract_doj_markdown(DATE_FROM, DATE_TO)
    if not first_markdown:
        logging.error("Failed to fetch initial listing page markdown.")
        return

    try:
        pages_raw = process_doj_pagination(first_markdown, OPENAI_API_KEY)
    except Exception as e:
        logging.warning(f"Pagination parsing failed, treating as no pagination. Err={e}")
        pages_raw = []

    logging.debug("pages_raw type=%s sample=%s",
              type(pages_raw).__name__,
              (list(pages_raw.items())[:2] if isinstance(pages_raw, dict)
               else pages_raw[:2] if isinstance(pages_raw, list)
               else pages_raw))


    page_links = normalize_pages(pages_raw)
    no_pagination = (not page_links) or (len(page_links) <= 1)

    all_article_urls = []

    if no_pagination:
        logging.info("No pagination detected. Extracting article links from the first page via LLM.")
        try:
            urls = extract_article_links_with_openai(first_markdown, OPENAI_API_KEY) or []
            all_article_urls.extend(urls)
        except Exception as e:
            logging.error(f"LLM link extraction failed on first page: {e}")
    else:
        logging.info(f"Pagination detected with {len(page_links)} pages. Extracting per page.")
        for page_url in page_links:  # <-- already strings now
            if not page_url:
                continue
            page_md = await extract_doj_markdown_from_url(page_url)
            if not page_md:
                logging.warning(f"Empty markdown for {page_url}")
                continue
            try:
                urls = extract_article_links_with_openai(page_md, OPENAI_API_KEY) or []
                all_article_urls.extend(urls)
            except Exception as e:
                logging.error(f"LLM link extraction failed on {page_url}: {e}")

    # De-dupe and filter
    all_article_urls = sorted(set(u for u in all_article_urls if isinstance(u, str) and u.startswith("http")))
    logging.info(f"Found {len(all_article_urls)} unique article URLs.")

    # Fetch articles concurrently with a polite cap
    sem = asyncio.Semaphore(5)  # tune concurrency as needed
    tasks = [fetch_article_text(url, sem) for url in all_article_urls]
    results = await asyncio.gather(*tasks)

    article_text_store = {url: text for url, text in results}

    output_file = "extracted_article_text.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(article_text_store, f, ensure_ascii=False, indent=2)

    print(f"Article text extracted and saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
