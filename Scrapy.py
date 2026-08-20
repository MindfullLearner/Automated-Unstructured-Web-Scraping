"""
Task 2: Automated Unstructured Web Scraping & Data Extraction Pipeline
Progree Data Science Internship

What this script does:
1. Sends requests to a public site (books.toscrape.com - a site built for scraping practice)
2. Parses raw HTML with BeautifulSoup
3. Extracts target fields: title, price, rating, availability
4. Cleans whitespace / junk characters from extracted text
5. Loops through multiple pages automatically (pagination)
6. Writes everything to a clean, structured CSV file
"""

import requests
from bs4 import BeautifulSoup
import csv
import time

# ---- CONFIG ----
BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"
TOTAL_PAGES = 5          # change this to scrape more/fewer pages
OUTPUT_FILE = "E:/books_data.csv"       
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ProgreeInternBot/1.0)"}

# Star rating words on the site map to numbers - we convert them for clean data
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def clean_text(text):
    """Remove extra whitespace, newlines, and tabs from scraped text."""
    if text is None:
        return ""
    return " ".join(text.split()).strip()


def scrape_page(page_number):
    """Scrape a single listing page and return a list of book dicts."""
    url = BASE_URL.format(page_number)
    response = requests.get(url, headers=HEADERS, timeout=10)

    if response.status_code != 200:
        print(f"Page {page_number} not reachable (status {response.status_code}), stopping.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all("article", class_="product_pod")

    page_data = []
    for book in books:
        # --- Title ---
        title = book.h3.a["title"]
        title = clean_text(title)

        # --- Price (comes as "£53.74" with a currency symbol) ---
        raw_price = book.find("p", class_="price_color").text
        price = clean_text(raw_price).replace("£", "").replace("Â", "")

        # --- Rating (given as a CSS class like "star-rating Three") ---
        rating_class = book.find("p", class_="star-rating")["class"]
        rating_word = rating_class[1] if len(rating_class) > 1 else "Zero"
        rating = RATING_MAP.get(rating_word, 0)

        # --- Availability ---
        availability = clean_text(book.find("p", class_="instock availability").text)

        page_data.append({
            "title": title,
            "price_gbp": price,
            "rating_out_of_5": rating,
            "availability": availability
        })

    return page_data


def run_pipeline():
    all_data = []

    for page in range(1, TOTAL_PAGES + 1):
        print(f"Scraping page {page}...")
        page_data = scrape_page(page)
        if not page_data:
            break
        all_data.extend(page_data)
        time.sleep(1)  # polite delay so we don't hammer the server

    # Write to CSV
    if all_data:
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=all_data[0].keys())
            writer.writeheader()
            writer.writerows(all_data)
        print(f"\nDone! {len(all_data)} records saved to {OUTPUT_FILE}")
    else:
        print("No data collected.")


if __name__ == "__main__":
    run_pipeline()