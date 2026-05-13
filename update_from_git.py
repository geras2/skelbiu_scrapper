import zipfile
import shutil
import tempfile
import requests
import streamlit as st
from pathlib import Path

def update_app():

    repo_zip = (
        "https://github.com/geras2/"
        "skelbiu_scrapper/archive/"
        "refs/heads/main.zip"
    )

    st.write("Downloading update...")

    # temp folder
    temp_dir = tempfile.mkdtemp()

    zip_path = Path(temp_dir) / "update.zip"

    # ----------------------------------------
    # Download ZIP
    # ----------------------------------------

    r = requests.get(repo_zip)

    with open(zip_path, "wb") as f:

        f.write(r.content)

    # ----------------------------------------
    # Extract ZIP
    # ----------------------------------------

    extract_dir = Path(temp_dir) / "extract"

    with zipfile.ZipFile(zip_path, "r") as z:

        z.extractall(extract_dir)

    # GitHub creates nested folder
    source_dir = next(
        extract_dir.iterdir()
    )

    # ----------------------------------------
    # Files to update
    # ----------------------------------------

    files_to_copy = [

        "app.py",
        "scrape_views.py",
        "requirements.txt",
        "install.bat",
        "start.bat"

    ]

    for filename in files_to_copy:

        src = source_dir / filename

        dst = Path(filename)

        if src.exists():

            shutil.copy2(src, dst)

    shutil.rmtree(temp_dir)

    st.success(
        "Update completed. "
        "Restart app."
    )