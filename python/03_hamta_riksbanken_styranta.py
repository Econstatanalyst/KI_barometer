"""
03_hamta_riksbanken_styranta.py
================================
Hämtar Riksbankens styrränta (dagliga värden) 1996-01-01–2024-12-31
via Riksbankens REST API, beräknar månadsgenomsnitt och sparar
rådata som CSV i data/raw/.

Källa: https://api.riksbank.se/swea/v1/
Serie:  SECBREPOEFF = styrräntan (f.d. reporäntan)
"""

import requests
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

API_URL = (
    "https://api.riksbank.se/swea/v1/Observations/SECBREPOEFF/1996-01-01/2024-12-31"
)

OUTPUT_DIR = Path("data/raw")
OUTPUT_FIL = OUTPUT_DIR / "riksbanken_styranta_1996_2024.csv"

# ---------------------------------------------------------------------------
# Hämta dagliga värden
# ---------------------------------------------------------------------------

def hamta_data(api_url: str) -> pd.DataFrame:
    print("Skickar förfrågan till Riksbankens API...")
    svar = requests.get(api_url, timeout=30)
    svar.raise_for_status()

    json_data = svar.json()

    rader = []
    for post in json_data:
        datum = post["date"]
        varde = post["value"]
        rader.append({
            "datum":        pd.to_datetime(datum),
            "styranta_pct": float(varde) if varde is not None else None
        })

    df = pd.DataFrame(rader)
    df = df.sort_values("datum").reset_index(drop=True)

    print(f"Hämtade {len(df)} dagliga observationer.")
    return df

# ---------------------------------------------------------------------------
# Beräkna månadsgenomsnitt
# ---------------------------------------------------------------------------

def berakna_manadsgenomsnitt(df: pd.DataFrame) -> pd.DataFrame:
    print("Beräknar månadsgenomsnitt...")

    # Gruppera på år och månad, beräkna medelvärde
    df["ar"]    = df["datum"].dt.year
    df["manad"] = df["datum"].dt.month

    manad_df = (
        df.groupby(["ar", "manad"])["styranta_pct"]
        .mean()
        .reset_index()
    )

    # Bygg datum (första i månaden) och period-kolumn
    manad_df["datum"] = pd.to_datetime(
        manad_df["ar"].astype(str) + "-" +
        manad_df["manad"].astype(str).str.zfill(2) + "-01"
    )

    manad_df["period"] = manad_df["datum"].dt.strftime("%YM%m")

    manad_df = manad_df.sort_values("datum").reset_index(drop=True)

    return manad_df[["datum", "period", "styranta_pct"]]

# ---------------------------------------------------------------------------
# Validering
# ---------------------------------------------------------------------------

def validera(df: pd.DataFrame) -> None:
    print(f"\n--- Validering ---")
    print(f"Antal rader:       {len(df)}")
    print(f"Första period:     {df['period'].iloc[0]}")
    print(f"Sista period:      {df['period'].iloc[-1]}")
    print(f"Saknade värden:    {df['styranta_pct'].isna().sum()}")
    print(f"Min styrränta:     {df['styranta_pct'].min():.2f}%")
    print(f"Max styrränta:     {df['styranta_pct'].max():.2f}%")
    print(f"Medel styrränta:   {df['styranta_pct'].mean():.2f}%")
    print(f"------------------\n")

    forvantat = (2024 - 1996 + 1) * 12
    if len(df) != forvantat:
        print(f"Varning: Förväntade {forvantat} rader men fick {len(df)}.")
    else:
        print(f"Radantal stämmer ({forvantat} månader).")

# ---------------------------------------------------------------------------
# Huvudprogram
# ---------------------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_dag    = hamta_data(API_URL)
    df_manad  = berakna_manadsgenomsnitt(df_dag)

    validera(df_manad)

    df_manad.to_csv(OUTPUT_FIL, index=False, encoding="utf-8-sig")
    print(f"Data sparad till: {OUTPUT_FIL}")
    print("\nFörsta 5 raderna:")
    print(df_manad.head().to_string(index=False))
    print("\nSista 5 raderna:")
    print(df_manad.tail().to_string(index=False))

if __name__ == "__main__":
    main()
