# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
import pandas as pd
import re

def now_lt():

    return (
        pd.Timestamp.now(tz="Europe/Vilnius")
        .tz_localize(None)
        .floor("s")
    )
from pathlib import Path

import pandas as pd

def load_excel(
    file,
    data_sheet="data"
):
    path = Path(file)

    # -----------------------------------
    # LOAD EXISTING SHEET
    # -----------------------------------

    if path.exists():

        try:

            old_df = pd.read_excel(
                file,
                sheet_name=data_sheet
            )

        except Exception:

            old_df = pd.DataFrame()

    else:

        old_df = pd.DataFrame()
    return old_df

def write_excel(
    new_df,
    url,
    file,
    data_sheet="data"
):
    # -----------------------------------
    # WRITE BACK
    # -----------------------------------

    path = Path(file)

    with pd.ExcelWriter(
        file,
        engine="openpyxl",
        mode="w"
    ) as writer:

        new_df.to_excel(
            writer,
            sheet_name=data_sheet,
            index=False
        )
        if url:
            pd.DataFrame({
                "url": [url]
            }).to_excel(
                writer,
                sheet_name=f"url",
                index=False
            )


def build_discount_urls(base_url):

    urls = []

    for i in range(2, 15):

        # CASE 1:
        # already has /2?
        if re.search(r"/\d+\?", base_url):

            new_url = re.sub(
                r"/\d+\?",
                f"/{i}?",
                base_url
            )

        # CASE 2:
        # missing page number
        else:

            new_url = base_url.replace(
                "/?",
                f"/{i}?"
            )

        urls.append(new_url)

    return urls