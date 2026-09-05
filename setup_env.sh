#!/usr/bin/env bash
# One-time environment setup for capstone-solar-ghana (Phase A onward).
# Rebuilds .venv from requirements.txt and freezes the exact versions used.
set -euo pipefail
cd "$(dirname "$0")"

PY="$(command -v python3.12 || command -v python3)"
echo "Using: $("$PY" -V) at $PY"

"$PY" -m venv .venv --clear
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
.venv/bin/pip freeze > requirements-lock.txt
echo "Exact versions frozen to requirements-lock.txt"

.venv/bin/python - <<'EOF'
import importlib, platform
print(f"Python {platform.python_version()} on {platform.machine()}")
for m in ("numpy", "pandas", "sklearn", "statsmodels", "xgboost",
          "tensorflow", "shap", "matplotlib", "seaborn"):
    mod = importlib.import_module(m)
    print(f"  {m:<12} {getattr(mod, '__version__', '?')}")
print("Environment OK")
EOF
