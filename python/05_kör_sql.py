"""
05_kör_sql.py
=============
Motor som öppnar DuckDB-databasen och kör SQL-filerna i rätt ordning.
Alla SQL-filer ligger i sql/-mappen och körs sekventiellt.

Databasen sparas som en fil: ki_barometer.duckdb
"""

import duckdb
from pathlib import Path

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

DB_FIL  = Path("ki_barometer.duckdb")
SQL_DIR = Path("sql")

# Lista över SQL-filer i den ordning de ska köras
SQL_FILER = [
    "01_skapa_tabeller.sql",
    "02_bygg_analystabell.sql",
]

# ---------------------------------------------------------------------------
# Kör en SQL-fil och skriv ut resultatet
# ---------------------------------------------------------------------------

def kör_sql_fil(con: duckdb.DuckDBPyConnection, sql_fil: Path) -> None:
    print(f"\n{'=' * 60}")
    print(f"Kör: {sql_fil.name}")
    print(f"{'=' * 60}")

    sql = sql_fil.read_text(encoding="utf-8")

    # Kör SQL-filen och hämta eventuellt resultat från sista frågan
    resultat = con.execute(sql)

    # Om frågan returnerar rader, skriv ut dem
    try:
        df = resultat.df()
        if not df.empty:
            print(df.to_string(index=False))
    except Exception:
        pass

    print(f"✓ {sql_fil.name} klar.")

# ---------------------------------------------------------------------------
# Huvudprogram
# ---------------------------------------------------------------------------

def main():
    print(f"\nÖppnar databas: {DB_FIL}")
    con = duckdb.connect(str(DB_FIL))

    for filnamn in SQL_FILER:
        sql_fil = SQL_DIR / filnamn

        if not sql_fil.exists():
            print(f"✗ FEL: Filen {sql_fil} hittades inte – hoppar över.")
            continue

        kör_sql_fil(con, sql_fil)

    con.close()
    print(f"\n✓ Alla SQL-filer körda. Databasen sparad till: {DB_FIL}")

if __name__ == "__main__":
    main()
