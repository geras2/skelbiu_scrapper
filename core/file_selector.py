from pathlib import Path

import pandas as pd
import streamlit as st


def render_file_selector():

    data_folder = Path("data")

    data_folder.mkdir(
        exist_ok=True
    )

    excel_files = sorted(
        data_folder.glob("*.xlsx"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    options = (
        [f.name for f in excel_files]
        + ["NEW FILE"]
    )

    selected_file = st.selectbox(
        "Select Excel file",
        options,
        index=0
    )

    loaded_url = ""

    if selected_file == "NEW FILE":

        new_file_name = st.text_input(
            "New file name",
            value="skelbiu_bikes.xlsx"
        )

        file = data_folder / new_file_name

    else:

        file = data_folder / selected_file

        try:

            url_df = pd.read_excel(
                file,
                sheet_name="url"
            )

            loaded_url = url_df.loc[0, "url"]

        except Exception:

            loaded_url = ""

    return file, loaded_url