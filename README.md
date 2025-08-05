
# 🏛️ DOJ_Scraper

**DOJ_Scraper** is a Python-based scraper designed to collect press releases (or similar documents) from the U.S. Department of Justice website. It automates:

- Fetching listings of DOJ materials
- Parsing dates, titles, links, and metadata
- Saving structured output (e.g. JSON or CSV)

---

## ⚠️ Pagination Requirement

The scraper **requires pagination** on the search results page to work properly. If your date filter returns **only a single page**, the script won't proceed.  
**Tip:** Use a date range with enough volume (e.g. several weeks or months) so that results span **multiple pages**. This ensures full crawling. This limitation will be fixed in a future update.

---

## 🚀 Getting Started

### Requirements

- Python 3.9 or higher  
- Recommended modules in `requirements.txt`

Install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## ⚙️ Running the Scraper

Assuming you have a main script named `main.py` or `scrapPage.py`, follow these steps:

```bash
cd DOJ_Scraper   # ensure you're in project root
source .venv/bin/activate

# Run the scraper with a date filter
python main.py --start-date YYYY-MM-DD --end-date YYYY-MM-DD
```

Example:
```bash
python main.py --start-date 2025-01-01 --end-date 2025-06-30
```

If fewer results appear and **pagination isn't triggered**, adjust the date range broader until multiple pages are encountered.

---

## 🗂️ Output

- Scraped results are saved into:
  - `data/` folder (if used; outputs might include `.csv`, `.json`, or logs)
- Filenames denote the date range or batch number.

---

## ✅ Tips & Caveats

- **Always choose date ranges that result in multiple pages**, especially during busy periods.
- **Remove or rotate your `.env` or credentials**, particularly when publishing your repo.
- This is built as a straightforward scraper—remember to respect terms of service and rate-limit requests.

---

## 🔧 Planned Enhancements

- Automatic pagination detection to avoid missing data  
- Better handling of date filters (e.g. iterative splitting if only one page)  
- Support for more output formats (database, Excel, etc.)

---

## 📄 License & Contributing

_This project is currently not licensed. Add a `LICENSE` file if needed._

Contributions are welcome! If you’d like to suggest features (like fixing pagination handling), feel free to open an issue or pull request.
