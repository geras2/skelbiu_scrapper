    # ---------------------------------------------------
    # ADD NEW ADS
    # ---------------------------------------------------
    # if add_new_button:
import random
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from core.scrape_views import extract_ad_info
from core.helpers import now_lt, write_excel
from core.scrape_views import (
    extract_ads,
    extract_ad_info
)
def run_run_new_ads(file, url):

    try:

        st.write(
            "Extracting ads from search page..."
        )

        # --------------------------------------
        # Extract search results
        # --------------------------------------

        scraped_df = extract_ads(url)

        st.write(
            f"Found {len(scraped_df)} ads"
        )

        # --------------------------------------
        # Existing file
        # --------------------------------------

        if file.exists():

            old_df = pd.read_excel(
                file,
                sheet_name="data"
            )

            existing_links = (

                old_df["link"]
                .astype(str)
                .unique()

            )

            # Keep only unseen ads
            new_df = scraped_df[
                ~scraped_df["link"]
                .astype(str)
                .isin(existing_links)
            ].copy()

            st.write(
                f"New ads: {len(new_df)}"
            )

            # ----------------------------------
            # Enrich ONLY new ads
            # ----------------------------------

            if len(new_df) > 0:

                details = []

                progress = st.progress(0)

                total = len(new_df)

                for i, link in enumerate(
                    new_df["link"]
                ):

                    result = extract_ad_info(
                        link
                    )

                    details.append(result)

                    progress.progress(
                        (i + 1) / total
                    )

                    time.sleep(
                        random.uniform(1, 2)
                    )

                details_df = pd.DataFrame(
                    details
                )

                new_df[
                    [
                        "ad_id",
                        "views",
                        "bookmarks"
                    ]
                ] = details_df

                new_df["scraped_at"] = (
                    now_lt()
                )

                combined_df = pd.concat(

                    [old_df, new_df],
                    ignore_index=True

                )

            else:

                combined_df = old_df

        # --------------------------------------
        # New file
        # --------------------------------------

        else:

            new_df = scraped_df.copy()

            details = []

            progress = st.progress(0)

            total = len(new_df)

            for i, link in enumerate(
                new_df["link"]
            ):

                result = extract_ad_info(
                    link
                )

                details.append(result)

                progress.progress(
                    (i + 1) / total
                )

                time.sleep(
                    random.uniform(1, 2)
                )

            details_df = pd.DataFrame(
                details
            )

            new_df[
                [
                    "ad_id",
                    "views",
                    "bookmarks"
                ]
            ] = details_df

            new_df["scraped_at"] = (
                now_lt()
            )

            combined_df = new_df

        # --------------------------------------
        # Save
        # --------------------------------------

        write_excel(
            combined_df,
            url,
            file
        )

        st.success(
            f"Dataset rows: "
            f"{len(combined_df)}"
        )

        st.dataframe(combined_df)

    except Exception as e:

        st.error(str(e))

