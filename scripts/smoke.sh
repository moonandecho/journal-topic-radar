#!/usr/bin/env bash
# One-command self-check: Python/deps/config/matcher/offline pipeline/source connectivity.
set -euo pipefail
cd "$(dirname "$0")/.."
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
PY="${PYTHON:-.venv/bin/python}"
if [ ! -x "$PY" ]; then PY=python3; fi
"$PY" - "$@" <<'PY'
from __future__ import annotations
import importlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))

rows: list[tuple[str, str, str]] = []


def add(name: str, ok: bool, detail: str) -> None:
    rows.append((name, "PASS" if ok else "FAIL", detail))


# 1. Python version
add("Python >= 3.9", sys.version_info >= (3, 9), f"{sys.version.split()[0]}")
# 2. dependencies
for mod in ("requests", "yaml", "bs4", "jieba"):
    try:
        m = importlib.import_module(mod)
        add(f"dependency:{mod}", True, getattr(m, "__version__", "ok"))
    except Exception as e:
        add(f"dependency:{mod}", False, repr(e))
# 3. config
try:
    from radar import config
    journals = config.load_journals()
    domestic = sum(j["country"] == "国内" for j in journals)
    foreign = sum(j["country"] == "国外" for j in journals)
    add("config 10 journals / 5+5", len(journals) == 10 and domestic == 5 and foreign == 5,
        f"{len(journals)} journals ({domestic} 国内 / {foreign} 国外)")
except Exception as e:
    add("config 10 journals / 5+5", False, repr(e))
    journals = []
# 4. fixtures
try:
    missing = [j["slug"] for j in journals if not (config.ROOT / "fixtures" / f"{j['slug']}.json").exists()]
    add("offline fixtures", not missing, "all present" if not missing else f"missing: {missing}")
except Exception as e:
    add("offline fixtures", False, repr(e))
# 5. matcher backend
backend = None
try:
    from radar.matcher import make_backend
    backend, reasons = make_backend("auto")
    add("matcher backend", True, f"{backend.name} / {backend.kind}" + (f" degraded={reasons}" if reasons else ""))
except Exception as e:
    add("matcher backend", False, repr(e))
# 6. sample offline match
try:
    from radar.pipeline import run_match
    t = time.time()
    report = run_match("大语言模型驱动的代码生成与漏洞检测", journal_names=[journals[0]["name"]] if journals else None,
                       offline=True, matcher_prefer="lexical")
    add("sample offline match", len(report.journals) >= 1, f"{len(report.journals)} journal(s), {time.time()-t:.2f}s")
except Exception as e:
    add("sample offline match", False, repr(e))
# 7. source connectivity (real network; run in parallel)
from radar.sources.common import date_after, session
sess = session()


def probe(j):
    if j["country"] == "国内":
        url = j.get("current_url") or j.get("site_url") or j.get("official_site")
        try:
            r = sess.get(url, timeout=15)
            return j["name"], r.status_code < 400, f"HTTP {r.status_code} {url}"
        except Exception as e:
            return j["name"], False, f"{type(e).__name__}: {e} ({url})"
    issn = j["issn"]
    ok = True
    details = []
    try:
        r = sess.get(f"https://api.crossref.org/journals/{issn}/works",
                     params={"rows": 1, "sort": "published", "order": "desc",
                             "filter": f"from-pub-date:{date_after(30)}"}, timeout=20)
        details.append(f"Crossref HTTP {r.status_code}")
        ok = ok and r.status_code < 400
    except Exception as e:
        details.append(f"Crossref ERR {type(e).__name__}")
        ok = False
    try:
        r = sess.get("https://api.openalex.org/works",
                     params={"filter": f"primary_location.source.issn:{issn}", "per-page": 1,
                             "mailto": "radar@example.invalid"}, timeout=20)
        details.append(f"OpenAlex HTTP {r.status_code}")
        ok = ok and r.status_code < 400
    except Exception as e:
        details.append(f"OpenAlex ERR {type(e).__name__}")
        ok = False
    return j["name"], ok, "; ".join(details)


if journals:
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(probe, j) for j in journals]
        for fut in as_completed(futs):
            name, ok, detail = fut.result()
            add(f"source:{name[:22]}", ok, detail)
# 8. optional known sources (home reachable, not default route)
try:
    from radar.sources import sciengine, wanfang
    ok1, d1 = sciengine.probe()
    add("source:sciengine home", ok1, d1)
    ok2, d2 = wanfang.probe()
    add("source:wanfang home", ok2, d2)
except Exception as e:
    add("source:extra probes", False, repr(e))

# print PASS/FAIL table
width = max(len(r[0]) for r in rows) if rows else 10
print("=" * 118)
print(f"{'CHECK':<{width}}  {'RESULT':<6}  DETAIL")
print("-" * 118)
for name, result, detail in rows:
    print(f"{name:<{width}}  {result:<6}  {detail}")
print("=" * 118)
failed = [r for r in rows if r[1] != "PASS"]
print(f"SMOKE RESULT: {'PASS' if not failed else 'FAIL'} ({len(rows)-len(failed)}/{len(rows)} passed)")
if failed:
    raise SystemExit(1)
PY
