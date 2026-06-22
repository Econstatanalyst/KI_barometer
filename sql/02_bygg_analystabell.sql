-- =============================================================
-- 02_bygg_analystabell.sql
-- =============================================================
-- Bygger en bred analystabell genom att:
-- 1. Slå ihop de tre råtabellerna med JOIN på period
-- 2. Skapa LAG-variabler för barometern (3, 6, 12 månader)
-- 3. Klassificera månader som krisperioder med CASE WHEN
-- =============================================================


DROP TABLE IF EXISTS analystabell;

CREATE TABLE analystabell AS

WITH bas AS (
    -- Steg 1: JOIN de tre tabellerna på period
    SELECT
        k.datum,
        k.period,
        k.barometerindikator,
        s.kpi_arsforandring_pct,
        s.kpi_skuggindex_2020_100,
        r.styranta_pct

    FROM ki_barometer k
    LEFT JOIN scb_kpi          s ON k.period = s.period
    LEFT JOIN riksbanken_styranta r ON k.period = r.period
),

med_lag AS (
    -- Steg 2: Skapa LAG-variabler för barometern
    -- LAG(n) hämtar barometerns värde n månader tidigare
    -- Det gör att vi kan testa: korrelerar barometern från X månader
    -- sedan med inflationen idag?
    SELECT
        *,

        -- Barometern 3 månader tidigare
        LAG(barometerindikator, 3)  OVER (ORDER BY datum) AS barometer_lag3,

        -- Barometern 6 månader tidigare
        LAG(barometerindikator, 6)  OVER (ORDER BY datum) AS barometer_lag6,

        -- Barometern 12 månader tidigare
        LAG(barometerindikator, 12) OVER (ORDER BY datum) AS barometer_lag12

    FROM bas
)

-- Steg 3: Klassificera krisperioder med CASE WHEN
SELECT
    *,
    CASE
        WHEN period BETWEEN '2001M03' AND '2002M12' THEN 'IT-kris'
        WHEN period BETWEEN '2008M09' AND '2009M06' THEN 'Finanskris'
        WHEN period BETWEEN '2021M01' AND '2023M12' THEN 'Energikris'
        ELSE 'Lugn period'
    END AS krisperiod

FROM med_lag
ORDER BY datum;


-- -------------------------------------------------------------
-- Snabbkontroll: visa de första och sista raderna
-- -------------------------------------------------------------

SELECT
    period,
    barometerindikator,
    kpi_arsforandring_pct,
    styranta_pct,
    barometer_lag3,
    barometer_lag6,
    barometer_lag12,
    krisperiod
FROM analystabell
LIMIT 15;
