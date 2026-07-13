"""Download NASA POWER daily data for all study sites.

Usage:  python src/download_power.py
Creates one CSV per site in data/raw/ plus a download log with row counts.
NASA POWER is free and requires no registration or API key.
"""
import csv
import hashlib
import io
import sys
import time
import urllib.request
from datetime import datetime

from config import API_URL, DATA_RAW, END, PARAMETERS, SITES, START

MAX_RETRIES = 4
BACKOFF_SECONDS = 10


def fetch(url: str) -> str:
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "capstone-solar-ghana/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"  attempt {attempt}/{MAX_RETRIES} failed: {e}")
            time.sleep(BACKOFF_SECONDS * attempt)
    raise RuntimeError(f"Download failed after {MAX_RETRIES} attempts: {last_err}")


def strip_header(raw: str) -> str:
    """NASA POWER CSVs begin with a commented metadata block ending at '-END HEADER-'."""
    if "-END HEADER-" in raw:
        raw = raw.split("-END HEADER-")[-1].lstrip("\r\n")
    return raw


def main() -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    log_path = DATA_RAW / "download_log.txt"
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n=== Download run {datetime.now().isoformat()} ===\n")
        for key, site in SITES.items():
            out = DATA_RAW / f"{key}_power_daily_{START}_{END}.csv"
            if out.exists():
                print(f"[skip] {out.name} already exists")
                continue
            url = API_URL.format(
                params=",".join(PARAMETERS), start=START, end=END,
                lat=site["lat"], lon=site["lon"],
            )
            print(f"[get ] {site['name']} ({site['lat']}, {site['lon']}) ...")
            raw = fetch(url)
            body = strip_header(raw)
            rows = list(csv.reader(io.StringIO(body)))
            n_data = max(0, len([r for r in rows if r]) - 1)
            out.write_text(body, encoding="utf-8")
            digest = hashlib.sha256(body.encode()).hexdigest()[:16]
            msg = f"{out.name}: {n_data} data rows, sha256:{digest}"
            print(f"[ok  ] {msg}")
            log.write(msg + "\n")
            time.sleep(2)  # be polite to the API
    print("\nDone. Next: python src/validate_data.py")


if __name__ == "__main__":
    sys.exit(main())
