# app.py

import streamlit as st
import pandas as pd
from pathlib import Path
import time
import random
from pathlib import Path

from scrape_views import (
    extract_ads,
    extract_ad_info
)

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Skelbiu Tracker",
    layout="wide"
)

st.title("Skelbiu Tracker")

# ---------------------------------------------------
# INPUTS
# ---------------------------------------------------

url = st.text_area(
    "Skelbiu URL",
    height=120
)

# ---------------------------------------------------
# ADD NEW BUTTON
# ---------------------------------------------------

add_new_button = st.button(
    "Add New Ads"
)


# folder with excel files
data_folder = Path("data")

# create folder if missing
data_folder.mkdir(exist_ok=True)

# scan existing xlsx files
excel_files = sorted(
    [f.name for f in data_folder.glob("*.xlsx")]
)

# default option
options = ["NEW FILE"] + excel_files

selected_file = st.selectbox(
    "Select Excel file",
    options
)

# create new file
if selected_file == "NEW FILE":

    new_file_name = st.text_input(
        "New file name",
        value="skelbiu_bikes.xlsx"
    )

    file = data_folder / new_file_name

else:

    file = data_folder / selected_file

path = Path(file)
# ---------------------------------------------------
# BUTTONS
# ---------------------------------------------------

col1, col2 = st.columns(2)

# add_new_button = col1.button(
#     "Add New Ads"
# )

rerun_existing_button = st.button(
    "Rerun Existing Ads"
)

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------

def now_lt():

    return (
        pd.Timestamp.now(tz="Europe/Vilnius")
        .tz_localize(None)
        .floor("s")
    )


# ---------------------------------------------------
# ADD NEW ADS
# ---------------------------------------------------

if add_new_button:

    try:

        st.write("Extracting ads from search page...")

        new_df = extract_ads(url)

        st.write(f"Found {len(new_df)} ads")

        # ------------------------------------------
        # ENRICH NEW ADS
        # ------------------------------------------

        details = []

        progress = st.progress(0)

        total = len(new_df)

        for i, link in enumerate(latest_ads["link"]):

            result = extract_ad_info(link)

            details.append(result)

            progress.progress((i + 1) / total)

            time.sleep(
                random.uniform(2, 5)
            )

        details_df = pd.DataFrame(details)

        new_df[
            ["ad_id", "views", "bookmarks"]
        ] = details_df

        new_df["scraped_at"] = now_lt()

        path = Path(file)

        # ------------------------------------------
        # APPEND ONLY NEW ADS
        # ------------------------------------------

        if path.exists():

            old_df = pd.read_excel(file)

            existing_ids = (
                old_df["ad_id"]
                .astype(str)
                .unique()
            )

            new_df = new_df[
                ~new_df["ad_id"]
                .astype(str)
                .isin(existing_ids)
            ]

            combined_df = pd.concat(
                [old_df, new_df],
                ignore_index=True
            )

        else:

            combined_df = new_df

        combined_df.to_excel(
            file,
            index=False
        )

        st.success(
            f"Added {len(new_df)} new ads"
        )

        st.dataframe(new_df)

    except Exception as e:

        st.error(str(e))


# ---------------------------------------------------
# RERUN EXISTING ADS
# ---------------------------------------------------

if rerun_existing_button:

    try:

        path = Path(file)

        if not path.exists():

            st.error(
                "Excel file does not exist yet"
            )

            st.stop()

        old_df = pd.read_excel(file)

        # ------------------------------------------
        # LATEST UNIQUE ADS
        # ------------------------------------------

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

        # ------------------------------------------
        # UPDATE METRICS
        # ------------------------------------------

        details = []

        progress = st.progress(0)

        total = len(latest_ads)

        for i, link in enumerate(latest_ads["link"]):

            details.append(
                extract_ad_info(link)
            )

            progress.progress((i + 1) / total)

        # details_df = pd.DataFrame(details)

        # latest_ads[
        #     ["ad_id", "views", "bookmarks"]
        # ] = details_df
        details_df = pd.DataFrame(details).reset_index(drop=True)

        latest_ads = latest_ads.reset_index(drop=True)

        latest_ads["ad_id"] = details_df["ad_id"]
        latest_ads["views"] = details_df["views"]
        latest_ads["bookmarks"] = details_df["bookmarks"]
        
        latest_ads["scraped_at"] = now_lt()

        # ------------------------------------------
        # APPEND SNAPSHOT
        # ------------------------------------------

        combined_df = pd.concat(
            [old_df, latest_ads],
            ignore_index=True
        )

        combined_df.to_excel(
            file,
            index=False
        )

        st.success(
            f"Updated {len(latest_ads)} ads"
        )

        st.dataframe(latest_ads)

    except Exception as e:

        st.error(str(e))