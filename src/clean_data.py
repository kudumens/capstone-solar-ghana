"""Clean raw NASA POWER CSVs and build the processed modelling dataset.

Usage: python src/clean_data.py
Steps: replace -999 sentinels, build a continuous daily index, interpolate
short gaps (<=3 days), add calendar/season features, lags, and rolling means.
Output: data/processed/all_sites_daily.csv (+ one file per site).
"""
import sys

import numpy as np
import pandas as pd

from config import DATA_PROCESSED, DATA_RAW, END, PARAMETERS, SITES, START

TARGET = "ALLSKY_SFC_SW_DWN"
MAX_GAP_INTERPOLATE = 3


def season_of(month: int) -> str:
    """Southern-Ghana seasonal convention; Harmattan = Dec-Feb dust season."""
    if month in (12, 1, 2):
        return "harmattan_dry"
    if month in (3, 4, 5, 6):
        return "major_wet"
    if month in (7, 8):
        return "minor_dry"
    return "minor_wet"  # Sep-Nov


def load_site(key: str) -> pd.DataFrame:
    path = DATA_RAW / f"{key}_power_daily_{START}_{END}.csv"
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(
        df["YEAR"].astype(str) + df["DOY"].astype(str).str.zfill(3), format="%Y%j"
    )
    df = df.set_index("date").sort_index()
    df = df[PARAMETERS].replace(-999, np.nan)
    # enforce continuous daily index
    full = pd.date_range(pd.Timestamp(START), pd.Timestamp(END), freq="D")
    df = df.reindex(full)
    df = df.interpolate(limit=MAX_GAP_INTERPOLATE, limit_direction="both")
    return df


def engineer(df: pd.DataFrame, key: str) -> pd.DataFrame:
    site = SITES[key]
    out = df.copy()
    out["site"] = key
    out["zone"] = site["zone"]
    doy = out.index.dayofyear
    out["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    out["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    out["month"] = out.index.month
    out["season"] = [season_of(m) for m in out.index.month]
    for lag in range(1, 8):
        out[f"ghi_lag{lag}"] = out[TARGET].shift(lag)
    out["ghi_roll7"] = out[TARGET].rolling(7).mean()
    out["ghi_roll30"] = out[TARGET].rolling(30).mean()
    return out


def main() -> int:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    frames = []
    for key in SITES:
        df = engineer(load_site(key), key)
        df.index.name = "date"
        df.to_csv(DATA_PROCESSED / f"{key}_daily_features.csv")
        frames.append(df)
        n_missing = int(df[TARGET].isna().sum())
        print(f"{key:<10} rows={len(df)}  remaining {TARGET} NaNs={n_missing}")
    all_df = pd.concat(frames)
    all_df.to_csv(DATA_PROCESSED / "all_sites_daily.csv")
    print(f"\nWrote {DATA_PROCESSED / 'all_sites_daily.csv'} ({len(all_df)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
