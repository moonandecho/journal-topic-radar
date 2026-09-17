#!/usr/bin/env python3
"""Fetch the configured journals online and write docs/source-evidence.md.

This is deliberately a real-network command: it writes HTTP status, issue,
publication date, first 3 titles and a normalized fixture path for each
configured journal.  It also stores a small raw-response snippet under
fixtures/raw/ so the repo contains real response samples.
"""
from __future__ import annotations
from datetime import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from radar import config
from radar.pipeline import fetch_issue
from radar.sources.common import http_get, date_after, SourceError

ROOT = config.ROOT
RAW = ROOT / "fixtures" / "raw"


def primary_target(j: dict) -> str:
    if j.get("country") == "国内":
        return j.get("current_url") or j.get("site_url") or j.get("official_site") or ""
    issn = j.get("issn")
    return f"https://api.crossref.org/journals/{issn}/works"


def probe(j: dict) -> tuple[str, int | str, int | str]:
    url = primary_target(j)
    try:
        if j.get("country") == "国外":
            r = http_get(url, params={"rows": 5, "sort": "published", "order": "desc",
                                      "filter": f"from-pub-date:{date_after(30)}"}, timeout=30)
        else:
            r = http_get(url, timeout=30)
        return url, r.status_code, len(r.content)
    except SourceError as e:
        return url, "ERR", e.message
    except Exception as e:
        return url, "ERR", repr(e)


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    journals = config.load_journals()
    lines: list[str] = []
    lines.append("# 数据源真实抓取证据")
    lines.append("")
    lines.append(f"- 生成方式：使用项目 adapter 对 10 本运行时期刊逐一真实联网抓取。")
    lines.append(f"- 生成时间：{datetime.now().astimezone().isoformat(timespec='seconds')}")
    lines.append("- 每刊 `fixtures/<slug>.json` 是本次响应标准化后的可离线样本；`fixtures/raw/<slug>.txt` 保留真实响应片段。")
    lines.append("")
    lines.append("## 1. 汇总表")
    lines.append("")
    lines.append("| # | 期刊 | 国别 | 主源 | HTTP | 期号 | 发布日期 | 抓取论文数 | 前 3 条标题 |")
    lines.append("|---:|---|---|---|---:|---|---:|---:|---|")
    details: list[str] = []
    captured: list[str] = []
    for i, j in enumerate(journals, 1):
        url, status, size = probe(j)
        try:
            issue = fetch_issue(j, offline=False)
            ok = issue.ok
            n = len(issue.papers)
            issue_s = issue.issue or "-"
            pub = issue.published or "-"
            src = issue.source or "-"
            titles = [p.title for p in issue.papers[:3]]
            if issue.ok:
                fixture = dict(issue.to_dict())
                fixture["captured_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
                fixture["capture_note"] = "normalized from real online adapter response"
                (ROOT / "fixtures" / f"{j.get('slug')}.json").write_text(
                    json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            ok = False; n = 0; issue_s = "-"; pub = "-"; src = "-"; titles = []
            issue = None
            lines.append(f"<!-- fetch_issue failed for {j.get('name')}: {e} -->")
        title_cell = "<br>".join(t.replace("|", "\\|") for t in titles[:3]) if titles else "-"
        lines.append(f"| {i} | {j.get('name')} | {j.get('country')} | `{src}` | {status} | {issue_s} | {pub} | {n} | {title_cell} |")
        # raw snippet
        try:
            if j.get("country") == "国外":
                params = {"rows": 3, "sort": "published", "order": "desc",
                          "filter": f"from-pub-date:{date_after(30)}"}
                r = http_get(url, params=params, timeout=30)
            else:
                r = http_get(url, timeout=30)
            snippet = r.text[:2500]
        except Exception as e:
            snippet = f"probe failed: {e}"
        raw_path = RAW / f"{j.get('slug')}.txt"
        raw_path.write_text(f"URL: {url}\nHTTP/bytes: {status}/{size}\nCaptured: {datetime.now().astimezone().isoformat(timespec='seconds')}\n\n{snippet}\n", encoding="utf-8")
        captured.append(str(raw_path.relative_to(ROOT)))
        details.append("")
        details.append(f"### {i}. {j.get('name')}")
        details.append("")
        details.append(f"- 国别：{j.get('country')}")
        details.append(f"- 标识：ISSN={j.get('issn') or '-'}；slug={j.get('slug')}；官网={j.get('official_site') or '-'}")
        details.append(f"- 主目标 URL：{url}")
        details.append(f"- HTTP/大小：{status}；{size} bytes")
        details.append(f"- adapter 源：`{src}`；期号：{issue_s}；发布日期：{pub}；论文数：{n}")
        if issue is not None:
            for d in issue.diagnostics[:6]:
                details.append(f"- 诊断：{d}")
        for k, p in enumerate((issue.papers[:3] if issue else []), 1):
            details.append(f"- Top{k}：{p.title} | {p.published} | {p.url}")
        details.append(f"- 标准化离线样本：`fixtures/{j.get('slug')}.json`")
        details.append(f"- 原始响应片段：`fixtures/raw/{j.get('slug')}.txt`")
    lines.extend(details)
    lines.append("")
    lines.append("## 2. 候选替换记录")
    lines.append("")
    lines.append("- 原候选 计算机学报（cjc.ict.ac.cn）：HTTPS 被 reset，HTTP 当期页 404；官方站无稳定当期目录 HTML API → 替换为 计算机研究与发展（crd.ict.ac.cn / crad.ict.ac.cn Magtech 当期目录，真实 HTTP 200 且可解析）。")
    lines.append("- 原候选 电子学报（ejournal.org.cn）：首页 HTTP 200，但 `/zh/issue/2026/6/` 返回 6189 bytes 的 JS 壳页面，当期目录不可稳定解析 → 替换为 电子与信息学报（jeit.ac.cn/article/current，HTTP 200 且 40 条列表可解析）。")
    lines.append("- 原候选 中国科学:信息科学（SciEngine）：官网 SPA，未找到可验证的当期目录/摘要 JSON 映射 → 替换为 中文信息学报（jcip.cipsc.org.cn/cn/article/current，HTTP 200 且 Magtech 目录可解析）。")
    lines.append("- 原候选 JMLR：Crossref total=0，无法满足“每刊至少 5 篇最近一期” → 替换为 IEEE TKDE（1041-4347，Crossref 38(10) 可解析 15 篇）。")
    lines.append("- 原候选 IJCV：latest issue `134(10)` Crossref 同卷期不足 5 篇，需要跨卷期补足，不满足“该期”要求 → 替换为 IEEE TKDE；保留 TPAMI/TNNLS 等同卷期 ≥5 篇的刊。")
    lines.append("")
    lines.append("## 3. 备注")
    lines.append("")
    lines.append("- 国内刊不依赖 CNKI；主路径是各刊官网当期目录 adapter。")
    lines.append("- Crossref 首选、OpenAlex 补摘要；Elsevier 部分新文章 Crossref/OpenAlex 均无摘要，记录中 `text_source` 会标为 `title+keywords` 或 `title+abstract`，不静默伪造。")
    lines.append("- 抓取不到或某字段不可用时，`diagnostics`/`degradation_reasons` 在 JSON、Markdown、终端和日志中均有标注。")
    (ROOT / "docs" / "source-evidence.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote docs/source-evidence.md; raw snippets: {len(captured)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
