"""
02_hamta_scb_kpi.py
===================
Hämtar KPI (totalt) månadsvis 1996M01–2024M12 från SCB:s PxWeb-API
och sparar rådata som CSV i data/raw/.

Källa: https://api.scb.se/OV0104/v1/doris/sv/ssd/START/PR/PR0101/PR0101A/KPI2020M
"""

import requests
import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

API_URL = (
    "https://api.scb.se/OV0104/v1/doris/sv/ssd/START/PR/PR0101/PR0101A/KPI2020M"
)

START_AR = 1996
SLUT_AR  = 2024

OUTPUT_DIR = Path("data/raw")
OUTPUT_FIL = OUTPUT_DIR / "scb_kpi_1996_2024.csv"

# ---------------------------------------------------------------------------
# Bygg lista med månadsperioder
# ---------------------------------------------------------------------------

def bygg_perioder(start_ar: int, slut_ar: int) -> list[str]:
    perioder = []
    for ar in range(start_ar, slut_ar + 1):
        for manad in range(1, 13):
            perioder.append(f"{ar}M{manad:02d}")
    return perioder

# ---------------------------------------------------------------------------
# Bygg JSON-fråga för en variabel i taget
# ---------------------------------------------------------------------------

def bygg_fraga(perioder: list[str], contents_code: str) -> dict:
    return {
        "query": [
            {
                "code": "ContentsCode",
                "selection": {
                    "filter": "item",
                    "values": [contents_code]
                }
            },
            {
                "code": "Tid",
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
# Hämta en variabel och returnera som Series med period som index
# ---------------------------------------------------------------------------

def hamta_variabel(api_url: str, perioder: list[str], contents_code: str, kolumnnamn: str) -> pd.Series:
    print(f"Hämtar {kolumnnamn}...")
    fraga = bygg_fraga(perioder, contents_code)
    svar = requests.post(api_url, json=fraga, timeout=30)
    svar.raise_for_status()

    json_data = svar.json()

    rader = []
    for post in json_data["data"]:
        period = post["key"][0]
        varde  = post["values"][0]
        rader.append({
            "period": period,
            kolumnnamn: float(varde) if varde not in ["..", ""] else None
        })

    df = pd.DataFrame(rader).set_index("period")
    return df[kolumnnamn]

# ---------------------------------------------------------------------------
# Hämta båda variabler och slå ihop
# 00000804 = Årsförändring (%)
# 00000807 = KPI, skuggindex (2020=100) – används för att beräkna inflation
# ---------------------------------------------------------------------------

def hamta_data(api_url: str, perioder: list[str]) -> pd.DataFrame:
    arsforandring = hamta_variabel(api_url, perioder, "00000804", "kpi_arsforandring_pct")
    skuggindex    = hamta_variabel(api_url, perioder, "00000807", "kpi_skuggindex_2020_100")

    df = pd.DataFrame({
        "kpi_arsforandring_pct":    arsforandring,
        "kpi_skuggindex_2020_100":  skuggindex
    }).reset_index()

    df = df.rename(columns={"index": "period"})

    df["datum"] = pd.to_datetime(
        df["period"].str.replace("M", "-") + "-01",
        format="%Y-%m-%d"
    )

    df = df.sort_values("datum").reset_index(drop=True)

    return df[["datum", "period", "kpi_arsforandring_pct", "kpi_skuggindex_2020_100"]]

# ---------------------------------------------------------------------------
# Validering
# ---------------------------------------------------------------------------

def validera(df: pd.DataFrame) -> None:
    print(f"\n--- Validering ---")
    print(f"Antal rader:              {len(df)}")
    print(f"Första period:            {df['period'].iloc[0]}")
    print(f"Sista period:             {df['period'].iloc[-1]}")
    print(f"Saknade (årsförändring):  {df['kpi_arsforandring_pct'].isna().sum()}")
    print(f"Saknade (skuggindex):     {df['kpi_skuggindex_2020_100'].isna().sum()}")
    print(f"Min årsförändring:        {df['kpi_arsforandring_pct'].min():.1f}%")
    print(f"Max årsförändring:        {df['kpi_arsforandring_pct'].max():.1f}%")
    print(f"Medel årsförändring:      {df['kpi_arsforandring_pct'].mean():.1f}%")
    print(f"Min skuggindex:           {df['kpi_skuggindex_2020_100'].min():.1f}")
    print(f"Max skuggindex:           {df['kpi_skuggindex_2020_100'].max():.1f}")
    print(f"------------------\n")

    forvantat = (SLUT_AR - START_AR + 1) * 12
    if len(df) != forvantat:
        print(f"Varning: Förväntade {forvantat} rader men fick {len(df)}.")
    else:
        print(f"Radantal stämmer ({forvantat} månader).")

# ---------------------------------------------------------------------------
# Huvudprogram
# ---------------------------------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    perioder = bygg_perioder(START_AR, SLUT_AR)

    df = hamta_data(API_URL, perioder)

    validera(df)

    df.to_csv(OUTPUT_FIL, index=False, encoding="utf-8-sig")
    print(f"Data sparad till: {OUTPUT_FIL}")
    print("\nFörsta 5 raderna:")
    print(df.head().to_string(index=False))

if __name__ == "__main__":
    main()