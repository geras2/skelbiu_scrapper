
import pandas as pd

from core.scrape_views import extract_ads


def collect_ads_from_urls(urls):

    dfs = []
    # print(urls)
    for url in urls:
        df = extract_ads(url)

        dfs.append(df)

    combined = pd.concat(
        dfs,
        ignore_index=True
    )

    combined = combined.drop_duplicates(
        subset=["link", "price"]
    )

    return combined