"""
04_validera_data.py
===================
Validerar rådata mot kända referensvärden från officiella källor.
Syftet är att säkerställa att datainsamlingen gått rätt till innan
vi går vidare till rensning och analys.

Referensvärden hämtade manuellt från:
- KI:s statistikdatabas (statistik.konj.se)
- SCB:s statistikdatabas (statistikdatabasen.scb.se)
- Riksbankens webbplats (riksbank.se)
"""

import pandas as pd
from pathlib import Path

# ---------------------------------------------------------------------------
# Sökvägar
# ---------------------------------------------------------------------------

KI_FIL        = Path("data/raw/ki_barometer_1996_2024.csv")
KPI_FIL       = Path("data/raw/scb_kpi_1996_2024.csv")
RIKSBANK_FIL  = Path("data/raw/riksbanken_styranta_1996_2024.csv")

# ---------------------------------------------------------------------------
# Kända referensvärden (manuellt verifierade mot officiella källor)
# ---------------------------------------------------------------------------

REFERENSVARDEN = [
    {
        "fil":         KI_FIL,
        "kolumn":      "barometerindikator",
        "period":      "2009M01",
        "forvantad":   73.3,
        "tolerans":    0.1,
        "beskrivning": "KI barometer januari 2009 (finanskrisens botten)",
        "kalla":       "statistik.konj.se"
    },
    {
        "fil":         KPI_FIL,
        "kolumn":      "kpi_arsforandring_pct",
        "period":      "2022M10",
        "forvantad":   10.9,
        "tolerans":    0.1,
        "beskrivning": "KPI årsförändring oktober 2022 (inflationstoppen)",
        "kalla":       "statistikdatabasen.scb.se"
    },
    {
        "fil":         KPI_FIL,
        "kolumn":      "kpi_arsforandring_pct",
        "period":      "2020M06",
        "forvantad":   0.7,
        "tolerans":    0.1,
        "beskrivning": "KPI årsförändring juni 2020 (låg inflation under corona)",
        "kalla":       "statistikdatabasen.scb.se"
    },
    {
        "fil":         RIKSBANK_FIL,
        "kolumn":      "styranta_pct",
        "period":      "2022M07",
        "forvantad":   0.5,       # Genomsnitt av 0.25% och 0.75% under månaden
        "tolerans":    0.3,       # Generösare tolerans – vi jämför mot månadssnitt
        "beskrivning": "Riksbankens styrränta juli 2022 (höjning från 0.25% till 0.75%)",
        "kalla":       "riksbank.se"
    },
    {
        "fil":         RIKSBANK_FIL,
        "kolumn":      "styranta_pct",
        "period":      "1996M01",
        "forvantad":   8.72,
        "tolerans":    0.1,
        "beskrivning": "Riksbankens styrränta januari 1996 (hög ränta efter 90-talskrisen)",
        "kalla":       "riksbank.se"
    },
]

# ---------------------------------------------------------------------------
# Valideringsfunktion
# ---------------------------------------------------------------------------

def validera_referensvarde(ref: dict) -> bool:
    df = pd.read_csv(ref["fil"])

    rad = df[df["period"] == ref["period"]]

    if rad.empty:
        print(f"  FEL: Period {ref['period']} hittades inte i {ref['fil'].name}")
        return False

    faktiskt = rad[ref["kolumn"]].values[0]
    avvikelse = abs(faktiskt - ref["forvantad"])
    godkand = avvikelse <= ref["tolerans"]

    status = "✓ OK" if godkand else "✗ FEL"

    print(f"  {status}  {ref['beskrivning']}")
    print(f"         Period:    {ref['period']}")
    print(f"         Förväntat: {ref['forvantad']}  |  Faktiskt: {round(faktiskt, 3)}  |  Avvikelse: {round(avvikelse, 3)}")
    print(f"         Källa:     {ref['kalla']}")
    print()

    return godkand

# ---------------------------------------------------------------------------
# Grundläggande filkontroller
# ---------------------------------------------------------------------------

def kontrollera_filer() -> bool:
    print("=" * 60)
    print("FILKONTROLL")
    print("=" * 60)

    alla_ok = True
    filer = [
        (KI_FIL,       348, "KI barometer"),
        (KPI_FIL,      348, "SCB KPI"),
        (RIKSBANK_FIL, 348, "Riksbanken styrränta"),
    ]

    for fil, forvantat_antal, namn in filer:
        if not fil.exists():
            print(f"  ✗ FEL:  {namn} – filen saknas ({fil})")
            alla_ok = False
            continue

        df = pd.read_csv(fil)
        antal = len(df)
        period_ok = (df["period"].iloc[0] == "1996M01" and
                     df["period"].iloc[-1] == "2024M12")
        antal_ok = antal == forvantat_antal

        if antal_ok and period_ok:
            print(f"  ✓ OK    {namn} – {antal} rader, 1996M01–2024M12")
        else:
            print(f"  ✗ FEL:  {namn} – {antal} rader (förväntat {forvantat_antal}), period OK: {period_ok}")
            alla_ok = False

    print()
    return alla_ok

# ---------------------------------------------------------------------------
# Huvudprogram
# ---------------------------------------------------------------------------

def main():
    print()
    print("=" * 60)
    print("DATAVALIDERING – KI Barometer-projektet")
    print("=" * 60)
    print()

    # Steg 1: Filkontroll
    filer_ok = kontrollera_filer()

    if not filer_ok:
        print("Avbryter – åtgärda filproblemen innan du fortsätter.")
        return

    # Steg 2: Referensvärden
    print("=" * 60)
    print("REFERENSVÄRDEN")
    print("=" * 60)
    print()

    resultat = []
    for ref in REFERENSVARDEN:
        ok = validera_referensvarde(ref)
        resultat.append(ok)

    # Sammanfattning
    antal_ok  = sum(resultat)
    antal_fel = len(resultat) - antal_ok

    print("=" * 60)
    print("SAMMANFATTNING")
    print("=" * 60)
    print(f"  Godkända kontroller: {antal_ok} / {len(resultat)}")
    if antal_fel == 0:
        print("  ✓ All data godkänd – redo för nästa steg.")
    else:
        print(f"  ✗ {antal_fel} kontroll(er) misslyckades – granska datan innan du fortsätter.")
    print()

def rita_grafer():
    import matplotlib.pyplot as plt

    print("Ritar grafer...")

    ki  = pd.read_csv(KI_FIL,       parse_dates=["datum"])
    kpi = pd.read_csv(KPI_FIL,      parse_dates=["datum"])
    rb  = pd.read_csv(RIKSBANK_FIL, parse_dates=["datum"])

    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle("KI Barometer-projektet – rådata 1996–2024", fontsize=13)

    # --- Graf 1: KI barometer ---
    axes[0].plot(ki["datum"], ki["barometerindikator"], color="#1f77b4", linewidth=1.2)
    axes[0].axhline(100, color="gray", linestyle="--", linewidth=0.8)
    axes[0].set_ylabel("Index")
    axes[0].set_title("KI:s barometerindikator (medelvärde = 100)")
    axes[0].annotate("Finanskris", xy=(pd.Timestamp("2009-01-01"), 73.3),
                     xytext=(pd.Timestamp("2011-01-01"), 68),
                     arrowprops=dict(arrowstyle="->", color="red"), color="red", fontsize=8)

    # --- Graf 2: KPI årsförändring ---
    axes[1].plot(kpi["datum"], kpi["kpi_arsforandring_pct"], color="#d62728", linewidth=1.2)
    axes[1].axhline(2, color="gray", linestyle="--", linewidth=0.8, label="Inflationsmål 2%")
    axes[1].axhline(0, color="black", linestyle="-", linewidth=0.5)
    axes[1].set_ylabel("Procent")
    axes[1].set_title("KPI årsförändring (%)")
    axes[1].legend(fontsize=8)
    axes[1].annotate("10.9% (okt 2022)", xy=(pd.Timestamp("2022-10-01"), 10.9),
                     xytext=(pd.Timestamp("2018-01-01"), 10),
                     arrowprops=dict(arrowstyle="->", color="red"), color="red", fontsize=8)

    # --- Graf 3: Styrränta ---
    axes[2].plot(rb["datum"], rb["styranta_pct"], color="#2ca02c", linewidth=1.2)
    axes[2].axhline(0, color="black", linestyle="-", linewidth=0.5)
    axes[2].set_ylabel("Procent")
    axes[2].set_title("Riksbankens styrränta (%)")
    axes[2].annotate("Minusränta", xy=(pd.Timestamp("2016-01-01"), -0.5),
                     xytext=(pd.Timestamp("2010-01-01"), -0.8),
                     arrowprops=dict(arrowstyle="->", color="red"), color="red", fontsize=8)

    plt.tight_layout()

    OUTPUT_GRAF = Path("data/raw/validering_graf.png")
    plt.savefig(OUTPUT_GRAF, dpi=150)
    print(f"Graf sparad till: {OUTPUT_GRAF}")
    plt.show()


if __name__ == "__main__":
    main()
    rita_grafer()
