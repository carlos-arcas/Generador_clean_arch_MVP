#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_DIR}"

if [[ ! -x "${PROJECT_DIR}/.venv/bin/python" ]]; then
  python3 -m venv "${PROJECT_DIR}/.venv"
fi

source "${PROJECT_DIR}/.venv/bin/activate"
python -m pip install --upgrade pip
pip install -r "${PROJECT_DIR}/requirements.txt"

if ! python -m herramientas.auditar_completitud_producto; then
  echo "VALIDACIÓN FALLIDA"
  exit 1
fi

if ! pytest -q --maxfail=1; then
  echo "VALIDACIÓN FALLIDA"
  exit 1
fi

if ! pytest --cov=. --cov-report=term-missing --cov-fail-under=85; then
  echo "VALIDACIÓN FALLIDA"
  exit 1
fi

echo "PRODUCTO VALIDADO 100%"
