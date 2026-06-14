# The Global Demographic Transition

**Who's aging, who's booming, and where does India stand?**
A data-analytics study of 60+ years of demographic change across 200+ countries.

---

## 🎯 Objective & outcome

**Objective —** turn 60+ years of World Bank data into a clear, decision-ready read on
**which countries are aging vs. still growing**, who is aging *fastest*, and **where India
stands** — for a long-horizon (25-year) global investment fund.

**What this project does —** a fully reproducible analytics pipeline: pull 11 demographic
indicators for 200+ countries from the World Bank API → clean into a SQL **star-schema**
warehouse → answer the brief with **6 analytical SQL queries** → visualise in an interactive
**Power BI** dashboard.

**Did we achieve it? ✅ Yes.** The global transition is quantified (fertility roughly
**halved, 5.3 → 2.4 births per woman**), the youngest/oldest regions and **fastest-aging
countries** are ranked, and **India's demographic-dividend window** is pinpointed (working-age
share peaking *now*). Delivered end-to-end with documented methodology and honest caveats
(e.g. unweighted country averages).

---

## The brief (business context)

> A client managing a 25-year global infrastructure & equities fund needs to know
> which countries will have a **young, growing workforce** (good for labour supply
> and consumer markets) versus which face an **aging crisis** (rising healthcare and
> pension costs, shrinking workforce). They also want a clear read on **where India
> sits** in this window of opportunity.

As the analyst, the questions I set out to answer:

1. How has the world moved through the "demographic transition" since 1960?
2. Which regions / income groups are **youngest** and which are **oldest** today?
3. Which countries are aging **fastest**, and who still has a **demographic dividend**?
4. Where is **India** in this story — and how long is its workforce window open?

---

## Data source

| | |
|---|---|
| **Source** | [World Bank Open Data](https://data.worldbank.org/) (compiled from UN World Population Prospects & national statistics offices) |
| **Access** | Public REST API — no key required. Downloaded reproducibly via `scripts/01_download_data.py` |
| **Coverage** | 217 countries + 79 aggregates, years **1960–2023** |
| **Why this source** | Authoritative, government/UN-grade, free, transparent methodology. No fabricated or scraped data. |

### Data dictionary (the 11 indicators)

| Column | Meaning | Units |
|---|---|---|
| `population_total` | Total population | people |
| `population_growth_pct` | Annual population growth | % |
| `fertility_rate` | Births per woman over her lifetime | births |
| `life_expectancy` | Life expectancy at birth | years |
| `birth_rate` | Live births per 1,000 people | per 1,000 |
| `death_rate` | Deaths per 1,000 people | per 1,000 |
| `pct_age_0_14` | Share of population aged 0–14 (children) | % |
| `pct_age_15_64` | Share aged 15–64 (working-age) | % |
| `pct_age_65_plus` | Share aged 65+ (elderly) | % |
| `urban_population_pct` | Share living in urban areas | % |
| `dependency_ratio` | Dependents (under-15 + over-64) per 100 working-age | ratio |

**Key concepts a reviewer will expect me to know:**
- **Replacement-level fertility ≈ 2.1.** Below this, a population eventually shrinks without immigration.
- **Demographic dividend:** the growth boost a country gets while it has a large working-age share and few dependents.
- **Aging:** rising `pct_age_65_plus` and `dependency_ratio` → pressure on pensions & healthcare.

---

## Key findings

> All figures below are produced reproducibly by the SQL queries in `sql/`.
> "Average" means the average across countries unless stated otherwise.

**1. The world's families have nearly halved in size.** Average fertility fell from
**5.31 children per woman in the 1960s to 2.44 in the 2020s** — now close to the
~2.1 "replacement" level at which a population stops growing.
→ `sql/01_global_fertility_decline.sql`

**2. People live far longer — but how long depends heavily on where you're born.**
In 2023, average life expectancy ranged from **80.8 years in North America** down to
**64.6 in Sub-Saharan Africa** — a gap of roughly **16 years**.
→ `sql/02_life_expectancy_by_region.sql`

**3. The world is ageing.** The share of children (0–14) fell from **39.4% (1960s) to
26.1% (2020s)**, while the elderly share (65+) **doubled, from 5.1% to 10.0%**. The gap
between young and old is closing fast.
→ `sql/03_population_ageing.sql`

**4. Almost all future growth will come from the poorest countries.** Since 2015,
**low-income countries grew 2.42%/year** versus just **0.52–0.63% in richer ones** —
about **4–5× faster**. (At 2.4%/yr a population doubles in ~29 years.)
→ `sql/04_growth_by_income_group.sql`

**5. Some countries transformed within a single lifetime.** The biggest fertility
collapses 1960→2023 were led by **Iran (7.52 → 1.70)**, Kuwait, and Brunei — the
leaderboard is dominated by the Middle East/Gulf and Latin America.
→ `sql/05_fastest_transition_countries.sql`

**6. India's demographic dividend is peaking right now — and it's time-limited.**
India's fertility fell from **5.88 to 2.01** (now *below* replacement) and life
expectancy rose **+24 years** (46.5 → 70.3). Critically, its **working-age share
(15–64) is at an all-time high of 67.7%** — meaning ~2 in 3 Indians are of working
age today. But with fertility already below replacement and the elderly share rising
(3.5% → 6.6%), this growth window will begin to close in the coming decades.
**India's opportunity is now.**
→ `sql/06_india_story.sql`

---

## Project structure

```
.
├── README.md                       <- the brief, data dictionary & key findings
├── data/
│   ├── raw/                         <- untouched API downloads (never edited by hand)
│   │   ├── worldbank_indicators_raw.csv
│   │   └── worldbank_countries_raw.csv
│   └── processed/                   <- analysis-ready outputs
│       ├── dim_country.csv          <- country dimension (217 real countries)
│       ├── fact_demographics.csv    <- fact table (13,888 country-year rows)
│       └── demographics.db          <- SQLite database queried in the analysis
├── scripts/
│   ├── 01_download_data.py          <- pulls real data from the World Bank API
│   ├── 02_clean_data.py             <- cleans, removes aggregates, builds star schema
│   ├── 03_load_to_sqlite.py         <- loads the clean tables into a SQLite database
│   └── run_sql.py                   <- helper: runs any .sql file against the database
├── sql/                             <- the analysis, one question per file
│   ├── 01_global_fertility_decline.sql
│   ├── 02_life_expectancy_by_region.sql
│   ├── 03_population_ageing.sql
│   ├── 04_growth_by_income_group.sql
│   ├── 05_fastest_transition_countries.sql
│   └── 06_india_story.sql
└── powerbi/
    └── Global Demographics.pbix     <- interactive one-page dashboard (6 visuals + region slicer)
```

## How to reproduce

```bash
# one-time setup
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# build the data
python scripts/01_download_data.py      # raw data   -> data/raw/
python scripts/02_clean_data.py         # clean data -> data/processed/
python scripts/03_load_to_sqlite.py     # build the SQLite database

# then run any analysis query, e.g.:
python scripts/run_sql.py sql/06_india_story.sql
```

## Methodology notes (the honest details)
- **Aggregates removed.** The raw data mixes 217 real countries with 79 groupings
  ("Euro area", "High income", etc.). All analysis uses real countries only, so totals
  and averages aren't double-counted.
- **Missing values left as NULL, not invented.** Gaps are small (≤1.8%, mostly the
  structural 1960 growth rate) and are excluded from averages rather than fabricated.
- **Star schema.** Country attributes live in `dim_country`; measurements in
  `fact_demographics`; the two join on `country_code` — the layout BI tools expect.
- **Known caveat.** Cross-country averages weight every country equally (tiny and huge
  countries count the same). This is a valid "average country" view but differs from a
  population-weighted "average person" view.

## Progress log
- [x] **Step 1 — Data acquisition.** Reproducible download script; 17,024 indicator rows + country metadata.
- [x] **Step 2 — Data cleaning & modeling.** Aggregates removed, types fixed, star schema (217 countries × 13,888 facts); all quality checks pass.
- [x] **Step 3 — Analysis & insights.** SQLite database + 6 documented SQL queries → the six key findings above.
- [x] **Step 4 — Power BI dashboard.** Interactive one-page dashboard (`powerbi/Global Demographics.pbix`): the six findings as visuals, a DAX measure for the fastest-transition leaderboard, and a region slicer that cross-filters the whole page.
