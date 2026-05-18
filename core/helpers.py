# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
import pandas as pd


def now_lt():

    return (
        pd.Timestamp.now(tz="Europe/Vilnius")
        .tz_localize(None)
        .floor("s")
    )
def write_excel(combined_df, url, file):

    with pd.ExcelWriter(
        file,
        engine="openpyxl"
    ) as writer:

        # Main ads data
        combined_df.to_excel(
            writer,
            sheet_name="data",
            index=False
        )

        # Source URL
        pd.DataFrame({
            "url": [url]
        }).to_excel(
            writer,
            sheet_name="url",
            index=False
        )
        