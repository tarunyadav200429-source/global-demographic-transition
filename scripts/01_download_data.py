"""
=============================================================================
GLOBAL DEMOGRAPHIC TRANSITION
Step 01: Download real data from the World Bank Open Data API
=============================================================================

WHAT THIS SCRIPT DOES (in plain English):
  The World Bank publishes free, UN-sourced data about every country on Earth
  (population, life expectancy, fertility, etc.) going back to 1960.
  This script asks their public API for that data and saves it to CSV files
  on your computer, so the rest of the project can use it offline.

WHY WE DO IT THIS WAY (the "5-years-experience" thinking):
  A junior analyst downloads one messy Excel file by hand.
  A senior analyst writes a *reproducible* script: anyone can re-run it and get
  the exact same data. That is what makes a project look professional.

HOW TO RUN IT:
  Open a terminal in this project folder and type:
      python scripts/01_download_data.py
  (On Windows it might be:  py scripts\\01_download_data.py )
=============================================================================
"""

# --- 1. Import the tools we need -------------------------------------------
# 'requests' talks to the internet. 'pandas' handles tables of data.
# 'time' lets us pause politely between requests. 'os' handles file paths.
import time
import os
import requests          # if this errors: run  python -m pip install requests
import pandas as pd

# --- 2. Decide WHERE files will be saved -----------------------------------
# We build the path relative to THIS script's location, so it works no matter
# what folder you run it from. (A senior habit: never hard-code 'C:/Users/...')
HERE = os.path.dirname(os.path.abspath(__file__))          # the 'scripts' folder
RAW_DIR = os.path.join(HERE, "..", "data", "raw")          # the 'data/raw' folder
os.makedirs(RAW_DIR, exist_ok=True)                        # create it if missing

# --- 3. Decide WHAT data we want -------------------------------------------
# The World Bank gives each statistic a code. We pick 10 indicators that
# together tell the "demographic transition" story. The dict maps
#   API_CODE -> a friendly column name we will actually use.
INDICATORS = {
    "SP.POP.TOTL":        "population_total",        # total people
    "SP.POP.GROW":        "population_growth_pct",   # yearly growth %
    "SP.DYN.TFRT.IN":     "fertility_rate",          # births per woman
    "SP.DYN.LE00.IN":     "life_expectancy",         # years a newborn is expected to live
    "SP.DYN.CBRT.IN":     "birth_rate",              # births per 1,000 people
    "SP.DYN.CDRT.IN":     "death_rate",              # deaths per 1,000 people
    "SP.POP.0014.TO.ZS":  "pct_age_0_14",            # % of people aged 0-14 (children)
    "SP.POP.1564.TO.ZS":  "pct_age_15_64",           # % working-age (the "workforce")
    "SP.POP.65UP.TO.ZS":  "pct_age_65_plus",         # % aged 65+ (elderly)
    "SP.URB.TOTL.IN.ZS":  "urban_population_pct",    # % living in cities
    "SP.POP.DPND":        "dependency_ratio",        # dependents per 100 working-age
}

YEARS = "1960:2023"      # the range of years we ask for


# --- 4. A small helper that downloads a URL with automatic RETRIES ---------
# The internet is unreliable: APIs occasionally return errors for no good
# reason. A senior analyst NEVER assumes a request will succeed on the first
# try. This function tries up to 4 times, waiting a bit longer each time
# (called "exponential backoff"), before finally giving up.
def get_json_with_retry(url, max_tries=4):
    for attempt in range(1, max_tries + 1):
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()      # raises an error on a bad status code
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_tries:
                raise                        # out of tries -> let the error surface
            wait = 2 ** attempt              # 2s, 4s, 8s ...
            print(f"\n     (attempt {attempt} failed: {e}; retrying in {wait}s)",
                  end="", flush=True)
            time.sleep(wait)


# --- 4b. A helper function to download ONE indicator -----------------------
# We ask for ALL rows in a single page (per_page=20000). There are only ~265
# countries x ~64 years, so everything fits in one request. This is simpler
# AND more reliable than looping through many pages.
def download_indicator(code, friendly_name):
    print(f"  -> downloading {friendly_name}  ({code}) ...", end="", flush=True)
    url = (
        f"https://api.worldbank.org/v2/country/all/indicator/{code}"
        f"?format=json&date={YEARS}&per_page=20000"
    )
    payload = get_json_with_retry(url)       # [ metadata , data ]
    all_rows = payload[1] or []              # the data part (or empty if None)
    time.sleep(0.3)                          # be polite to the free API

    # Turn the raw rows into a tidy table with just the columns we care about.
    records = []
    for row in all_rows:
        records.append({
            "country_code": row["countryiso3code"],     # e.g. 'IND'
            "country_name": row["country"]["value"],     # e.g. 'India'
            "year":         int(row["date"]),
            friendly_name:  row["value"],                # the actual number (may be None)
        })
    df = pd.DataFrame(records)
    print(f" got {len(df):,} rows")
    return df


# --- 5. Download every indicator and MERGE them into one wide table --------
def download_all_indicators():
    print("STEP 1 of 2: downloading indicators")
    combined = None
    for code, name in INDICATORS.items():
        df = download_indicator(code, name)
        if combined is None:
            combined = df
        else:
            # 'merge' = SQL JOIN. We line up rows by country + year, then add
            # the new indicator as an extra column. This is a key DA skill.
            combined = combined.merge(
                df, on=["country_code", "country_name", "year"], how="outer"
            )
    # Save the raw, untouched download. We NEVER edit this file by hand -
    # it is our "source of truth" we can always go back to.
    out = os.path.join(RAW_DIR, "worldbank_indicators_raw.csv")
    combined.to_csv(out, index=False)
    print(f"   saved -> {out}   ({len(combined):,} rows, {combined.shape[1]} columns)\n")
    return combined


# --- 6. Download the COUNTRY METADATA (our 'dimension' table) --------------
# This tells us each country's Region and Income Group. We will JOIN this to
# the indicators later. It also marks which entries are real countries vs.
# aggregates like "World" or "South Asia" (which we must handle carefully).
def download_country_metadata():
    print("STEP 2 of 2: downloading country metadata (region, income group)")
    url = "https://api.worldbank.org/v2/country?format=json&per_page=400"
    payload = get_json_with_retry(url)
    rows = payload[1]
    records = []
    for r in rows:
        records.append({
            "country_code":  r["id"],                      # iso3 code, e.g. 'IND'
            "country_name":  r["name"],
            "region":        r["region"]["value"],         # e.g. 'South Asia'
            "income_group":  r["incomeLevel"]["value"],    # e.g. 'Lower middle income'
            "capital_city":  r["capitalCity"],
            # The API marks aggregates (World, regions...) with region = 'Aggregates'.
            # We add a clear True/False flag so cleaning is easy later.
            "is_aggregate":  r["region"]["value"] == "Aggregates",
        })
    df = pd.DataFrame(records)
    out = os.path.join(RAW_DIR, "worldbank_countries_raw.csv")
    df.to_csv(out, index=False)
    real = (~df["is_aggregate"]).sum()
    print(f"   saved -> {out}   ({len(df)} entries: {real} real countries, "
          f"{len(df)-real} aggregates)\n")
    return df


# --- 7. Run everything when the file is executed ---------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("DOWNLOADING REAL WORLD BANK DATA  (this takes ~30-60 seconds)")
    print("=" * 70)
    download_all_indicators()
    download_country_metadata()
    print("DONE. Look inside  data/raw/  for your two CSV files.")
