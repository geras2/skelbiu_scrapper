# app.py

import streamlit as st
import pandas as pd
from pathlib import Path

from scrape_views import (
    extract_ads,
    extract_ad_info
)

# ----------------------------------------
# PAGE
# ----------------------------------------

st.set_page_config(
    page_title="Skelbiu Scraper",
    layout="wide"
)

st.title("Skelbiu Scraper")

# ----------------------------------------
# INPUTS
# ----------------------------------------

default_url = (
    "https://www.skelbiu.lt/skelbimai/"
)

url = st.text_area(
    "Skelbiu URL",
    value=default_url,
    height=120
)

file = st.text_input(
    "Excel file",
    value="skelbiu_bikes.xlsx"
)

run_button = st.button("Run Scraper")

# ----------------------------------------
# RUN
# ----------------------------------------

if run_button:

    try:

        st.write("Extracting ads...")

        df = extract_ads(url)

        st.write(f"Found {len(df)} ads")

        # --------------------------------
        # ENRICH
        # --------------------------------

        progress = st.progress(0)

        details = []

        total = len(df)

        for i, link in enumerate(df["link"]):

            details.append(
                extract_ad_info(link)
            )

            progress.progress((i + 1) / total)

        details_df = pd.DataFrame(details)

        df[
            ["ad_id", "views", "bookmarks"]
        ] = details_df

        # --------------------------------
        # TIMESTAMP
        # --------------------------------

        df["scraped_at"] = (
            pd.Timestamp.now(
                tz="Europe/Vilnius"
            )
            .tz_localize(None)
            .floor("s")
        )

        # --------------------------------
        # APPEND HISTORY
        # --------------------------------

        path = Path(file)

        if path.exists():

            old_df = pd.read_excel(file)

            df = pd.concat(
                [old_df, df],
                ignore_index=True
            )

        # --------------------------------
        # DEDUP
        # --------------------------------

        df = df.drop_duplicates(
            subset=["ad_id", "scraped_at"],
            keep="last"
        )

        # --------------------------------
        # SAVE
        # --------------------------------

        df.to_excel(file, index=False)

        st.success(f"Saved to {file}")

        st.dataframe(df.tail(20))

    except Exception as e:

        st.error(str(e))