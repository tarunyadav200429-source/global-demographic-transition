-- ============================================================================
-- QUERY 4: Population growth by income group (recent years)  --  JOIN practice
-- ============================================================================
-- THE QUESTION (in plain English):
--   "In recent years (2015 onward), how fast is the population growing in
--    LOW-income vs HIGH-income countries? Who is driving world population growth?"
--
-- WHY IT MATTERS:
--   The demographic transition happens at different SPEEDS for different countries.
--   Rich countries finished it long ago and barely grow (some even shrink); poor
--   countries are still early in it and grow fast. This single split explains
--   where almost all future population growth on Earth will come from.
--
-- THE SKILL HERE: reusing the JOIN, this time to bring in `income_group` from the
--   country table. Same pattern as Query 2 - the more you see it, the more it sticks.
-- ----------------------------------------------------------------------------

SELECT
    -- income_group lives in the country (dimension) table, so we read it via "d".
    d.income_group                            AS income_group,

    -- Average yearly population growth %, across recent years, 2 decimals.
    ROUND(AVG(f.population_growth_pct), 2)    AS avg_annual_growth_pct,

    -- How many country-year rows fed each average (honesty check).
    COUNT(*)                                  AS rows_used

FROM        fact_demographics AS f

-- Glue each fact row to its country so we can see that country's income group.
JOIN        dim_country       AS d
       ON   f.country_code = d.country_code

-- Focus on recent years for a "today" picture, and drop missing growth values.
WHERE       f.year >= 2015
       AND  f.population_growth_pct IS NOT NULL

-- One average per income group.
GROUP BY    d.income_group

-- Fastest-growing groups at the top.
ORDER BY    avg_annual_growth_pct DESC;
