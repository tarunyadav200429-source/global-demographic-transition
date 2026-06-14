"""
02_clean_data.py
=================
Global Demographic Transition  |  STEP 2 of 5: Clean & Model the data

WHAT THIS SCRIPT DOES (in plain English)
----------------------------------------
Step 1 (01_download_data.py) pulled messy raw data from the World Bank API into
data/raw/. That raw data has two problems we must fix before any analysis:

  1. It mixes 217 REAL countries with ~79 "aggregates" (e.g. "Euro area",
     "Sub-Saharan Africa", "High income"). If we leave aggregates in, every chart
     we build will double-count people and give wrong totals.
  2. The text columns have stray whitespace, and we don't yet have a clean
     "star schema" (a separate country table + a separate facts table), which is
     the layout Power BI loves.

So this script turns the raw data into two tidy, analysis-ready tables:

  * dim_country        -> ONE row per country (the "dimension"): who/where it is.
  * fact_demographics  -> ONE row per country PER year (the "facts"): the numbers.

These two tables join on `country_code`. That country + facts split is the
classic "star schema" that professional analysts build for BI tools.

HOW TO RUN IT (from the WSL terminal):
  cd .../global-demographic-transition
  python scripts/02_clean_data.py
"""

# ---------------------------------------------------------------------------
# SECTION 0 — Imports and file paths
# ---------------------------------------------------------------------------
# pandas is the spreadsheet-in-code library. We always import it "as pd" by
# convention, so every analyst reading our code knows what `pd` means.
import pandas as pd

# `pathlib.Path` is the modern way to handle file/folder paths. It works the
# same on Windows, Mac, and Linux, so our code never breaks because of slashes.
from pathlib import Path

# __file__ is THIS script's location (.../scripts/02_clean_data.py).
# .resolve() makes it an absolute path; .parents[1] climbs two folders up
# (scripts -> project-1-global-demographics) to get the PROJECT ROOT.
# Building paths relative to the script means the code runs no matter what
# folder you launch it from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"          # where step 1 saved its output
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"  # where THIS step saves output

# Create data/processed/ if it doesn't exist yet. `parents=True` makes any
# missing parent folders too; `exist_ok=True` means "don't error if it's there".
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# SECTION 1 — Load the raw data
# ---------------------------------------------------------------------------
print("=" * 70)
print("STEP 2: CLEANING & MODELLING THE DATA")
print("=" * 70)

# read_csv reads a comma-separated file into a DataFrame (a table in memory).
countries_raw = pd.read_csv(RAW_DIR / "worldbank_countries_raw.csv")
indicators_raw = pd.read_csv(RAW_DIR / "worldbank_indicators_raw.csv")

print(f"\nLoaded raw country metadata : {countries_raw.shape[0]:>6} rows")
print(f"Loaded raw indicator data   : {indicators_raw.shape[0]:>6} rows")


# ---------------------------------------------------------------------------
# SECTION 2 — Build the COUNTRY DIMENSION table (dim_country)
# ---------------------------------------------------------------------------
# A "dimension" table describes the THINGS we measure (here: countries).
# We want ONE clean row per real country.

# 2a. The raw country file has an `is_aggregate` flag that is True for groupings
#     like "Euro area" and False for real countries. We keep only real countries.
#     The `~` means "NOT", so `~is_aggregate` = "rows that are NOT aggregates".
#     .copy() makes an independent copy so pandas doesn't warn us later about
#     editing a slice of the original table.
dim_country = countries_raw[~countries_raw["is_aggregate"]].copy()

# 2b. Strip stray whitespace from every text column. We saw the raw `region`
#     values had trailing spaces (e.g. "Sub-Saharan Africa "), which would make
#     Power BI treat "Sub-Saharan Africa" and "Sub-Saharan Africa " as two
#     different regions. .str.strip() trims spaces off both ends of each value.
text_columns = ["country_code", "country_name", "region", "income_group", "capital_city"]
for col in text_columns:
    dim_country[col] = dim_country[col].str.strip()

# 2c. Keep only the columns we actually need for analysis, in a sensible order,
#     and drop the now-redundant `is_aggregate` column (every row is False now).
dim_country = dim_country[
    ["country_code", "country_name", "region", "income_group", "capital_city"]
]

# 2d. Sort alphabetically by country name so the file is easy to read/scan.
#     reset_index(drop=True) renumbers the rows 0,1,2,... after sorting.
dim_country = dim_country.sort_values("country_name").reset_index(drop=True)

print(f"\nBuilt dim_country           : {dim_country.shape[0]:>6} real countries")


# ---------------------------------------------------------------------------
# SECTION 3 — Build the DEMOGRAPHICS FACT table (fact_demographics)
# ---------------------------------------------------------------------------
# A "fact" table holds the MEASUREMENTS. Here: one row per country per year,
# with each demographic indicator as a column. We must remove every aggregate
# so totals are correct.

# 3a. Get the set of valid (real) country codes from the dimension we just built.
valid_codes = set(dim_country["country_code"])

# 3b. Keep only indicator rows whose country_code is a REAL country.
#     This single filter removes BOTH kinds of aggregates at once:
#       - code-bearing aggregates (e.g. "EUU" Euro area) -> code not in the set
#       - income-group aggregates (e.g. "High income")   -> their code is blank,
#         so it can't be in the set either.
fact = indicators_raw[indicators_raw["country_code"].isin(valid_codes)].copy()

# 3c. Lock down data types. `year` should be a whole number (integer), not a
#     float like 1960.0, so it displays cleanly and joins reliably.
fact["year"] = fact["year"].astype(int)

# 3d. We don't need country_name in the fact table — it lives in dim_country and
#     we join to get it. Storing it in both places risks them disagreeing later.
#     This is a core star-schema principle: each fact joins out to its dimension.
fact = fact.drop(columns=["country_name"])

# 3e. Round the measurement columns to 2 decimals. The API returns long decimals
#     (e.g. 68.336473) that imply false precision; 2 dp is plenty for reporting.
#     We round every column EXCEPT the join keys and the raw population count.
measure_cols = [
    "population_growth_pct", "fertility_rate", "life_expectancy",
    "birth_rate", "death_rate", "pct_age_0_14", "pct_age_15_64",
    "pct_age_65_plus", "urban_population_pct", "dependency_ratio",
]
fact[measure_cols] = fact[measure_cols].round(2)

# 3f. population_total is a headcount of people, so it must be a whole number.
#     We use pandas' nullable integer type "Int64" (capital I) because a few
#     values are missing (NaN); ordinary int can't hold NaN, but Int64 can.
fact["population_total"] = fact["population_total"].round().astype("Int64")

# 3g. Sort by country then year — the natural reading order for a time series.
fact = fact.sort_values(["country_code", "year"]).reset_index(drop=True)

print(f"Built fact_demographics     : {fact.shape[0]:>6} country-year rows")


# ---------------------------------------------------------------------------
# SECTION 4 — Quality checks (the part that separates a pro from a beginner)
# ---------------------------------------------------------------------------
# Never trust your own cleaning blindly. We run automatic checks and PRINT the
# results so we (and anyone reviewing the project) can see the data is sound.
print("\n" + "-" * 70)
print("DATA QUALITY REPORT")
print("-" * 70)

# CHECK 1: No duplicate country-year combinations. Each country should appear
#          at most once per year. If this number is not 0, something is wrong.
dupes = fact.duplicated(subset=["country_code", "year"]).sum()
print(f"Duplicate country-year rows         : {dupes}  (must be 0)")

# CHECK 2: Every fact row's country_code exists in dim_country (referential
#          integrity). orphans should be 0 — no facts pointing at a missing country.
orphans = (~fact["country_code"].isin(valid_codes)).sum()
print(f"Fact rows with no matching country  : {orphans}  (must be 0)")

# CHECK 3: The three age-bucket percentages (0-14, 15-64, 65+) describe how the
#          population is split by age, so they should add up to ~100%. We allow a
#          tiny rounding tolerance. This catches a whole class of data errors.
age_sum = fact[["pct_age_0_14", "pct_age_15_64", "pct_age_65_plus"]].sum(axis=1)
# Only test rows where all three are present (dropna), then check they're near 100.
bad_age = ((age_sum.dropna() - 100).abs() > 1.0).sum()
print(f"Rows where age %s don't sum to ~100 : {bad_age}  (should be ~0)")

# CHECK 4: Missing-value summary per indicator, as a percentage. We REPORT this
#          rather than fake-filling the gaps. The gaps are small and mostly
#          structural (e.g. 1960 has no growth rate because there's no 1959 to
#          compare to). Power BI simply ignores blanks in its visuals.
print("\nMissing values per indicator (%):")
missing_pct = (fact[measure_cols + ["population_total"]].isna().mean() * 100).round(2)
for name, pct in missing_pct.sort_values(ascending=False).items():
    print(f"   {name:<24}: {pct:>5}%")

# A quick human-readable summary of coverage.
print(f"\nCountries covered : {fact['country_code'].nunique()}")
print(f"Years covered     : {fact['year'].min()} to {fact['year'].max()}")


# ---------------------------------------------------------------------------
# SECTION 5 — Save the cleaned tables
# ---------------------------------------------------------------------------
# index=False tells pandas NOT to write its internal row-number column, which
# would otherwise show up as a junk first column when Power BI imports the file.
dim_path = PROCESSED_DIR / "dim_country.csv"
fact_path = PROCESSED_DIR / "fact_demographics.csv"

dim_country.to_csv(dim_path, index=False)
fact.to_csv(fact_path, index=False)

print("\n" + "=" * 70)
print("DONE. Cleaned files written to data/processed/:")
print(f"   - {dim_path.name:<24} ({dim_country.shape[0]} rows)")
print(f"   - {fact_path.name:<24} ({fact.shape[0]} rows)")
print("=" * 70)
print("\nNEXT (Step 3): SQL + Python EDA on these clean tables.")
