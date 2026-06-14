-- ============================================================================
-- QUERY 1: The global fertility decline, decade by decade
-- ============================================================================
-- THE QUESTION (in plain English):
--   "On average across the world, how many children did a woman have in the
--    1960s, the 1970s, ... up to the 2020s? Is it going up or down?"
--
-- WHY IT MATTERS:
--   Falling fertility is the OPENING CHAPTER of the demographic transition.
--   When families have fewer children, populations eventually stop growing and
--   start ageing. This single trend sets up the whole story of the project.
--
-- HOW TO READ THE SQL BELOW (each line is explained with a -- comment):
--   Lines starting with "--" are COMMENTS. The database ignores them; they are
--   notes for humans. The actual command is the rest.
-- ----------------------------------------------------------------------------

SELECT
    -- Turn a year (e.g. 1974) into its decade (1970). In SQL, dividing two whole
    -- numbers throws away the remainder: 1974 / 10 = 197, then 197 * 10 = 1970.
    -- "AS decade" renames this calculated column to the friendly name "decade".
    (year / 10) * 10                     AS decade,

    -- AVG(...) is an AGGREGATE function: it averages a column across many rows.
    -- ROUND(x, 2) trims the answer to 2 decimal places so it's easy to read.
    ROUND(AVG(fertility_rate), 2)        AS avg_children_per_woman,

    -- COUNT(*) counts how many country-year rows fed into each decade's average.
    -- We include it as an honesty check: more rows = a more reliable average.
    COUNT(*)                             AS rows_used

-- FROM says which table to pull from. We only need the facts table here, because
-- fertility_rate lives there and we're averaging the whole world (no country
-- detail needed). No JOIN required for this one.
FROM        fact_demographics

-- WHERE filters rows BEFORE they are averaged. Some early/odd rows have no
-- fertility value (NULL); we exclude them so they don't distort the average.
-- "IS NOT NULL" means "only keep rows where this value actually exists".
WHERE       fertility_rate IS NOT NULL

-- GROUP BY is the heart of this query: it says "don't give me one big average -
-- instead make a SEPARATE group for each decade and average within each group".
-- So we get one row per decade.
GROUP BY    decade

-- ORDER BY sorts the final result. Here: oldest decade first, so you read the
-- decline top-to-bottom like a timeline.
ORDER BY    decade;
