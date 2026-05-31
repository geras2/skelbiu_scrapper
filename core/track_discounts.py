import pandas as pd
import streamlit as st

from core.ad_collection import (
    collect_ads_from_urls
)

from core.helpers import (
    load_excel,
    write_excel,
    build_discount_urls
)


def run_track_discounts(
    file,
    url
):

    # -----------------------------------
    # SCRAPE CURRENT ADS
    # -----------------------------------

    urls = build_discount_urls(url)

    scraped_df = collect_ads_from_urls(
        urls
    )

    # -----------------------------------
    # LOAD HISTORY
    # -----------------------------------

    excel_df = load_excel(
        file,
        "discounts_tracker"
    )
    # -----------------------------------
    # MIGRATE OLD FILES
    # -----------------------------------

    if "ad_id" not in excel_df.columns:

        st.warning(
            "Old file detected. "
            "Generating ad_id from links..."
        )

        excel_df["ad_id"] = (

            excel_df["link"]
            .astype(str)
            .str.extract(
                r"-(\d+)\.html"
            )[0]

        )
    # -----------------------------------
    # FIRST RUN
    # -----------------------------------

    if len(excel_df) == 0:

        scraped_df["status"] = "new"

        write_excel(
            scraped_df,
            url,
            file,
            "discounts_tracker"
        )

        st.success(
            f"Initial load: {len(scraped_df)} ads"
        )

        st.dataframe(scraped_df)

        return

    # -----------------------------------
    # BACKWARD COMPATIBILITY
    # -----------------------------------

    if "status" not in excel_df.columns:

        excel_df["status"] = None

    # -----------------------------------
    # LATEST SNAPSHOT PER AD
    # -----------------------------------

    latest_excel = (

        excel_df
        .sort_values("scraped_at")
        .groupby("ad_id")
        .tail(1)
        .copy()

    )

    # -----------------------------------
    # NEW ADS
    # -----------------------------------

    new_ads = scraped_df[

        ~scraped_df["ad_id"].isin(
            latest_excel["ad_id"]
        )

    ].copy()

    new_ads["status"] = "new"

    # -----------------------------------
    # CHANGED ADS
    # -----------------------------------

    ignore_cols = [

        "scraped_at",
        "meta",
        "status"

    ]

    compare_cols = [

        col

        for col in scraped_df.columns

        if col not in ignore_cols

    ]

    old_cmp = latest_excel[
        compare_cols
    ].copy()

    new_cmp = scraped_df[
        compare_cols
    ].copy()

    changed_ids = []

    common_ids = set(
        scraped_df["ad_id"]
    ) & set(
        latest_excel["ad_id"]
    )

    for ad_id in common_ids:

        old_row = old_cmp[
            old_cmp["ad_id"] == ad_id
        ].iloc[0]

        new_row = new_cmp[
            new_cmp["ad_id"] == ad_id
        ].iloc[0]

        changed = False

        for col in compare_cols:

            if col == "ad_id":
                continue

            old_val = str(
                old_row[col]
            )

            new_val = str(
                new_row[col]
            )

            if old_val != new_val:

                changed = True

                break

        if changed:

            changed_ids.append(
                ad_id
            )

    changed_ads = scraped_df[

        scraped_df["ad_id"].isin(
            changed_ids
        )

    ].copy()

    changed_ads["status"] = (
        "changed"
    )

    # -----------------------------------
    # POSSIBLE SOLD
    # -----------------------------------

    current_ids = set(
        scraped_df["ad_id"]
    )

    possible_sold = latest_excel[

        (~latest_excel["ad_id"].isin(
            current_ids
        ))

        &

        (
            latest_excel["status"]
            .fillna("")
            .ne("possible sold")
        )

    ].copy()

    possible_sold["status"] = (
        "possible sold"
    )

    possible_sold["scraped_at"] = (
        pd.Timestamp.now()
    )

    # -----------------------------------
    # COMBINE CHANGES
    # -----------------------------------

    changes_df = pd.concat(

        [

            new_ads,
            changed_ads,
            possible_sold

        ],

        ignore_index=True

    )

    # -----------------------------------
    # NOTHING CHANGED
    # -----------------------------------

    if len(changes_df) == 0:

        st.info(
            "No changes detected"
        )

        return

    # -----------------------------------
    # APPEND TO HISTORY
    # -----------------------------------

    combined_df = pd.concat(

        [
            excel_df,
            changes_df
        ],

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
    # UI
    # -----------------------------------

    st.success(
        f"Changes detected: {len(changes_df)}"
    )

    st.write(
        f"New: {len(new_ads)} | "
        f"Changed: {len(changed_ads)} | "
        f"Possible sold: {len(possible_sold)}"
    )

    st.dataframe(
        changes_df
    )