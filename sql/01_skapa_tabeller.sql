-- =============================================================
-- 01_skapa_tabeller.sql
-- =============================================================
-- Skapar tre råtabeller i DuckDB och laddar in CSV-filerna.
-- Kör detta skript en gång för att initialisera databasen.
-- =============================================================


-- -------------------------------------------------------------
-- Tabell 1: KI:s barometerindikator
-- Källa: statistik.konj.se
-- -------------------------------------------------------------

DROP TABLE IF EXISTS ki_barometer;

CREATE TABLE ki_barometer (
    datum       DATE,
    period      VARCHAR,
    barometerindikator DOUBLE
);

INSERT INTO ki_barometer
SELECT
    datum::DATE,
    period,
    barometerindikator
FROM read_csv_auto('data/raw/ki_barometer_1996_2024.csv');


-- -------------------------------------------------------------
-- Tabell 2: SCB:s KPI
-- Källa: statistikdatabasen.scb.se
-- -------------------------------------------------------------

DROP TABLE IF EXISTS scb_kpi;

CREATE TABLE scb_kpi (
    datum                   DATE,
    period                  VARCHAR,
    kpi_arsforandring_pct   DOUBLE,
    kpi_skuggindex_2020_100 DOUBLE
);

INSERT INTO scb_kpi
SELECT
    datum::DATE,
    period,
    kpi_arsforandring_pct,
    kpi_skuggindex_2020_100
FROM read_csv_auto('data/raw/scb_kpi_1996_2024.csv');


-- -------------------------------------------------------------
-- Tabell 3: Riksbankens styrränta
-- Källa: riksbank.se
-- -------------------------------------------------------------

DROP TABLE IF EXISTS riksbanken_styranta;

CREATE TABLE riksbanken_styranta (
    datum        DATE,
    period       VARCHAR,
    styranta_pct DOUBLE
);

INSERT INTO riksbanken_styranta
SELECT
    datum::DATE,
    period,
    styranta_pct
FROM read_csv_auto('data/raw/riksbanken_styranta_1996_2024.csv');


-- -------------------------------------------------------------
-- Snabbkontroll: räkna rader i varje tabell
-- -------------------------------------------------------------

SELECT 'ki_barometer'       AS tabell, COUNT(*) AS antal_rader FROM ki_barometer
UNION ALL
SELECT 'scb_kpi'            AS tabell, COUNT(*) AS antal_rader FROM scb_kpi
UNION ALL
SELECT 'riksbanken_styranta' AS tabell, COUNT(*) AS antal_rader FROM riksbanken_styranta;
