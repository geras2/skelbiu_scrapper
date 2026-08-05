# ---------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------

import re
import time
from datetime import datetime
import random

# ---------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------

import pandas as pd
import requests

from bs4 import BeautifulSoup

from core.session import get_scraper

# ---------------------------------------------------------
# Helper function:
# Convert Skelbiu numbers into integers
#
# Examples:
# "1K"  -> 1000
# "12"  -> 12
# "2.5K" -> 2500
# ---------------------------------------------------------

def parse_number(s):

    if s is None:
        return None

    print(s)

    s = s.upper().strip()

    # Convert K notation
    if "K" in s:
        return int(float(s.replace("K", "")) * 1000)

    # Remove non-digit characters
    return int(re.sub(r"[^\d]", "", s))


# ---------------------------------------------------------
# Extract detailed information from a single ad page
#
# Input:
#   link -> direct Skelbiu ad URL
#
# Returns:
#   pandas Series with:
#       ad_id
#       views
#       bookmarks
# ---------------------------------------------------------


# ---------------------------------------------------------
# Download complete HTML
# ---------------------------------------------------------
def extract_html(link, retries=5):
    scraper = get_scraper()
    for attempt in range(retries):

        try:
            r = scraper.get(link, timeout=30)

            r.raise_for_status()

            soup = BeautifulSoup(r.text, "html.parser")

            if soup.select_one("div.block.id"):
                return r

        except Exception as e:
            print(e)

        time.sleep(random.uniform(2, 5))

    raise RuntimeError(f"Failed to load {link}")

def extract_ad_info(link):
    """
    Extract information from a Skelbiu ad page.

    Returns:
        pd.Series:
            ad_id
            views
            bookmarks
            status
    """

    try:
        # r = scraper.get(link, timeout=30)
        r = extract_html(link)


        soup = BeautifulSoup(r.text, "html.parser")

        # -------------------------------
        # Ad ID
        # -------------------------------
        ad_id = None

        id_el = soup.select_one("div.block.id")
        if id_el:
            match = re.search(r"\d+", id_el.get_text())
            if match:
                ad_id = match.group()

        # -------------------------------
        # Views
        # -------------------------------
        views = None

        views_el = soup.select_one("div.block.showed span")
        if views_el:
            views = parse_number(
                views_el.get_text(strip=True)
            )

        # -------------------------------
        # Bookmarks
        # -------------------------------
        bookmarks = None

        bookmarks_el = soup.select_one("div.block.bookmarks span")
        if bookmarks_el:
            bookmarks = parse_number(
                bookmarks_el.get_text(strip=True)
            )

        # -------------------------------
        # Status
        # -------------------------------
        status = None

        status_el = soup.select_one("div.info-description")
        if status_el:
            status = status_el.get_text(
                " ",
                strip=True
            )

        return pd.Series({
            "ad_id": ad_id,
            "views": views,
            "bookmarks": bookmarks,
            "status": status
        })

    except Exception as e:
        print(f"{link} -> {e}")

        return pd.Series({
            "ad_id": None,
            "views": None,
            "bookmarks": None,
            "status": None
        })

# ---------------------------------------------------------
# Extract ads from Skelbiu search results page
#
# Input:
#   link -> Skelbiu search URL
#
# Returns:
#   DataFrame with:
#       title
#       price
#       meta
#       link
#       scraped_at
# ---------------------------------------------------------

def extract_ad_id(link):
    match = re.search(r'(\d+)(?=\.html$)', link)
    # return match.group(1) if match else None
    return int(match.group(1)) if match else None

# print(extract_ad_id("https://www.skelbiu.lt/skelbimai/grazus-vaikiskas-dvyratukas-86176334.html"))
# # 86176334

    
def extract_ads(link):

    # ---------------------------------------------
    # Browser-like headers
    # ---------------------------------------------

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    # ---------------------------------------------
    # Request page
    # ---------------------------------------------

    r = requests.get(
        link,
        headers=headers
    )

    r.raise_for_status()

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )

    # ---------------------------------------------
    # Collect ads
    # ---------------------------------------------

    items = []

    ads = soup.select(
        "a[href*='/skelbimai/']"
    )

    seen = set()

    # ---------------------------------------------
    # Process ads
    # ---------------------------------------------

    for ad in ads:

        href = ad.get("href")

        if not href:
            continue

        full_link = (

            href

            if href.startswith("http")

            else f"https://www.skelbiu.lt{href}"

        )

        # Skip duplicates
        if full_link in seen:
            continue

        seen.add(full_link)

        title_el = ad.select_one(
            "div.title"
        )

        price_el = ad.select_one(
            "div.price"
        )

        meta_el = ad.select_one(
            "div.second-dataline"
        )

        if not title_el:
            continue

        # -----------------------------------------
        # Extract ad ID from URL
        # -----------------------------------------

        match = re.search(
            r"-(\d+)\.html",
            full_link
        )

        ad_id = (

            str(match.group(1))

            if match

            else None

        )

        # -----------------------------------------
        # Store result
        # -----------------------------------------

        items.append({

            "ad_id": ad_id,

            "title": title_el.get_text(
                strip=True
            ),

            "price": (
                price_el.get_text(
                    " ",
                    strip=True
                )
                if price_el
                else None
            ),

            "meta": (
                meta_el.get_text(
                    " ",
                    strip=True
                )
                if meta_el
                else None
            ),

            "link": full_link,

            "scraped_at": datetime.now()

        })

    return pd.DataFrame(items)