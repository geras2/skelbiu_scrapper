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

def main():
    # ---------------------------------------------------
    # CONFIG
    # ---------------------------------------------------

    st.set_page_config(
        page_title="Skelbiu Tracker",
        layout="wide"
    )

    st.title("Skelbiu Tracker")

    # ---------------------------------------------------
    # FILE SELECTION
    # ---------------------------------------------------

    data_folder = Path("data")

    data_folder.mkdir(exist_ok=True)

    excel_files = sorted(
        data_folder.glob("*.xlsx"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    options = [f.name for f in excel_files] + ["NEW FILE"]

    default_index = 0

    selected_file = st.selectbox(
        "Select Excel file",
        options,
        index=default_index
    )

    # ---------------------------------------------------
    # RESOLVE FILE
    # ---------------------------------------------------

    loaded_url = ""

    if selected_file == "NEW FILE":

        new_file_name = st.text_input(
            "New file name",
            value="skelbiu_bikes.xlsx"
        )

        file = data_folder / new_file_name

    else:

        file = data_folder / selected_file

        # load URL from workbook
        try:

            url_df = pd.read_excel(
                file,
                sheet_name="url"
            )

            loaded_url = url_df.loc[0, "url"]

        except Exception:

            loaded_url = ""

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
    # ADD NEW ADS
    # ---------------------------------------------------
    # if add_new_button:
    def run_add_new_ads():

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

    # # ---------------------------------------------------
    # # RERUN EXISTING ADS
    # # ---------------------------------------------------

    # # if rerun_existing_button:
    # def run_rerun_ads():

    #     try:

    #         path = Path(file)

    #         if not path.exists():

    #             st.error(
    #                 "Excel file does not exist yet"
    #             )

    #             st.stop()

    #         old_df = pd.read_excel(file)

    #         # ------------------------------------------
    #         # LATEST UNIQUE ADS
    #         # ------------------------------------------

    #         latest_ads = (
    #             old_df
    #             .sort_values("scraped_at")
    #             .groupby("ad_id")
    #             .tail(1)
    #             .copy()
    #         )

    #         st.write(
    #             f"Rerunning {len(latest_ads)} ads..."
    #         )

    #         # ------------------------------------------
    #         # UPDATE METRICS
    #         # ------------------------------------------

    #         details = []

    #         progress = st.progress(0)

    #         total = len(latest_ads)

    #         for i, link in enumerate(latest_ads["link"]):

    #             details.append(
    #                 extract_ad_info(link)
    #             )
    #             time.sleep(
    #                     random.uniform(1, 2)
    #                 )
    #             progress.progress((i + 1) / total)

    #         details_df = pd.DataFrame(details).reset_index(drop=True)

    #         latest_ads = latest_ads.reset_index(drop=True)

    #         latest_ads["ad_id"] = details_df["ad_id"]
    #         latest_ads["views"] = details_df["views"]
    #         latest_ads["bookmarks"] = details_df["bookmarks"]
            
    #         latest_ads["scraped_at"] = now_lt()

    #         # ------------------------------------------
    #         # APPEND SNAPSHOT
    #         # ------------------------------------------

    #         combined_df = pd.concat(
    #             [old_df, latest_ads],   
    #             ignore_index=True
    #         )

    #         write_excel(combined_df, url,file)
    #         # write_data(combined_df, file)
    #         # write_url(url,file)
    #         st.success(
    #             f"Updated {len(latest_ads)} ads"
    #         )

    #         st.dataframe(latest_ads)

    #     except Exception as e:

    #         st.error(str(e))
    # ---------------------------------------------------
    # update app from git
    # ---------------------------------------------------
    ACTIONS = {
        "Add New Ads": run_add_new_ads,
        "Rerun Existing Ads": run_rerun_ads,
        "Update App": run_update_app,
    }
    for label, func in ACTIONS.items():

        if st.button(label):
            # func()
            func(file=file, url=url)
        


