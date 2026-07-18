# Förutspår Konjunkturbarometern inflationen?

En analys av hur väl Konjunkturinstitutets (KI) barometerindikator samvarierar med den faktiska KPI-inflationen i Sverige 1996–2024, med särskilt fokus på om sambandet förändras under ekonomiska kriser.

## Frågeställning

> Hur väl har Konjunkturinstitutets barometerindikator förutspått faktisk KPI-inflation i Sverige 1996–2024, och försämrades träffsäkerheten under inflationschocker som IT-krisen 2001, finanskrisen 2008–2009 och energiprisuppgången 2021–2023?

## Huvudresultat

Barometerindikatorn har en statistiskt säkerställd, positiv samvariation med KPI-inflationen på tolv månaders sikt (Spearmans rho = 0,397, p < 0,001 för hela perioden). Tvärtemot den ursprungliga hypotesen var sambandet **starkast under kriser** – rho = 0,823 under finanskrisen och rho = 0,815 under energikrisen, jämfört med 0,418 under lugna perioder. Barometern fungerar därmed som en ledande indikator för inflationsutvecklingen på ungefär ett års sikt, med störst signalvärde vid stora konjunkturomslag.

## Metod och verktyg

Projektet går igenom hela analyskedjan:

1. **Datainsamling (Python)** – programmatisk hämtning via API från KI, SCB och Riksbanken
2. **Validering (Python)** – kontroll mot kända referensvärden från officiella källor
3. **Databearbetning (SQL / DuckDB)** – sammanfogning med JOIN, fördröjda variabler med LAG, krisklassificering med CASE WHEN
4. **Analys (R)** – explorativ Pearson-korrelation, fördelningsanalys och formell prövning med Spearmans rangkorrelation
5. **Rapport** – sammanställning av frågeställning, metod, resultat och slutsats

## Datakällor

| Källa | Variabler | Hämtning |
|---|---|---|
| Konjunkturinstitutet | Barometerindikatorn (månadsvis) | PxWeb-API |
| SCB | KPI årsförändring och skuggindex | PxWeb-API |
| Riksbanken | Styrränta (månadsgenomsnitt) | REST-API |

## Mappstruktur

```
KI_barometer/
├── python/                     # Datainsamling och validering
│   ├── 01_hamta_ki_data.py
│   ├── 02_hamta_scb_kpi.py
│   ├── 03_hamta_riksbanken_styranta.py
│   ├── 04_validera_data.py
│   └── 05_kor_sql.py           # Motor som kör SQL-filerna
├── sql/                        # Databasuppbyggnad
│   ├── 01_skapa_tabeller.sql
│   └── 02_bygg_analystabell.sql
├── r/                          # Analys och grafer
│   └── 01_explorativ_analys.R
├── data/raw/                   # Rådata (CSV)
├── Rapport_KI_barometerindikator.pdf
└── ki_barometer.duckdb         # Databasen
```

## Så kör du projektet

Kräver Python (`requests`, `pandas`, `matplotlib`, `duckdb`) och R (`duckdb`, `dplyr`, `ggplot2`, `tidyr`, `gt`).

```bash
# 1. Hämta data
python python/01_hamta_ki_data.py
python python/02_hamta_scb_kpi.py
python python/03_hamta_riksbanken_styranta.py

# 2. Validera
python python/04_validera_data.py

# 3. Bygg databasen
python python/05_kor_sql.py

# 4. Kör analysen i R (t.ex. i RStudio)
#    r/01_explorativ_analys.R
```

## Metodval i korthet

Fördelningsanalysen visade att KPI-inflationen är kraftigt högerskev, driven av energikrisens extremvärden, och att sambandet inte är linjärt. Den formella prövningen genomfördes därför med Spearmans rangkorrelation, som är robust mot extremvärden och endast förutsätter ett monotont samband. Krisperioderna definierades utifrån kända historiska händelser – inte utifrån nivåer på de analyserade variablerna – för att undvika cirkularitet.

## Begränsningar

Antalet observationer i krisperioderna är litet (10–36 månader), vilket gör delperiodernas skattningar osäkra. Månadsdata är autokorrelerad, så p-värden bör tolkas med försiktighet. KI:s tjänstesektordata 1996–2002 är delvis skattad från kvartalsserier.

## Källor

- Konjunkturinstitutet: Metodbok för Konjunkturbarometern samt statistikdatabasen (statistik.konj.se)
- Statistiska centralbyrån: Konsumentprisindex (statistikdatabasen.scb.se)
- Sveriges riksbank: Styrräntan (api.riksbank.se)
