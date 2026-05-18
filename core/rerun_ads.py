import random
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from core.scrape_views import extract_ad_info
from core.helpers import now_lt, write_excel


def run_rerun_ads(file, url):

    try:

        path = Path(file)

        if not path.exists():

            st.error(
                "Excel file does not exist yet"
            )

            st.stop()

        old_df = pd.read_excel(
            file,
            sheet_name="data"
        )

        latest_ads = (
            old_df
            .sort_values("scraped_at")
            .groupby("ad_id")
            .tail(1)
            .copy()
        )

        st.write(
            f"Rerunning {len(latest_ads)} ads..."
        )

        details = []

        progress = st.progress(0)

        total = len(latest_ads)

        for i, link in enumerate(latest_ads["link"]):

            details.append(
                extract_ad_info(link)
            )

            time.sleep(
                random.uniform(1, 2)
            )

            progress.progress(
                (i + 1) / total
            )

        details_df = (
            pd.DataFrame(details)
            .reset_index(drop=True)
        )

        latest_ads = (
            latest_ads
            .reset_index(drop=True)
        )

        latest_ads["ad_id"] = details_df["ad_id"]
        latest_ads["views"] = details_df["views"]
        latest_ads["bookmarks"] = details_df["bookmarks"]

        latest_ads["scraped_at"] = now_lt()

        combined_df = pd.concat(
            [old_df, latest_ads],
            ignore_index=True
        )

        write_excel(
            combined_df,
            url,
            file
        )

        st.success(
            f"Updated {len(latest_ads)} ads"
        )

        st.dataframe(latest_ads)

    except Exception as e:

        st.error(str(e))