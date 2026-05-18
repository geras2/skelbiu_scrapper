# ---------------------------------------------------------
# Standard library imports
# ---------------------------------------------------------

import re
from datetime import datetime

# ---------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------

import cloudscraper
import pandas as pd
import requests

from bs4 import BeautifulSoup

# ---------------------------------------------------------
# Create shared scraper session
#
# cloudscraper helps bypass basic anti-bot protection
# and Cloudflare challenges.
# ---------------------------------------------------------

scraper = cloudscraper.create_scraper()


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

def extract_ad_info(link):

    try:

        # ---------------------------------------------
        # Request ad page
        # ---------------------------------------------

        r = scraper.get(link, timeout=30)

        print(r.status_code)

        # Parse HTML
        soup = BeautifulSoup(r.text, "html.parser")

        # Extract full text content
        text = soup.get_text(" ", strip=True)

        # ---------------------------------------------
        # Extract ad ID
        #
        # Example:
        # "ID: 71466308"
        # ---------------------------------------------

        id_match = re.search(r"ID:\s*(\d+)", text)

        ad_id = id_match.group(1) if id_match else None

        # ---------------------------------------------
        # Extract views
        #
        # HTML example:
        # <div class="block showed">
        #     <span>1K</span>
        # </div>
        # ---------------------------------------------

        views_el = soup.select_one(
            "div.block.showed span"
        )

        views = None

        if views_el:

            views = parse_number(
                views_el.get_text(strip=True)
            )

        # ---------------------------------------------
        # Extract bookmarks
        #
        # Example text:
        # "Įsimintas 21"
        # ---------------------------------------------

        bookmarks_match = re.search(
            r"Įsimintas\s+(\d+)",
            text
        )

        bookmarks = (
            int(bookmarks_match.group(1))
            if bookmarks_match else None
        )

        # Return extracted data
        return pd.Series({

            "ad_id": ad_id,
            "views": views,
            "bookmarks": bookmarks

        })

    except Exception as e:

        print(e)

        # Return empty values if scraping fails
        return pd.Series({

            "ad_id": None,
            "views": None,
            "bookmarks": None

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

def extract_ads(link):

    # ---------------------------------------------
    # Browser-like headers
    #
    # Helps reduce blocking from Skelbiu
    # ---------------------------------------------

    headers = {

        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

    }

    # Request search page
    r = requests.get(link, headers=headers)

    # Raise error if request failed
    r.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(r.text, "html.parser")

    # Storage for extracted ads
    items = []

    # ---------------------------------------------
    # Find all ad links
    # ---------------------------------------------

    ads = soup.select("a[href*='/skelbimai/']")

    # Used to avoid duplicates
    seen = set()

    # ---------------------------------------------
    # Iterate through ads
    # ---------------------------------------------

    for ad in ads:

        href = ad.get("href")

        # Skip duplicates / invalid links
        if not href or href in seen:
            continue

        # Extract ad components
        title_el = ad.select_one("div.title")
        price_el = ad.select_one("div.price")
        meta_el = ad.select_one("div.second-dataline")

        # Skip incomplete elements
        if not title_el:
            continue

        seen.add(href)

        # Store extracted data
        items.append({

            "title": title_el.get_text(strip=True),

            "price": (
                price_el.get_text(" ", strip=True)
                if price_el else None
            ),

            "meta": (
                meta_el.get_text(" ", strip=True)
                if meta_el else None
            ),

            "link": (
                href if href.startswith("http")
                else f"https://www.skelbiu.lt{href}"
            ),

            "scraped_at": datetime.now()

        })

    # Convert results into DataFrame
    df = pd.DataFrame(items)

    return df