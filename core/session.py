from functools import lru_cache

import cloudscraper


@lru_cache(maxsize=1)
def get_scraper():

    scraper = cloudscraper.create_scraper(
        browser={
            "browser": "chrome",
            "platform": "windows",
            "mobile": False,
        }
    )

    scraper.headers.update({
        "Accept-Language": "lt-LT,lt;q=0.9,en;q=0.8",
    })

    scraper.get("https://www.skelbiu.lt", timeout=30)

    return scraper