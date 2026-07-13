"""Validate downloaded NASA POWER CSVs: row counts, ranges, missing values.

Usage: python src/validate_data.py
Writes results/data_validation_report.txt and prints a summary.
NASA POWER encodes missing values as -999.
"""
import sys

import pandas as pd

from config import DATA_RAW, END, PARAMETERS, RESULTS, SITES, START

EXPECTED_DAYS = (pd.Timestamp(END) - pd.Timestamp(START)).days + 1  # 7,305 for 2005-2024

RANGES = {
    "ALLSKY_SFC_SW_DWN": (0, 9),      # kWh/m2/day
    "T2M": (5, 45),                   # deg C
    "RH2M": (0, 100),                 # %
    "CLOUD_AMT": (0, 100),            # %
    "PRECTOTCORR": (0, 400),          # mm/day
    "WS2M": (0, 25),                  # m/s
}


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    lines = [f"Data validation report — expected {EXPECTED_DAYS} rows per site\n"]
    ok = True
    for key, site in SITES.items():
        path = DATA_RAW / f"{key}_power_daily_{START}_{END}.csv"
        if not path.exists():
            lines.append(f"[MISSING] {path.name} — run src/download_power.py first")
            ok = False
            continue
        df = pd.read_csv(path)
        df = df.replace(-999, pd.NA)
        n = len(df)
        lines.append(f"\n{site['name']} ({path.name})")
        lines.append(f"  rows: {n} ({'OK' if n == EXPECTED_DAYS else 'UNEXPECTED'})")
        for p in PARAMETERS:
            if p not in df.columns:
                lines.append(f"  [FAIL] column {p} missing")
                ok = False
                continue
            col = pd.to_numeric(df[p], errors="coerce")
            miss = int(col.isna().sum())
            lo, hi = RANGES[p]
            out_of_range = int(((col < lo) | (col > hi)).sum())
            flag = "" if (miss / max(n, 1) < 0.02 and out_of_range == 0) else "  <-- CHECK"
            lines.append(
                f"  {p:<20} missing={miss:>5} ({miss/max(n,1):.2%})  "
                f"min={col.min():.2f} max={col.max():.2f}{flag}"
            )
            if miss / max(n, 1) >= 0.02 or out_of_range > 0:
                ok = False
    report = "\n".join(str(x) for x in lines)
    (RESULTS / "data_validation_report.txt").write_text(report, encoding="utf-8")
    print(report)
    print(f"\nOverall: {'PASS' if ok else 'ISSUES FOUND (see above)'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
