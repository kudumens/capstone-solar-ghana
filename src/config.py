"""Project configuration: sites, parameters, date range, paths."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
RESULTS = PROJECT_ROOT / "results"

# Five study sites spanning Ghana's climatic zones
SITES = {
    "accra":    {"name": "Accra",    "zone": "coastal_savannah", "lat": 5.60,  "lon": -0.19},
    "takoradi": {"name": "Takoradi", "zone": "coastal",          "lat": 4.90,  "lon": -1.76},
    "kumasi":   {"name": "Kumasi",   "zone": "forest",           "lat": 6.69,  "lon": -1.62},
    "tamale":   {"name": "Tamale",   "zone": "guinea_savannah",  "lat": 9.40,  "lon": -0.84},
    "navrongo": {"name": "Navrongo", "zone": "sudan_savannah",   "lat": 10.89, "lon": -1.09},
}

# NASA POWER daily parameters (Renewable Energy community)
PARAMETERS = [
    "ALLSKY_SFC_SW_DWN",  # GHI, kWh/m2/day  (dependent variable)
    "T2M",                # air temperature at 2 m, deg C
    "RH2M",               # relative humidity at 2 m, %
    "CLOUD_AMT",          # cloud amount, %
    "PRECTOTCORR",        # corrected precipitation, mm/day
    "WS2M",               # wind speed at 2 m, m/s
]

START = "20050101"
END = "20241231"

API_URL = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
    "?parameters={params}&start={start}&end={end}"
    "&latitude={lat}&longitude={lon}&community=RE&format=CSV"
)

# Temporal split (no shuffling — prevents leakage)
TRAIN_END = "2020-12-31"
VAL_END = "2022-12-31"   # validation: 2021-2022; test: 2023-2024

# RQ5 off-grid sizing defaults
LOAD_KWH_MONTH_TIERS = [100, 200, 300]
PERFORMANCE_RATIO = 0.75
BATTERY_USABLE_DOD = 0.80
LOLP_TARGETS = [0.01, 0.05]
