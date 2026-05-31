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

import re
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
def extract_html(link):

    scraper = cloudscraper.create_scraper()

    r = scraper.get(link)
    return r
    
def extract_ad_info(link):

    try:

        # ---------------------------------------------
        # Request ad page
        # ---------------------------------------------
        
        r = scraper.get(link, timeout=30)
        # r = extract_html(link)


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
        # print(soup.select_one("div.block.showed"))
        # print(link)
        # print(r.status_code)


        views_div = soup.select_one(
            "div.block.showed"
        )

        views = None

        if views_div:

            title = views_div.get("title", "")

            match = re.search(
                r"Skaitytas:\s*([\dK\.]+)",
                title
            )

            if match:

                views = parse_number(
                    match.group(1)
                )
                # ---------------------------------------------
        # Ad status
        #
        # Example:
        # <div class="info-description">
        #     Skelbimas pašalintas.
        # </div>
        # ---------------------------------------------

        status_el = soup.select_one(
            "div.info-description"
        )

        status = None

        if status_el:

            status = status_el.get_text(
                strip=True
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
            "bookmarks": bookmarks,
            "status": status
        })

    except Exception as e:

        print(e)

        # Return empty values if scraping fails
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
    """
    Extract ad ID from Skelbiu URL.

    Example:
    https://www.skelbiu.lt/skelbimai/...-84990032.html

    returns:
    84990032
    """

    match = re.search(
        r"-(\d+)\.html",
        link
    )

    return (
        match.group(1)
        if match
        else None
    )
    
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