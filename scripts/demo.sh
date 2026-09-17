#!/usr/bin/env bash
# 5-minute interview demo: offline, no network, uses real fixtures.
# Usage: ./scripts/demo.sh "你的论文主题"
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
TOPIC="${1:-大语言模型驱动的代码生成与漏洞检测}"
PY="${PYTHON:-.venv/bin/python}"
if [ ! -x "$PY" ]; then PY=python3; fi
mkdir -p docs/demo-output
echo "[demo] topic=$TOPIC"
echo "[demo] matcher=auto (embedding if available, otherwise explicit lexical degradation)"
PYTHONPATH=src "$PY" -m radar match --topic "$TOPIC" --offline --matcher auto --format table --output docs/demo-output/latest
echo "[demo] written: docs/demo-output/latest.json"
echo "[demo] written: docs/demo-output/latest.md"
