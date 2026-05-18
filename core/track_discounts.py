import pandas as pd
import streamlit as st

from core.ad_collection import (
    collect_ads_from_urls
)

from core.helpers import (
    load_excel,
    write_excel
)

from core.helpers import (
    build_discount_urls
)


def run_track_discounts(
    file,
    url
):

    # -----------------------------------
    # BUILD PAGINATED URLS
    # -----------------------------------

    urls = build_discount_urls(url)

    # -----------------------------------
    # SCRAPE ADS
    # -----------------------------------

    scraped_df = collect_ads_from_urls(
        urls
    )

    # -----------------------------------
    # LOAD EXISTING DATA
    # -----------------------------------

    excel_df = load_excel(
        file,
        "discounts_tracker"
    )

    # -----------------------------------
    # COMPARE COLUMNS
    # Ignore scraped_at
    # -----------------------------------

    compare_cols = [

        col
        for col in scraped_df.columns
        if col != "scraped_at"

    ]

    # -----------------------------------
    # FIND NEW / CHANGED ROWS
    # -----------------------------------

    if len(excel_df) > 0:

        new_rows = scraped_df.merge(

            excel_df[compare_cols],

            how="left",

            indicator=True,

            on=compare_cols

        )

        new_rows = new_rows[
            new_rows["_merge"] == "left_only"
        ].drop(columns="_merge")

    else:

        new_rows = scraped_df.copy()

    # -----------------------------------
    # APPEND NEW ROWS
    # -----------------------------------

    combined_df = pd.concat(
        [excel_df, new_rows],
        ignore_index=True
    )

    # -----------------------------------
    # SAVE
    # -----------------------------------

    write_excel(

        combined_df,

        url,

        file,

        "discounts_tracker"

    )

    # -----------------------------------
    # UI OUTPUT
    # -----------------------------------

    st.success(
        f"New changes: {len(new_rows)}"
    )

    st.dataframe(new_rows)