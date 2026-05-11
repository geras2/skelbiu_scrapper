import re
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import requests
scraper = cloudscraper.create_scraper()
from datetime import datetime

def parse_number(s):

    if s is None:
        return None
    print(s)
    s = s.upper().strip()

    if "K" in s:
        return int(float(s.replace("K", "")) * 1000)

    return int(re.sub(r"[^\d]", "", s))


def extract_ad_info(link):

    try:

        r = scraper.get(link, timeout=30)

        print(r.status_code)

        soup = BeautifulSoup(r.text, "html.parser")

        # -------------------------
        # ID
        # -------------------------

        text = soup.get_text(" ", strip=True)

        id_match = re.search(r"ID:\s*(\d+)", text)

        ad_id = id_match.group(1) if id_match else None

        # -------------------------
        # Views
        # -------------------------

        views_el = soup.select_one(
            "div.block.showed span"
        )

        views = None

        if views_el:
            views = parse_number(
                views_el.get_text(strip=True)
            )

        # -------------------------
        # Bookmarks
        # -------------------------

        bookmarks_match = re.search(
            r"Įsimintas\s+(\d+)",
            text
        )

        bookmarks = (
            int(bookmarks_match.group(1))
            if bookmarks_match else None
        )

        return pd.Series({
            "ad_id": ad_id,
            "views": views,
            "bookmarks": bookmarks
        })

    except Exception as e:

        print(e)

        return pd.Series({
            "ad_id": None,
            "views": None,
            "bookmarks": None
        })


def extract_ads(link):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    r = requests.get(link, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    items = []

    # Each listing container
    ads = soup.select("a[href*='/skelbimai/']")

    seen = set()

    for ad in ads:
        href = ad.get("href")

        # avoid duplicates / junk
        if not href or href in seen:
            continue

        title_el = ad.select_one("div.title")
        price_el = ad.select_one("div.price")
        meta_el = ad.select_one("div.second-dataline")

        if not title_el:
            continue

        seen.add(href)

        items.append({
            "title": title_el.get_text(strip=True),
            "price": price_el.get_text(" ", strip=True) if price_el else None,
            "meta": meta_el.get_text(" ", strip=True) if meta_el else None,
            "link": href if href.startswith("http") else f"https://www.skelbiu.lt{href}",
            "scraped_at": datetime.now()
        })
        df = pd.DataFrame(items)
    return df