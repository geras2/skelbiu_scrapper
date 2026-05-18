# app.py

import streamlit as st
import pandas as pd
from pathlib import Path
import time
import random
from pathlib import Path
from core.update_from_git import update_app
# from core.scrape_views import (
#     extract_ads,
#     extract_ad_info
# )
from core.helpers import (write_excel,build_discount_urls, load_excel)
from core.rerun_ads import run_rerun_ads
from core.run_new_ads import run_run_new_ads
from core.file_selector import render_file_selector

from core.ad_collection import (
    collect_ads_from_urls
)
def main():
    # ---------------------------------------------------
    # CONFIG
    # ---------------------------------------------------

    st.set_page_config(
        page_title="Skelbiu Tracker",
        layout="wide"
    )

    st.title("Skelbiu Tracker")

    file, loaded_url = (
        render_file_selector()
    )
    # ---------------------------------------------------
    # URL INPUT
    # ---------------------------------------------------

    url = st.text_area(
        "Skelbiu URL",
        value=loaded_url,
        height=120
    )

    # ---------------------------------------------------
    # update button function
    # ---------------------------------------------------
    def run_update_app():

        try:

            update_app()

        except Exception as e:

            st.error(str(e))



    def run_track_discounts(file, url):

        urls = build_discount_urls(url)

        scraped_df = collect_ads_from_urls(urls)

        # then reuse existing enrichment logic
        # --------------------------------------
        # Save
        # --------------------------------------
        excel_df = load_excel(
            file,
            "discounts_tracker"
        )
        combined_df = pd.concat(
            [excel_df, scraped_df],
            ignore_index=True
        )
        combined_df = combined_df.drop_duplicates(
            subset=[
                col
                for col in combined_df.columns
                if col != "scraped_at"
            ]
        )
        write_excel(
            combined_df,
            url,
            file,
            "discounts_tracker"
        )

        st.success(
            f"Dataset rows: "
            f"{len(combined_df)}"
        )

        st.dataframe(combined_df)
    # ---------------------------------------------------
    # update app from git
    # ---------------------------------------------------
    ACTIONS = {
        "Add New Ads": run_run_new_ads,
        "Rerun Existing Ads": run_rerun_ads,
        "Check Discounts":run_track_discounts,
        "Update App": run_update_app,
    }
    cols = st.columns(len(ACTIONS))

    for col, (label, func) in zip(cols, ACTIONS.items()):

        with col:

            if st.button(label):

                func(file=file, url=url)
            


