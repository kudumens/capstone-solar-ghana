# Machine-Learning Forecasting of Solar Irradiance and Reliability-Constrained Off-Grid Solar Sizing Across Ghana's Climatic Zones

QM 640 Data Analytics Capstone — Walsh College / Great Learning (MSc)
Author: Richard Adjei-Mensah · Term 3 - 2026

## Overview

This project (1) develops and statistically compares classical (persistence, day-of-year climatology, and SARIMA-class dynamic harmonic regression) and machine-learning (random forest, XGBoost, LSTM) models forecasting daily global horizontal irradiance (GHI) at five sites spanning Ghana's coastal, forest, and savannah climatic zones, and (2) converts the same twenty-year irradiance record into a reliability-constrained off-grid sizing model that computes, per climatic zone, the PV array and battery capacity required to serve a household load at target loss-of-load probabilities (LOLP).

### Research questions

- **RQ1** — How accurately can ML models (random forest, XGBoost, LSTM) forecast daily GHI across Ghana's climatic zones, and do they significantly outperform classical approaches (persistence, day-of-year climatology, dynamic harmonic regression) at the 1-day and 7-day horizons?
- **RQ2** — Which meteorological variables are most strongly associated with daily solar-irradiance variation, and which contribute most to predictive performance?
- **RQ3** — How does forecasting accuracy differ between the wet and dry seasons (including the Harmattan) and across the north–south climatic gradient?
- **RQ4** — What PV array + battery capacity does an off-grid household need per climatic zone to serve 100/200/300 kWh/month at 1–5% LOLP?

## Key results (test window 2023–2024, single evaluation)

Best ML model per site (frozen on 2021–2022 validation) vs. the strongest classical baseline (DHR), 1-day horizon:

| Site | Best ML | Test RMSE (kWh/m²/day) | Skill vs. DHR | Holm p (one-sided HLN DM) |
| --- | --- | --- | --- | --- |
| Navrongo | LSTM | 0.845 | +0.4% | .365 |
| Tamale | Random forest | 0.828 | +2.7% | .005 |
| Kumasi | Random forest | 0.664 | +3.5% | < .001 |
| Accra | Random forest | 0.841 | +5.3% | < .001 |
| Takoradi | XGBoost | 1.024 | +4.4% | .004 |

- **H1 (≥15% RMSE reduction vs. climatology, significant in every zone): not supported.** Gains are statistically significant at 4/5 sites vs. DHR (5/5 vs. climatology) but peak at +10.2% vs. climatology. At the 7-day horizon no model separates from the seasonal baseline. Model combination (ensembles, DHR blends) adds nothing (`results/ensemble_check.csv`).
- **H2 (cloud & humidity strongest drivers): not supported.** Cloud amount is the strongest *marginal* correlate everywhere (Spearman ρ −.44 to −.69), but conditionally (SHAP) irradiance history absorbs the signal.
- **H3 (wet-season degradation, worst in the south): partially supported.** Wet > dry RMSE significant at Kumasi/Accra/Takoradi; stable zonal ordering (forest easiest, coast hardest).
- **H4 (≥25% zonal battery difference): supported decisively.** At the 200 kWh/month tier, required nominal battery spans 1.4→6.2 kWh (LOLP 5%) and 4.3→32.4 kWh (LOLP 1%) across zones: a 343–654% spread (year-block bootstrap CIs entirely above 25%). The 2-day-autonomy installer rule oversizes the north ~10× while failing the 1% target in the forest zone.

Full tables in `results/` (`test_metrics.csv`, `dm_tests.csv`, `sizing_tables.csv`, `h4_test.csv`); figures in `results/figures/`.

## Data

Source: [NASA POWER](https://power.larc.nasa.gov/) daily point data (Renewable Energy community), 2005-01-01 → 2024-12-31, six parameters: `ALLSKY_SFC_SW_DWN` (GHI), `T2M`, `RH2M`, `CLOUD_AMT`, `PRECTOTCORR`, `WS2M`. 36,525 site-days, zero missing.

| Site     | Zone             | Lat   | Lon   |
| -------- | ---------------- | ----- | ----- |
| Accra    | Coastal savannah | 5.60  | -0.19 |
| Takoradi | Coastal          | 4.90  | -1.76 |
| Kumasi   | Moist forest     | 6.69  | -1.62 |
| Tamale   | Guinea savannah  | 9.40  | -0.84 |
| Navrongo | Sudan savannah   | 10.89 | -1.09 |

NASA POWER data are free and openly licensed; no registration required. Validation for Ghana: Quansah et al. (2022), _Scientific Reports_ 12, 10684.

## Reproduction

```bash
# 1. Build the environment (Python 3.12; creates .venv and requirements-lock.txt)
bash setup_env.sh

# 2. Download raw data (~5 CSVs, one per site; requires internet)
.venv/bin/python src/download_power.py

# 3. Validate the download and build the processed dataset
.venv/bin/python src/validate_data.py
.venv/bin/python src/clean_data.py

# 4. Run the notebooks in order (01 → 07), e.g.
.venv/bin/jupyter lab notebooks
```

Execution notes:

- **Determinism**: `SEED = 42` in every notebook (Python/NumPy/scikit-learn/XGBoost/TensorFlow). Splits are frozen in `src/config.py` (train ≤ 2020, validation 2021–2022, test 2023–2024; the test window is touched only in notebook 06, once).
- **Search modes (notebook 05)**: `NB05_SEARCH_MODE=full` (default; 27 RF / 72 XGB / 12 LSTM configurations, ~95 min on an Apple-silicon CPU) or `quick` (reduced grids for smoke tests).
- **Checkpointing**: notebooks 05–07 checkpoint all expensive work to `results/cache/` and resume after interruption (useful on Colab). Optional wall-clock budgets via `NB05_BUDGET_S` / `NB06_BUDGET_S` / `NB07_BUDGET_S` make runs stop cleanly and resume on rerun.
- Executing end-to-end with existing caches only re-renders tables and figures; delete `results/cache/` to force full recomputation.

## Repository structure

```text
capstone-solar-ghana/
├── README.md
├── LICENSE
├── requirements.txt         pinned versions of the reported run
├── requirements-lock.txt    full transitive freeze (created by setup_env.sh)
├── setup_env.sh
├── data/
│   ├── raw/                 NASA POWER CSVs, one per site (created by step 2)
│   └── processed/           cleaned, feature-engineered datasets (created by step 3)
├── notebooks/
│   ├── 01_download_data     … raw acquisition
│   ├── 02_data_validation   … QC (zero missing days)
│   ├── 03_eda               … distributions, seasonality, low-sun runs
│   ├── 04_baselines         … persistence, climatology, DHR
│   ├── 05_ml_models         … RF/XGBoost/LSTM tuning, both horizons
│   ├── 06_model_comparison  … test-set evaluation, DM tests, SHAP, RQ3
│   └── 07_offgrid_sizing    … 20-year LOLP backtest, H4, sizing tables
├── src/
│   ├── config.py            sites, parameters, date range, splits, paths
│   ├── download_power.py    NASA POWER API downloader (retry + checksum log)
│   ├── validate_data.py     row counts, ranges, missing-value report
│   └── clean_data.py        cleaning + feature engineering → data/processed/
├── results/                 metrics tables, sizing tables, figures/
└── reports/                 synopsis v2.2, annotated bibliography, interim & final reports
```

## Methods summary

Temporal split: train 2005–2020, validate 2021–2022, test 2023–2024 (no shuffling; single test evaluation in notebook 06). Direct multi-step strategy at h = 1 and 7; 16 origin-day features. Inference: one-sided HLN-corrected Diebold–Mariano tests with Holm adjustment, moving-block-bootstrap skill intervals (block ≈ decorrelation time), SHAP (RQ2), joint-block seasonal/zonal tests (RQ3). Sizing (RQ4): 20-year daily energy-balance backtest, LOLP 1%/5%, tiers 100/200/300 kWh/month, PR 0.75 (sensitivity 0.70–0.80), DoD 80%, year-block + moving-block bootstrap intervals. Full methodology in the final report in `reports/`.

## License

Code: MIT (see LICENSE). Data: NASA POWER open data — cite NASA Langley Research Center POWER Project.
