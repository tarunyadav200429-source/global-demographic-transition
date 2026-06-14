"""
03_load_to_sqlite.py
====================
Global Demographic Transition  |  STEP 3a of 5: Build the database

WHAT THIS SCRIPT DOES (in plain English)
----------------------------------------
In Step 2 we produced two clean CSV files. CSVs are fine for storage, but real
analysts query their data with SQL, and SQL needs a DATABASE. So this script
loads our two clean tables into a single SQLite database file:

    data/processed/demographics.db

A few terms, in plain words:
  * DATABASE  - one file that holds many tables (think: one Excel workbook).
  * TABLE     - a grid of rows & columns (think: one sheet in that workbook).
  * SQLite    - a tiny, file-based database built right into Python. No server,
                no install, no password. The whole database is just one .db file
                you can copy around like any other file. Perfect for portfolios.

After this runs, we'll have a real database we can ask questions of in SQL,
exactly like you would on the job.

HOW TO RUN IT (from the WSL terminal):
  cd .../global-demographic-transition
  python scripts/03_load_to_sqlite.py
"""

# ---------------------------------------------------------------------------
# SECTION 0 — Imports and file paths
# ---------------------------------------------------------------------------
import pandas as pd          # to read the clean CSVs
import sqlite3               # Python's built-in database engine (nothing to install)
from pathlib import Path     # safe, cross-platform file paths

# Same path trick as before: find the project root relative to this script,
# so the code runs no matter which folder you launch it from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# The two clean inputs we built in Step 2...
DIM_CSV = PROCESSED_DIR / "dim_country.csv"
FACT_CSV = PROCESSED_DIR / "fact_demographics.csv"

# ...and the database file we are about to create.
DB_PATH = PROCESSED_DIR / "demographics.db"


# ---------------------------------------------------------------------------
# SECTION 1 — Read the clean CSVs back into memory
# ---------------------------------------------------------------------------
print("=" * 70)
print("STEP 3a: BUILDING THE SQLITE DATABASE")
print("=" * 70)

dim_country = pd.read_csv(DIM_CSV)
fact_demographics = pd.read_csv(FACT_CSV)

print(f"\nRead dim_country.csv        : {dim_country.shape[0]:>6} rows")
print(f"Read fact_demographics.csv  : {fact_demographics.shape[0]:>6} rows")


# ---------------------------------------------------------------------------
# SECTION 2 — Connect to the database
# ---------------------------------------------------------------------------
# sqlite3.connect(path) OPENS the database file. If the file doesn't exist yet,
# SQLite creates it for us. The returned `conn` (connection) is our live link to
# the database — we send data and queries through it.
#
# If you re-run this script, we want a clean rebuild rather than stale leftovers,
# so we delete any existing .db file first. (unlink = delete the file.)
if DB_PATH.exists():
    DB_PATH.unlink()
    print("\nRemoved old database (fresh rebuild).")

conn = sqlite3.connect(DB_PATH)


# ---------------------------------------------------------------------------
# SECTION 3 — Write each DataFrame into the database as a table
# ---------------------------------------------------------------------------
# pandas can write a DataFrame straight into a database table with .to_sql().
#   - first argument  = the TABLE name we want inside the database
#   - con=conn        = which database to write into
#   - if_exists="replace" = if a table of that name exists, overwrite it
#   - index=False     = don't write pandas' internal row-number column
dim_country.to_sql("dim_country", con=conn, if_exists="replace", index=False)
fact_demographics.to_sql("fact_demographics", con=conn, if_exists="replace", index=False)

print("\nWrote 2 tables into the database:")
print("   - dim_country")
print("   - fact_demographics")


# ---------------------------------------------------------------------------
# SECTION 4 — Verify the database by running a tiny test query
# ---------------------------------------------------------------------------
# Let's prove the database works by asking it a question IN SQL. Reading the
# result back with pandas keeps it tidy. This is also your first look at SQL:
#
#   SELECT  -> "give me these columns"
#   COUNT(*)-> "count the rows"
#   FROM    -> "from this table"
#
# So "SELECT COUNT(*) FROM dim_country" means: "how many rows in dim_country?"
print("\n" + "-" * 70)
print("VERIFICATION (running test queries through SQL)")
print("-" * 70)

n_countries = pd.read_sql("SELECT COUNT(*) AS n FROM dim_country", conn)["n"][0]
n_facts = pd.read_sql("SELECT COUNT(*) AS n FROM fact_demographics", conn)["n"][0]
print(f"dim_country row count       : {n_countries}")
print(f"fact_demographics row count : {n_facts}")

# A slightly richer query: the 5 most populous countries in the latest year.
# Don't worry about every keyword yet — we'll learn these properly in step 3b.
# In plain English: "join the facts to their country names, keep only year 2023,
# sort by population biggest-first, and show the top 5."
preview = pd.read_sql(
    """
    SELECT  d.country_name,
            f.year,
            f.population_total
    FROM        fact_demographics AS f
    JOIN        dim_country        AS d  ON f.country_code = d.country_code
    WHERE       f.year = 2023
    ORDER BY    f.population_total DESC
    LIMIT 5
    """,
    conn,
)
print("\nSanity preview — 5 most populous countries in 2023:")
print(preview.to_string(index=False))


# ---------------------------------------------------------------------------
# SECTION 5 — Close the connection
# ---------------------------------------------------------------------------
# Always close the connection when done. It flushes everything safely to disk
# and releases the file. (commit() saves pending changes; close() ends the link.)
conn.commit()
conn.close()

print("\n" + "=" * 70)
print(f"DONE. Database ready at: data/processed/{DB_PATH.name}")
print("=" * 70)
print("\nNEXT (Step 3b): write analytical SQL queries to uncover the story.")
