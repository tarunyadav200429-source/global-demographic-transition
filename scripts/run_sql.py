"""
run_sql.py  -  a tiny helper to run a .sql file against our database
====================================================================
Global Demographic Transition  |  STEP 3b helper

WHAT THIS IS
------------
Instead of burying SQL inside Python, real analysts keep each query in its own
.sql file (clean, reusable, easy for a reviewer to read). This little helper
runs ANY of those .sql files against our demographics.db and prints the result
as a neat table.

HOW TO USE IT:
  python scripts/run_sql.py \
      sql/01_global_fertility_decline.sql

In words: "python, run run_sql.py, and the file to run is <that .sql file>".
The part after run_sql.py is called an ARGUMENT - it tells the script WHICH
query file you want to run.
"""

import sys                   # lets us read the argument you typed on the command line
import sqlite3               # the database engine
import pandas as pd          # to run the query and print it nicely
from pathlib import Path

# Locate the database relative to this script (so it works from any folder).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "processed" / "demographics.db"

# sys.argv is the list of words you typed. sys.argv[0] is the script name itself;
# sys.argv[1] is the FIRST thing after it - the .sql file you want to run.
# If you forget to pass a file, print a friendly reminder instead of crashing.
if len(sys.argv) < 2:
    print("Please tell me which .sql file to run, e.g.:")
    print("  python scripts/run_sql.py \\")
    print("      sql/01_global_fertility_decline.sql")
    sys.exit(1)   # stop the script with an error code

sql_file = Path(sys.argv[1])

# .read_text() reads the whole .sql file into a string we can hand to the database.
query = sql_file.read_text()

# Open the database, run the query, close up.
conn = sqlite3.connect(DB_PATH)
result = pd.read_sql(query, conn)
conn.close()

# Print a small header so we know which query produced the table, then the result.
print("=" * 70)
print(f"QUERY: {sql_file.name}")
print("=" * 70)
print(result.to_string(index=False))   # index=False hides pandas' row numbers
print(f"\n({len(result)} rows returned)")
