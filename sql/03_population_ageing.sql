-- ============================================================================
-- QUERY 3: Is the world getting older?  --  consolidating GROUP BY + AVG
-- ============================================================================
-- THE QUESTION (in plain English):
--   "Decade by decade, what share of people are CHILDREN (aged 0-14) versus
--    ELDERLY (aged 65+)? Is the balance tipping from young to old?"
--
-- WHY IT MATTERS:
--   This is the THIRD chapter of the demographic transition. Fewer babies +
--   longer lives = an ageing population. Watching the "children %" fall while
--   the "elderly %" climbs is the clearest single picture of a society ageing,
--   and it drives huge real-world issues: pensions, healthcare, workforce size.
--
-- NO NEW SQL HERE - you already know every keyword. We're reusing GROUP BY on a
-- decade and AVG, just on two columns at once. Repetition is how it sticks.
-- ----------------------------------------------------------------------------

SELECT
    -- Same decade trick as Query 1: 2007 -> 2000, etc.
    (year / 10) * 10                      AS decade,

    -- Average share of the population that are children (0-14 years old).
    ROUND(AVG(pct_age_0_14), 1)           AS pct_children_0_14,

    -- Average share that are elderly (65 and older).
    ROUND(AVG(pct_age_65_plus), 1)        AS pct_elderly_65_plus,

    -- A handy derived column: how many MORE percentage points are children than
    -- elderly. As the world ages, this gap shrinks toward zero. We can do maths
    -- on columns right inside SELECT.
    ROUND(AVG(pct_age_0_14) - AVG(pct_age_65_plus), 1) AS child_minus_elderly_gap

FROM        fact_demographics

-- Skip rows where either age share is missing, so the averages stay clean.
WHERE       pct_age_0_14   IS NOT NULL
       AND  pct_age_65_plus IS NOT NULL

GROUP BY    decade
ORDER BY    decade;
