#run_track_discounts()
 #├─ scrape_current_ads()
#  ├─ load_history()
#  ├─ detect_changes()
#  │   ├─ detect_new_ads()
#  │   ├─ detect_changed_ads()
#  │   └─ detect_possible_sold()
#  ├─ save_changes()
#  └─ show_results()

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

def migrate_history(df):

    if len(df) == 0:
        return df

    if "ad_id" not in df.columns:
        df["ad_id"] = (
            df["link"]
            .astype(str)
            .str.extract(
                r"-(\d+)\.html"
            )[0]
        )

    if "status" not in df.columns:
        df["status"] = None

    df["ad_id"] = (
        df["ad_id"]
        .astype(str)
        .str.strip()
    )

    return df

def latest_snapshot(history):

    return (
        history
        .sort_values("scraped_at")
        .groupby("ad_id")
        .tail(1)
        .copy()
    )
    
def detect_new_or_reposted_ads(
    current_ads,
    latest_ads
):
    """
    Rules:

    - ad_id never seen before      -> new
    - last status = possible sold -> reposted
    - otherwise                   -> ignore
    """

    latest_status = (
        latest_ads
        .set_index("ad_id")["status"]
        .to_dict()
    )

    result = []

    for _, row in current_ads.iterrows():

        ad_id = row["ad_id"]

        # completely new ad
        if ad_id not in latest_status:

            new_row = row.copy()
            new_row["status"] = "new"

            result.append(
                new_row
            )

            continue

        # ad disappeared previously
        # and now came back
        if latest_status[ad_id] == "possible sold":

            new_row = row.copy()
            new_row["status"] = "reposted"

            result.append(
                new_row
            )

    if not result:

        return pd.DataFrame(
            columns=current_ads.columns.tolist()
            + ["status"]
        )

    return pd.DataFrame(
        result
    )
    
# def detect_new_ads(
#     current_ads,
#     latest_ads
# ):

#     result = current_ads[
#         ~current_ads["ad_id"].isin(
#             latest_ads["ad_id"]
#         )
#     ].copy()

#     result["status"] = "new"

#     return result

def detect_changed_ads(
    current_ads,
    latest_ads
):

    ignore_cols = {
        "scraped_at",
        "meta",
        "status"
    }

    compare_cols = [
        c
        for c in current_ads.columns
        if c not in ignore_cols
    ]

    merged = current_ads.merge(
        latest_ads,
        on="ad_id",
        suffixes=(
            "_new",
            "_old"
        )
    )

    changed_mask = False

    for col in compare_cols:

        if col == "ad_id":
            continue

        diff = (
            merged[f"{col}_new"]
            .astype(str)
            !=
            merged[f"{col}_old"]
            .astype(str)
        )

        changed_mask |= diff

    changed_ids = merged.loc[
        changed_mask,
        "ad_id"
    ]

    result = current_ads[
        current_ads["ad_id"].isin(
            changed_ids
        )
    ].copy()

    result["status"] = "changed"

    return result

def detect_possible_sold(
    current_ads,
    latest_ads
):

    current_ids = set(
        current_ads["ad_id"]
    )

    result = latest_ads[
        ~latest_ads["ad_id"].isin(
            current_ids
        )
    ].copy()

    result["status"] = (
        "possible sold"
    )

    result["scraped_at"] = (
        pd.Timestamp.now()
    )

    return result

# detect_changes()
# ├── detect_new_or_reposted_ads()
# ├── detect_changed_ads()
# └── detect_possible_sold()
def detect_changes(
    current_ads,
    history
):

    if history.empty:

        current_ads = current_ads.copy()
        current_ads["status"] = "new"

        return current_ads

    latest_ads = latest_snapshot(
        history
    )

    new_or_reposted_ads = (
        detect_new_or_reposted_ads(
            current_ads,
            latest_ads
        )
    )

    changed_ads = (
        detect_changed_ads(
            current_ads,
            latest_ads
        )
    )

    possible_sold = (
        detect_possible_sold(
            current_ads,
            latest_ads
        )
    )

    return pd.concat(
        [
            new_or_reposted_ads,
            changed_ads,
            possible_sold
        ],
        ignore_index=True
    )
    
def load_history(file):
    df = load_excel(
        file,
        "discounts_tracker"
    )

    return migrate_history(df)

def scrape_current_ads(url):
    urls = build_discount_urls(url)
    return collect_ads_from_urls(urls)

def show_results(changes):

    new_count = (
        changes["status"] == "new"
    ).sum()

    changed_count = (
        changes["status"] == "changed"
    ).sum()

    sold_count = (
        changes["status"] == "possible sold"
    ).sum()

    st.success(
        f"Changes detected: {len(changes)}"
    )

    st.write(
        f"New: {new_count} | "
        f"Changed: {changed_count} | "
        f"Possible sold: {sold_count}"
    )

    st.dataframe(changes)

def save_changes(
    history,
    changes,
    url,
    file
):

    combined = pd.concat(
        [
            history,
            changes
        ],
        ignore_index=True
    )

    write_excel(
        combined,
        url,
        file,
        "discounts_tracker"
    )

    return combined

def run_track_discounts(file, url):
    current_ads = scrape_current_ads(url)
    history = load_history(file)

    history = migrate_history(history)

    changes = detect_changes(
        current_ads=current_ads,
        history=history
    )

    if changes.empty:
        st.info("No changes detected")
        return

    save_changes(
        history,
        changes,
        url,
        file
    )

    show_results(changes)
    
    

# def run_track_discounts(
#     file,
#     url
# ):

#     # -----------------------------------
#     # SCRAPE CURRENT ADS
#     # -----------------------------------

#     urls = build_discount_urls(url)

#     scraped_df = collect_ads_from_urls(
#         urls
#     )

#     # -----------------------------------
#     # LOAD HISTORY
#     # -----------------------------------

#     excel_df = load_excel(
#         file,
#         "discounts_tracker"
#     )
    
#     # -----------------------------------
#     # FIRST RUN
#     # -----------------------------------

#     if len(excel_df) == 0:

#         scraped_df["status"] = "new"

#         write_excel(
#             scraped_df,
#             url,
#             file,
#             "discounts_tracker"
#         )

#         st.success(
#             f"Initial load: {len(scraped_df)} ads"
#         )

#         st.dataframe(scraped_df)

#         return
#     # -----------------------------------
#     # MIGRATE OLD FILES
#     # -----------------------------------

#     if "ad_id" not in excel_df.columns:

#         st.warning(
#             "Old file detected. "
#             "Generating ad_id from links..."
#         )

#         excel_df["ad_id"] = (

#             excel_df["link"]
#             .astype(str)
#             .str.extract(
#                 r"-(\d+)\.html"
#             )[0]

#         )
#     # -----------------------------------
#     # BACKWARD COMPATIBILITY
#     # -----------------------------------

#     if "status" not in excel_df.columns:

#         excel_df["status"] = None

#     # -----------------------------------
#     # LATEST SNAPSHOT PER AD
#     # -----------------------------------

#     latest_excel = (

#         excel_df
#         .sort_values("scraped_at")
#         .groupby("ad_id")
#         .tail(1)
#         .copy()

#     )

#     # -----------------------------------
#     # NEW ADS
#     # -----------------------------------

#     new_ads = scraped_df[

#         ~scraped_df["ad_id"].isin(
#             latest_excel["ad_id"]
#         )

#     ].copy()

#     new_ads["status"] = "new"

#     # -----------------------------------
#     # CHANGED ADS
#     # -----------------------------------

#     ignore_cols = [

#         "scraped_at",
#         "meta",
#         "status"

#     ]

#     compare_cols = [

#         col

#         for col in scraped_df.columns

#         if col not in ignore_cols

#     ]

#     old_cmp = latest_excel[
#         compare_cols
#     ].copy()

#     new_cmp = scraped_df[
#         compare_cols
#     ].copy()

#     changed_ids = []

#     common_ids = set(
#         scraped_df["ad_id"]
#     ) & set(
#         latest_excel["ad_id"]
#     )

#     for ad_id in common_ids:

#         old_row = old_cmp[
#             old_cmp["ad_id"] == ad_id
#         ].iloc[0]

#         new_row = new_cmp[
#             new_cmp["ad_id"] == ad_id
#         ].iloc[0]

#         changed = False

#         for col in compare_cols:

#             if col == "ad_id":
#                 continue

#             old_val = str(
#                 old_row[col]
#             )

#             new_val = str(
#                 new_row[col]
#             )

#             if old_val != new_val:

#                 changed = True

#                 break

#         if changed:

#             changed_ids.append(
#                 ad_id
#             )

#     changed_ads = scraped_df[

#         scraped_df["ad_id"].isin(
#             changed_ids
#         )

#     ].copy()

#     changed_ads["status"] = (
#         "changed"
#     )

#     # -----------------------------------
#     # POSSIBLE SOLD
#     # -----------------------------------

#     current_ids = set(
#         scraped_df["ad_id"]
#     )

#     possible_sold = latest_excel[

#         (~latest_excel["ad_id"].isin(
#             current_ids
#         ))

#         &

#         (
#             latest_excel["status"]
#             .fillna("")
#             .ne("possible sold")
#         )

#     ].copy()

#     possible_sold["status"] = (
#         "possible sold"
#     )

#     possible_sold["scraped_at"] = (
#         pd.Timestamp.now()
#     )

#     # -----------------------------------
#     # COMBINE CHANGES
#     # -----------------------------------

#     changes_df = pd.concat(

#         [

#             new_ads,
#             changed_ads,
#             possible_sold

#         ],

#         ignore_index=True

#     )

#     # -----------------------------------
#     # NOTHING CHANGED
#     # -----------------------------------

#     if len(changes_df) == 0:

#         st.info(
#             "No changes detected"
#         )

#         return

#     # -----------------------------------
#     # APPEND TO HISTORY
#     # -----------------------------------

#     combined_df = pd.concat(

#         [
#             excel_df,
#             changes_df
#         ],

#         ignore_index=True

#     )

#     # -----------------------------------
#     # SAVE
#     # -----------------------------------

#     write_excel(

#         combined_df,

#         url,

#         file,

#         "discounts_tracker"

#     )

#     # -----------------------------------
#     # UI
#     # -----------------------------------

#     st.success(
#         f"Changes detected: {len(changes_df)}"
#     )

#     st.write(
#         f"New: {len(new_ads)} | "
#         f"Changed: {len(changed_ads)} | "
#         f"Possible sold: {len(possible_sold)}"
#     )

#     st.dataframe(
#         changes_df
#     )