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
from core.track_discounts import (
    run_track_discounts
)

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
    # update app from git
    # ---------------------------------------------------
    ACTIONS = {
        "Add New Ads": run_run_new_ads,
        "Rerun Existing Ads": run_rerun_ads,
        "Check Discounts":run_track_discounts,
        "Update App": update_app,
    }
    cols = st.columns(len(ACTIONS))

    for col, (label, func) in zip(cols, ACTIONS.items()):

        with col:

            if st.button(label):

                func(file=file, url=url)
            


