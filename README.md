# Forecasting Solar Irradiance and Probabilistic Off-Grid Solar Sizing for Ghana Using Machine Learning

QM 640 Data Analytics Capstone — Walsh College / Great Learning (MSc)
Author: Richard Adjei-Mensah · Summer 2026

## Overview

This project (1) develops and statistically compares classical (seasonal-naïve persistence, SARIMA) and machine-learning (random forest, XGBoost, LSTM) models forecasting daily global horizontal irradiance (GHI) at five sites spanning Ghana's coastal, forest, and savannah climatic zones, and (2) converts the same twenty-year irradiance record into a probabilistic off-grid sizing model that computes, per climatic zone, the PV array and battery capacity required to serve a household load (benchmark: 200 kWh/month) at a target loss-of-load probability (LOLP).

**Research questions**

- **RQ1** — How accurately can ML models forecast daily GHI across Ghana's climatic zones?
- **RQ2** — Which meteorological variables most strongly drive irradiance variation?
- **RQ3** — Do ML models significantly outperform classical baselines at 1-day and 7-day horizons?
- **RQ4** — How does accuracy differ between wet/dry (Harmattan) seasons and across zones?
- **RQ5** — What PV array + battery capacity does an off-grid household need per zone for 200 kWh/month at 1–5% LOLP?

## Data

Source: [NASA POWER](https://power.larc.nasa.gov/) daily point data (Renewable Energy community), 2005-01-01 → 2024-12-31, six parameters: `ALLSKY_SFC_SW_DWN` (GHI), `T2M`, `RH2M`, `CLOUD_AMT`, `PRECTOTCORR`, `WS2M`.

| Site | Zone | Lat | Lon |
|------|------|-----|-----|
| Accra | Coastal savannah | 5.60 | -0.19 |
| Takoradi | Coastal | 4.90 | -1.76 |
| Kumasi | Moist forest | 6.69 | -1.62 |
| Tamale | Guinea savannah | 9.40 | -0.84 |
| Navrongo | Sudan savannah | 10.89 | -1.09 |

NASA POWER data are free and openly licensed; no registration required. Validation for Ghana: Quansah et al. (2022), *Scientific Reports* 12, 10684.

## Reproduction

```bash
# 1. Install dependencies (Python 3.10+)
pip install -r requirements.txt

# 2. Download raw data (~5 CSVs, one per site; requires internet)
python src/download_power.py

# 3. Validate the download and build the processed dataset
python src/validate_data.py
python src/clean_data.py

# 4. Run the analysis notebooks in order
jupyter lab notebooks/
```

## Repository structure

```
capstone-solar-ghana/
├── README.md
├── LICENSE
├── requirements.txt
├── data/
│   ├── raw/                 NASA POWER CSVs, one per site (created by step 2)
│   └── processed/           cleaned, feature-engineered datasets (created by step 3)
├── notebooks/               01_download … 07_offgrid_sizing
├── src/
│   ├── config.py            sites, parameters, date range, paths
│   ├── download_power.py    NASA POWER API downloader (retry + checksum log)
│   ├── validate_data.py     row counts, ranges, missing-value report
│   └── clean_data.py        cleaning + feature engineering → data/processed/
├── results/                 metrics tables, figures, sizing tables
└── reports/                 interim & final report assets
```

## Methods summary

Temporal split: train 2005–2020, validate 2021–2022, test 2023–2024 (no shuffling). Metrics: RMSE, MAE, R², skill vs. seasonal-naïve baseline (target ≥ 15% RMSE reduction), Diebold–Mariano tests for RQ3, LOLP for RQ5. See the synopsis in `reports/` for full methodology.

## License

Code: MIT (see LICENSE). Data: NASA POWER open data — cite NASA Langley Research Center POWER Project.
