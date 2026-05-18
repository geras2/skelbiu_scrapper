# app.py

import streamlit as st
import pandas as pd
from pathlib import Path
import time
import random
from pathlib import Path
from core.update_from_git import update_app
from core.scrape_views import (
    extract_ads,
    extract_ad_info
)
from core.helpers import now_lt, write_excel
from core.rerun_ads import run_rerun_ads
from core.run_new_ads import run_run_new_ads
from core.file_selector import (
    render_file_selector
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

    # # ---------------------------------------------------
    # # FILE SELECTION
    # # ---------------------------------------------------

    # data_folder = Path("data")

    # data_folder.mkdir(exist_ok=True)

    # excel_files = sorted(
    #     data_folder.glob("*.xlsx"),
    #     key=lambda x: x.stat().st_mtime,
    #     reverse=True
    # )
    # options = [f.name for f in excel_files] + ["NEW FILE"]

    # default_index = 0

    # selected_file = st.selectbox(
    #     "Select Excel file",
    #     options,
    #     index=default_index
    # )

    # # ---------------------------------------------------
    # # RESOLVE FILE
    # # ---------------------------------------------------

    # loaded_url = ""

    # if selected_file == "NEW FILE":

    #     new_file_name = st.text_input(
    #         "New file name",
    #         value="skelbiu_bikes.xlsx"
    #     )

    #     file = data_folder / new_file_name

    # else:

    #     file = data_folder / selected_file

    #     # load URL from workbook
    #     try:

    #         url_df = pd.read_excel(
    #             file,
    #             sheet_name="url"
    #         )

    #         loaded_url = url_df.loc[0, "url"]

    #     except Exception:

    #         loaded_url = ""

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

    # ---------------------------------------------------
    # update app from git
    # ---------------------------------------------------
    ACTIONS = {
        "Add New Ads": run_run_new_ads,
        "Rerun Existing Ads": run_rerun_ads,
        "Update App": run_update_app,
    }
    for label, func in ACTIONS.items():

        if st.button(label):
            # func()
            func(file=file, url=url)
        


