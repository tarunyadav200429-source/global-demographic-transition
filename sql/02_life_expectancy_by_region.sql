-- ============================================================================
-- QUERY 2: Life expectancy by region (latest year, 2023)  --  learning the JOIN
-- ============================================================================
-- THE QUESTION (in plain English):
--   "In the most recent year, how long does the average person live in each
--    region of the world? Which regions live longest, which shortest?"
--
-- WHY IT MATTERS:
--   Rising life expectancy is the SECOND chapter of the demographic transition
--   (first fewer children, then longer lives). Showing it BY REGION reveals how
--   unequal the world still is - a powerful, honest insight for the dashboard.
--
-- THE NEW IDEA HERE: the JOIN
--   life_expectancy lives in the FACTS table (fact_demographics).
--   region          lives in the COUNTRY table (dim_country).
--   To use both in one query, we must JOIN the two tables - i.e. glue each fact
--   row to its matching country row. They match on the shared column country_code.
-- ----------------------------------------------------------------------------

SELECT
    -- We can now use columns from BOTH tables. To avoid confusion about which
    -- table a column came from, we prefix it with the table's short nickname
    -- (its "alias", defined below): d = dim_country, f = fact_demographics.
    d.region                              AS region,

    -- Average life expectancy across all countries in that region, 1 decimal.
    ROUND(AVG(f.life_expectancy), 1)      AS avg_life_expectancy,

    -- How many countries went into each region's average (honesty check).
    COUNT(*)                              AS countries_counted

FROM        fact_demographics AS f          -- the facts table, nicknamed "f"

-- JOIN ... ON is the new line. It says: for each row in f, find the row in
-- dim_country (nicknamed "d") that has the SAME country_code, and attach its
-- columns. Now each fact row also "knows" its region, income group, etc.
JOIN        dim_country       AS d
       ON   f.country_code = d.country_code

-- Keep only the most recent year so we get a clean current snapshot.
WHERE       f.year = 2023
       AND  f.life_expectancy IS NOT NULL   -- ignore any missing values

-- One average per region.
GROUP BY    d.region

-- Longest-living regions at the top.
ORDER BY    avg_life_expectancy DESC;
