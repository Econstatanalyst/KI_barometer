"""
01_hamta_ki_data.py
===================
Hämtar Konjunkturinstitutets barometerindikator (månadsvis, 1996M01–2024M12)
via KI:s PxWeb-API och sparar rådata som CSV i data/raw/.

Källa: http://statistik.konj.se/PXWeb/pxweb/sv/KonjBar/KonjBar__indikatorer/Indikatorm.px
"""

import requests
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

API_URL = (
    "https://statistik.konj.se:443/PxWeb/api/v1/sv/KonjBar/indikatorer/Indikatorm.px"
)

# Perioder: 1996M01 till 2024M12
START_AR = 1996
SLUT_AR  = 2024

OUTPUT_DIR = Path("data/raw")
OUTPUT_FIL = OUTPUT_DIR / "ki_barometer_1996_2024.csv"

# ---------------------------------------------------------------------------
# Bygg lista med alla månadsperioder (1996M01, 1996M02, ..., 2024M12)
# ---------------------------------------------------------------------------

def bygg_perioder(start_ar: int, slut_ar: int) -> list[str]:
    perioder = []
    for ar in range(start_ar, slut_ar + 1):
        for manad in range(1, 13):
            perioder.append(f"{ar}M{manad:02d}")
    return perioder

# ---------------------------------------------------------------------------
# Bygg JSON-fråga till PxWeb API
# PxWeb förväntar sig en POST med en "query"-lista och "response"-format.
# Vi hämtar bara "Barometerindikatorn" – den variabel vi behöver.
# ---------------------------------------------------------------------------

def bygg_fraga(perioder: list[str]) -> dict:
    return {
        "query": [
            {
                "code": "Indikator",
                "selection": {
                    "filter": "item",
                    "values": ["KIFI"]
                }
            },
            {
                "code": "Period",
                "selection": {
                    "filter": "item",
                    "values": perioder
                }
            }
        ],
        "response": {
            "format": "json"
        }
    }

# ---------------------------------------------------------------------------
# Hämta data och konvertera till DataFrame
# ---------------------------------------------------------------------------

def hamta_data(api_url: str, fraga: dict) -> pd.DataFrame:
    print("Skickar förfrågan till KI:s API...")
    svar = requests.post(api_url, json=fraga, timeout=30)
    svar.raise_for_status()  # Kasta fel om statuskod != 200

    json_data = svar.json()

    # PxWeb returnerar värden i "data"-listan, varje post har "key" och "values"
    # key[0] = indikator (vi har bara en), key[1] = period
    rader = []
    for post in json_data["data"]:
        period   = post["key"][1]          # t.ex. "1996M01"
        varde    = post["values"][0]       # t.ex. "97.3"

        rader.append({
            "period":            period,
            "barometerindikator": float(varde) if varde != ".." else None
        })

    df = pd.DataFrame(rader)

    # Konvertera period till datetime för enklare hantering i R och SQL
    df["datum"] = pd.to_datetime(
        df["period"].str.replace("M", "-") + "-01",
        format="%Y-%m-%d"
    )

    # Sortera kronologiskt
    df = df.sort_values("datum").reset_index(drop=True)

    return df[["datum", "period", "barometerindikator"]]

# ---------------------------------------------------------------------------
# Validering – enkel kontroll av att datan ser rimlig ut
# ---------------------------------------------------------------------------

def validera(df: pd.DataFrame) -> None:
    print(f"\n--- Validering ---")
    print(f"Antal rader:      {len(df)}")
    print(f"Första period:    {df['period'].iloc[0]}")
    print(f"Sista period:     {df['period'].iloc[-1]}")
    print(f"Saknade värden:   {df['barometerindikator'].isna().sum()}")
    print(f"Min:              {df['barometerindikator'].min():.1f}")
    print(f"Max:              {df['barometerindikator'].max():.1f}")
    print(f"Medelvärde:       {df['barometerindikator'].mean():.1f}  (förväntat ~100)")
    print(f"Std-avvikelse:    {df['barometerindikator'].std():.1f}   (förväntat ~10)")
    print(f"------------------\n")

    # Kontrollera förväntat antal rader (12 månader × antal år)
    forvantat = (SLUT_AR - START_AR + 1) * 12
    if len(df) != forvantat:
        print(f"⚠ Varning: Förväntade {forvantat} rader men fick {len(df)}.")
    else:
        print(f"✓ Radantal stämmer ({forvantat} månader).")

# ---------------------------------------------------------------------------
# Huvudprogram
# ---------------------------------------------------------------------------

def main():
    # Skapa output-mapp om den inte finns
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Bygg perioder och API-fråga
    perioder = bygg_perioder(START_AR, SLUT_AR)
    fraga    = bygg_fraga(perioder)

    # Hämta och bearbeta data
    df = hamta_data(API_URL, fraga)

    # Validera
    validera(df)

    # Spara som CSV
    df.to_csv(OUTPUT_FIL, index=False, encoding="utf-8-sig")
    print(f"✓ Data sparad till: {OUTPUT_FIL}")
    print("\nFörsta 5 raderna:")
    print(df.head().to_string(index=False))

if __name__ == "__main__":
    main()
