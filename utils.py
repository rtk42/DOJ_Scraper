# utils.py

import argparse
from datetime import datetime

DEFAULT_DATE_FROM = "2025-07-31"
DEFAULT_DATE_TO = "2025-08-01"

def get_date_range_from_args():
    parser = argparse.ArgumentParser(description="DOJ Press Release Scraper")
    parser.add_argument(
        "--start-date",
        default=DEFAULT_DATE_FROM,
        help=f"Start date in YYYY-MM-DD format (default: {DEFAULT_DATE_FROM})"
    )
    parser.add_argument(
        "--end-date",
        default=DEFAULT_DATE_TO,
        help=f"End date in YYYY-MM-DD format (default: {DEFAULT_DATE_TO})"
    )
    args = parser.parse_args()

    # Validate format
    try:
        datetime.strptime(args.start_date, "%Y-%m-%d")
        datetime.strptime(args.end_date, "%Y-%m-%d")
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format.")
        exit(1)

    return args.start_date, args.end_date
