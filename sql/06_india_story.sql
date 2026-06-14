-- ============================================================================
-- QUERY 6: Where does INDIA sit in the demographic transition?
-- ============================================================================
-- THE QUESTION (in plain English):
--   "Decade by decade, how have India's family size, lifespan, and - most
--    importantly - its WORKING-AGE SHARE changed? Is India's 'demographic
--    dividend' window still open?"
--
-- WHY IT MATTERS:
--   This is the headline of the whole project (see the brief in README). India is
--   now the world's most populous country. The share of people aged 15-64 (the
--   working age) is its economic engine: a big, growing working-age share = the
--   "demographic dividend" that can power decades of growth. We want to SEE that
--   window open over time.
--
-- NO NEW SQL - this reuses the decade GROUP BY from Query 1/3, focused on one
--   country. The skill on show is ANSWERING A BUSINESS QUESTION, not new syntax.
-- ----------------------------------------------------------------------------

SELECT
    (f.year / 10) * 10                        AS decade,

    -- Family size: expected to fall a lot over these decades.
    ROUND(AVG(f.fertility_rate), 2)           AS fertility_rate,

    -- Lifespan: expected to rise.
    ROUND(AVG(f.life_expectancy), 1)          AS life_expectancy,

    -- THE KEY METRIC: % of population that is working age (15-64). When this is
    -- large and rising, the country has a "demographic dividend".
    ROUND(AVG(f.pct_age_15_64), 1)            AS pct_working_age,

    -- The elderly share, to watch when the window starts to close.
    ROUND(AVG(f.pct_age_65_plus), 1)          AS pct_elderly,

    -- India's population in that decade (averaged), in MILLIONS for readability.
    -- We divide by 1,000,000 and round to whole millions.
    ROUND(AVG(f.population_total) / 1000000.0) AS population_millions

FROM        fact_demographics AS f
JOIN        dim_country       AS d  ON f.country_code = d.country_code

-- Filter to just India. (Its World Bank code is 'IND'.)
WHERE       d.country_name = 'India'

GROUP BY    decade
ORDER BY    decade;
