# skelbiu_scrapper

Streamlit-based scraper and tracker for Skelbiu.lt ads.

The app:
- extracts ads from Skelbiu search URLs
- collects:
  - title
  - price
  - location/time
  - views
  - bookmarks
  - ad ID
- stores historical snapshots into Excel files
- allows rerunning existing ads to track popularity changes over time

---

# Features

- Streamlit web UI
- Add and rerun ads from search URLs
- Excel export
- 
---

# Installation

## 1. Install Python

Download Python:

https://www.python.org/downloads/

IMPORTANT:
Enable:

```text
Add Python to PATH
```

during installation.

---

## 2. Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/skelbiu_scrapper.git
```

```bash
cd skelbiu_scrapper
```

---

## 3. Install dependencies

Run:

```bash
install.bat
```

or manually:

```bash
python -m pip install -r requirements.txt
```

---

# Running

Run:

```bash
start.bat
```

or manually:

```bash
python -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

# Project structure

```text
skelbiu_scrapper/
├── app.py
├── scrape_views.py
├── requirements.txt
├── install.bat
├── start.bat
├── README.md
└── data/
```

---

# Output

The scraper stores data into Excel files.

Columns include:

| column | description |
|---|---|
| ad_id | Skelbiu ad ID |
| title | ad title |
| price | listed price |
| meta | city and posting age |
| views | ad views |
| bookmarks | saved count |
| link | ad URL |
| scraped_at | scrape timestamp |

---

# Notes

- Skelbiu may rate-limit aggressive scraping.
- Slow reruns are recommended.
- Some fields may disappear if anti-bot protection activates.
- The scraper uses cloudscraper to reduce blocking.

---

# Disclaimer

This project is for educational and personal use only.

Respect Skelbiu.lt terms of service and avoid excessive scraping.
