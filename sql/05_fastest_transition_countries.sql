-- ============================================================================
-- QUERY 5: Which countries transformed fastest?  --  learning the CTE (WITH)
-- ============================================================================
-- THE QUESTION (in plain English):
--   "For each country, how much did fertility FALL from 1960 to 2023? Which
--    countries saw the biggest collapse in family size?"
--
-- WHY IT MATTERS:
--   The demographic transition isn't uniform - some countries raced through it in
--   one lifetime. Ranking the biggest fertility drops surfaces the most dramatic
--   social transformations on Earth (often East Asia & the Gulf). Great "wow"
--   slide for a dashboard.
--
-- THE NEW IDEA: a CTE - "Common Table Expression", written WITH name AS (...).
--   A CTE is a TEMPORARY, named result you build first and then use below, like
--   defining a variable before using it. It keeps complex queries readable by
--   breaking them into clear steps instead of one giant tangled query.
--   Here we build two mini-tables - fertility in 1960, and fertility in 2023 -
--   then join them to compare.
-- ----------------------------------------------------------------------------

WITH fertility_1960 AS (
    -- STEP 1: one row per country = its fertility rate in 1960.
    SELECT  country_code,
            fertility_rate AS fr_1960
    FROM    fact_demographics
    WHERE   year = 1960
      AND   fertility_rate IS NOT NULL
),

fertility_2023 AS (
    -- STEP 2: one row per country = its fertility rate in 2023.
    SELECT  country_code,
            fertility_rate AS fr_2023
    FROM    fact_demographics
    WHERE   year = 2023
      AND   fertility_rate IS NOT NULL
)

-- STEP 3: now join those two mini-tables (and the country names) and compute the
-- drop. Because the CTEs above each have one row per country, joining them on
-- country_code lines up "1960 value" next to "2023 value" for the same country.
SELECT
    d.country_name                          AS country,
    d.region                                AS region,
    a.fr_1960                               AS fertility_1960,
    b.fr_2023                               AS fertility_2023,
    -- The headline number: how many fewer children per woman, 1960 -> 2023.
    ROUND(a.fr_1960 - b.fr_2023, 2)         AS fertility_drop

FROM        fertility_1960 AS a
JOIN        fertility_2023 AS b  ON a.country_code = b.country_code
JOIN        dim_country     AS d ON a.country_code = d.country_code

-- Biggest collapse first...
ORDER BY    fertility_drop DESC

-- ...and show only the top 10 so the result is a clean leaderboard.
LIMIT 10;
